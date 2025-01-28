import argparse
from pathlib import Path
import socket
import sys
import subprocess
import site
import os
import http.server
import json
import logging

WINDOWS_SANDBOX_DEFAULT_DESKTOP = Path(r'C:\Users\WDAGUtilityAccount\Desktop')

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger('SandboxHTTPServer')

def enable_python_incoming_firewall():
    """Enable firewall rule for incoming connections to Python executable."""
    # Using `{sys.base_exec_prefix}\python.exe` instead of `sys.executable` to support venvs.
    for python_executable in ['python.exe', 'python3.exe']:
        subprocess.run(
            f'netsh advfirewall firewall add rule name="AllowPythonServer" '
            f'dir=in action=allow enable=yes program="{Path(sys.base_exec_prefix) / python_executable}"',
            check=True,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )
    logger.info("Firewall rule added for Python server.")

def get_ip_address():
    """Get the current IP address of the sandbox."""
    hostname = socket.gethostname()
    return socket.gethostbyname(hostname)

class SandboxRequestHandler(http.server.BaseHTTPRequestHandler):
    """HTTP request handler for receiving data from the host."""
    
    def do_POST(self):
        try:
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            data = json.loads(post_data)
            logger.info(f"Received data from host: {data}")
            response = {'status': 'success', 'message': 'Data received by sandbox'}
            self._send_response(response)
        except json.JSONDecodeError:
            logger.error("Failed to decode JSON from host.")
            self._send_response({'status': 'error', 'message': 'Invalid JSON'})
    
    def _send_response(self, data):
        """Send JSON response back to the client."""
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(json.dumps(data).encode('utf-8'))

    def log_message(self, format, *args):
        """Override default logging to integrate with custom logger."""
        logger.info("%s - - [%s] %s" % (self.client_address[0], self.log_date_time_string(), format % args))

def run_server(port):
    """Run the HTTP server in the sandbox."""
    server_address = ('', port)
    httpd = http.server.HTTPServer(server_address, SandboxRequestHandler)
    logger.info(f"Starting HTTP server on port {port}")
    httpd.serve_forever()

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Start the Sandbox HTTP Server")
    parser.add_argument('--port', type=int, default=8000, help="Port number for HTTP server")
    args = parser.parse_args()

    # Enable firewall rules to allow incoming connections
    enable_python_incoming_firewall()
    
    # Start server
    run_server(args.port)