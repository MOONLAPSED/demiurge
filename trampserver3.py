import socket
import logging
import collections
import time
from dataclasses import dataclass, field

# Setting up a logger
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(message)s")
logger = logging.getLogger(__name__)

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

# Server socket creation
def listening_socket(host, port):
    sock = socket.socket(socket.AF_INET6, socket.SOCK_STREAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.setsockopt(socket.IPPROTO_IPV6, socket.IPV6_V6ONLY, 0)
    sock.bind((host, port, 0, 0))
    sock.listen(5)
    sock.setblocking(False)
    return SocketWrapper(sock)

# Connection handler for echo
def echo_handler(sock):
    logger.info(f"New connection: {sock}")
    while True:
        try:
            data = sock.recv(8192)
            if data:
                logger.info(f"Received: {data.decode('utf-8')}")
                sock.send(data)  # Echo back the data
            else:
                break  # Connection closed by client
        except Exception as e:
            logger.error(f"Error: {e}")
            break
    sock.sock.close()
    logger.info(f"Connection closed: {sock}")

# Main server loop
def server():
    server_socket = listening_socket("localhost", 8869)
    logger.info("Server started on port 8869")
    
    while True:
        try:
            client_socket, _ = server_socket.accept()
            echo_handler(client_socket)
        except Exception as e:
            logger.error(f"Server error: {e}")
            time.sleep(0.1)

if __name__ == "__main__":
    server()
