import json
from http.server import BaseHTTPRequestHandler, HTTPServer
import time
import random
import logging
import logging.handlers
import os


def get_env_var(name):
    return os.environ.get(name)


ENV = get_env_var('ENV')
POD_NAME = get_env_var('POD_NAME')
POD_NS = get_env_var('POD_NAMESPACE')
POD_IP = get_env_var('POD_IP')

"""
LOGGING CONSTANTS
"""
_log_directory = '/logs/echo/'
_log_filename = 'echo.log'
log_path = os.path.join(_log_directory, _log_filename)

# Check if the directory exists, and if not, create it
if not os.path.exists(_log_directory) and ENV is not None:
    os.makedirs(_log_directory)

LOG = logging.getLogger(__name__)
LOG.setLevel(logging.INFO)

if ENV is not None:
    fh = logging.handlers.RotatingFileHandler(log_path, maxBytes=1024 * 1024 * 5, backupCount=5)  # 5 MB per file, 5 files max
    fh.setLevel(logging.INFO)

    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s')
    fh.setFormatter(formatter)
    LOG.addHandler(fh)



class EchoHandler(BaseHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        self.id = random.randint(1, 10000)
        LOG.info(f"[{self.id}] New connection established...")
        super().__init__(*args, **kwargs)

    def handle(self):
        # Record that handling of the request has started
        LOG.info(f"[{self.id}] Start of request received...")
        super().handle()

    def handle_request(self):
        # Timestamp when headers are fully received
        self.headers_received_time = time.time()
        LOG.info(f"[{self.id}] Headers received...")

        # Read the body if any
        content_length = self.headers.get('Content-Length')
        post_data = None
        if content_length:
            content_length = int(content_length)
            post_data = self.rfile.read(content_length).decode('utf-8')
            body_received_time = time.time()
            LOG.info(f"[{self.id}] Body received")

        # Prepare response data
        response_data = {
            'env': ENV,
            'pod': {
                'ns': POD_NS,
                'name': POD_NAME,
                'ip': POD_IP
            },
            'method': self.command,
            'path': self.path,
            'headers': dict(self.headers),
            'body': post_data
        }

        # Send response
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps(response_data, indent=2).encode('utf-8'))

        # Timestamp when response is sent
        self.response_sent_time = time.time()
        LOG.info(f"[{self.id}] Response sent")

    def do_GET(self):
        self.handle_request()

    def do_POST(self):
        self.handle_request()

    def do_PUT(self):
        self.handle_request()

    def do_DELETE(self):
        self.handle_request()

    def do_HEAD(self):
        self.handle_request()


def run(server_class=HTTPServer, handler_class=EchoHandler, port=8080):
    server_address = ('', port)
    httpd = server_class(server_address, handler_class)
    LOG.info(f'Starting httpd server on port {port}...')
    httpd.serve_forever()


if __name__ == '__main__':
    run()
