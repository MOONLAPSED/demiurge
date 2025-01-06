import collections
import sys
import socket
import types
import select
import time

class SocketWrapper:
    def __init__(self, sock):
        if not sock:
            raise ValueError("Socket cannot be None")
        self.sock = sock
    
    def fileno(self):
        return self.sock.fileno()
    
    def send(self, data):
        return self.sock.send(data)
    
    def recv(self, size):
        return self.sock.recv(size)
    
    def accept(self):
        client, addr = self.sock.accept()
        return SocketWrapper(client), addr

def nonblocking_read(sock, chunk_size=8192):
    if not isinstance(sock, SocketWrapper):
        sock = SocketWrapper(sock)
    while True:
        try:
            ready = select.select([sock], [], [], 0.1)[0]
            if ready:
                data = sock.recv(chunk_size)
                if not data:
                    raise ConnectionLost()
                return data
            yield None
        except socket.error:
            raise ConnectionLost()

def nonblocking_write(sock, data):
    if not isinstance(sock, SocketWrapper):
        sock = SocketWrapper(sock)
    while data:
        try:
            ready = select.select([], [sock], [], 0.1)[1]
            if ready:
                sent = sock.send(data)
                data = data[sent:]
            yield None
        except socket.error:
            raise ConnectionLost()

def nonblocking_accept(sock):
    if not isinstance(sock, SocketWrapper):
        sock = SocketWrapper(sock)
    while True:
        try:
            ready = select.select([sock], [], [], 0.1)[0]
            if ready:
                client_sock, addr = sock.accept()
                yield client_sock
                return  # Properly terminate the generator
            yield None
        except socket.error:
            raise ConnectionLost()

def listening_socket(host, port):
    # Create dual-stack socket that works for both IPv4 and IPv6
    sock = socket.socket(socket.AF_INET6, socket.SOCK_STREAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    # Enable dual-stack socket
    sock.setsockopt(socket.IPPROTO_IPV6, socket.IPV6_V6ONLY, 0)
    sock.bind((host, port, 0, 0))  # The zeros are for flow info and scope id
    sock.listen(5)
    sock.setblocking(False)
    return SocketWrapper(sock)

class ConnectionLost(Exception):
    pass

class Trampoline:
    """Manage communications between coroutines"""

    running = False

    def __init__(self):
        self.queue = collections.deque()

    def add(self, coroutine):
        """Request that a coroutine be executed"""
        self.schedule(coroutine)

    def run(self):
        result = None
        self.running = True
        try:
            while self.running:  # Remove the 'and self.queue' condition
                if self.queue:
                    func = self.queue.popleft()
                    result = func()
                else:
                    # Small sleep to prevent CPU spinning
                    time.sleep(0.01)
            return result
        finally:
            self.running = False

    def stop(self):
        self.running = False

    def schedule(self, coroutine, stack=(), val=None, *exc):
        def resume():
            value = val
            try:
                if exc:
                    value = coroutine.throw(value,*exc)
                else:
                    value = coroutine.send(value)
            except:
                if stack:
                    # send the error back to the "caller"
                    self.schedule(
                        stack[0], stack[1], *sys.exc_info()
                    )
                else:
                    # Nothing left in this pseudothread to
                    # handle it, let it propagate to the
                    # run loop
                    raise

            if isinstance(value, types.GeneratorType):
                # Yielded to a specific coroutine, push the
                # current one on the stack, and call the new
                # one with no args
                self.schedule(value, (coroutine,stack))

            elif stack:
                # Yielded a result, pop the stack and send the
                # value to the caller
                self.schedule(stack[0], stack[1], value)

            # else: this pseudothread has ended

        self.queue.append(resume)

def echo_handler(sock):
    """ Handle incoming connections and echo data. """
    if sock is None:
        raise ValueError("Socket must be initialized")
    
    wrapped_sock = SocketWrapper(sock)
    print("Handler started for a new client.")
    
    while True:
        try:
            data = yield nonblocking_read(wrapped_sock)
            print(f"Received data: {data.decode('utf-8')}")
            # Echo back the received data
            yield nonblocking_write(wrapped_sock, data)
            print(f"Echoed back: {data.decode('utf-8')}")
        except ConnectionLost:
            print("Connection lost.")
            break

def listen_on(trampoline, sock, handler):
    """ Listen for incoming connections and assign handlers. """
    if sock is None:
        raise ValueError("Listening socket must be initialized")
    wrapped_sock = SocketWrapper(sock)
    
    while True:
        try:
            client_sock = yield from nonblocking_accept(wrapped_sock)
            if client_sock:
                print("New connection accepted.")
                handler_coro = handler(client_sock)
                trampoline.add(handler_coro)
        except ConnectionLost:
            print("Connection lost while accepting.")
            break

try:
    # Create a scheduler to manage all our coroutines
    t = Trampoline()

    # Initialize server socket with explicit validation
    server_socket = listening_socket("localhost", 8869)
    if not server_socket:
        raise ValueError("Failed to create server socket")

    # Create server coroutine with validated socket
    server = listen_on(t, server_socket, echo_handler)

    # Add the coroutine to the scheduler
    t.add(server)

    # Run the event loop
    t.run()
except KeyboardInterrupt:
    print("\nShutting down server...")
except Exception as e:
    print(f"Error: {e}")
finally:
    if 'server_socket' in locals():
        server_socket.sock.close()
