#------------------------------------------------------------------------------
# Standard Library Imports - 3.13 std libs ONLY
#------------------------------------------------------------------------------
import collections
import dataclasses
import socket
import select
import sys
import types
import time
from typing import Generator, Any

#------------------------------------------------------------------------------
# Dataclasses for Socket Handling
#------------------------------------------------------------------------------
@dataclasses.dataclass(frozen=True)
class SocketWrapper:
    sock: socket.socket

    def fileno(self) -> int:
        return self.sock.fileno()

    def send(self, data: bytes) -> int:
        return self.sock.send(data)

    def recv(self, size: int) -> bytes:
        return self.sock.recv(size)

    def accept(self) -> tuple["SocketWrapper", tuple]:
        client, addr = self.sock.accept()
        return SocketWrapper(client), addr

#------------------------------------------------------------------------------
# Nonblocking Socket Operations
#------------------------------------------------------------------------------
def nonblocking_read(sock: SocketWrapper, chunk_size: int = 8192) -> Generator[None, None, bytes]:
    while True:
        ready = select.select([sock.sock], [], [], 0.1)[0]
        if ready:
            data = sock.recv(chunk_size)
            if not data:
                raise ConnectionLost("Client disconnected.")
            return data
        yield None

def nonblocking_write(sock: SocketWrapper, data: bytes) -> Generator[None, None, None]:
    while data:
        ready = select.select([], [sock.sock], [], 0.1)[1]
        if ready:
            sent = sock.send(data)
            data = data[sent:]
        yield None

def nonblocking_accept(sock: SocketWrapper) -> Generator[None, None, tuple]:
    while True:
        ready = select.select([sock.sock], [], [], 0.1)[0]
        if ready:
            client_sock, addr = sock.accept()
            yield client_sock
            return
        yield None

#------------------------------------------------------------------------------
# Listening Socket Factory
#------------------------------------------------------------------------------
def listening_socket(host: str, port: int) -> SocketWrapper:
    sock = socket.socket(socket.AF_INET6, socket.SOCK_STREAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.setsockopt(socket.IPPROTO_IPV6, socket.IPV6_V6ONLY, 0)
    sock.bind((host, port, 0, 0))
    sock.listen(5)
    sock.setblocking(False)
    return SocketWrapper(sock)

#------------------------------------------------------------------------------
# Custom Exception
#------------------------------------------------------------------------------
class ConnectionLost(Exception):
    """Raised when a connection is unexpectedly lost."""

#------------------------------------------------------------------------------
# Trampoline Scheduler
#------------------------------------------------------------------------------
class Trampoline:
    def __init__(self):
        self.queue = collections.deque()
        self.running = False

    def add(self, coroutine: Generator):
        self.schedule(coroutine)

    def schedule(self, coroutine: Generator, stack=(), val=None, *exc):
        def resume():
            try:
                value = val
                if exc:
                    value = coroutine.throw(*exc)
                else:
                    value = coroutine.send(value)
            except StopIteration:
                if stack:
                    self.schedule(stack[0], stack[1], *sys.exc_info())
                else:
                    raise
            else:
                if isinstance(value, types.GeneratorType):
                    self.schedule(value, (coroutine, stack))
                elif stack:
                    self.schedule(stack[0], stack[1], value)

        self.queue.append(resume)

    def run(self):
        self.running = True
        try:
            while self.running:
                if self.queue:
                    task = self.queue.popleft()
                    task()
                else:
                    time.sleep(0.01)
        finally:
            self.running = False

    def stop(self):
        self.running = False

#------------------------------------------------------------------------------
# Echo Handler Coroutine
#------------------------------------------------------------------------------
def echo_handler(sock: SocketWrapper) -> Generator:
    try:
        while True:
            data = yield from nonblocking_read(sock)
            yield from nonblocking_write(sock, data)
    except ConnectionLost:
        pass

#------------------------------------------------------------------------------
# Listen Coroutine
#------------------------------------------------------------------------------
def listen_on(trampoline: Trampoline, sock: SocketWrapper, handler) -> Generator:
    try:
        while True:
            client_sock = yield from nonblocking_accept(sock)
            trampoline.add(handler(client_sock))
    except ConnectionLost:
        pass

#------------------------------------------------------------------------------
# Main Execution
#------------------------------------------------------------------------------
if __name__ == "__main__":
    try:
        # Initialize trampoline and listening socket
        t = Trampoline()
        server_socket = listening_socket("::1", 8888)
        print("Server started on port 8888. Press Ctrl+C to stop.")

        # Add server coroutine to trampoline
        t.add(listen_on(t, server_socket, echo_handler))

        # Run trampoline event loop
        t.run()
    except KeyboardInterrupt:
        print("\nServer shutting down...")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        if 'server_socket' in locals():
            server_socket.sock.close()
