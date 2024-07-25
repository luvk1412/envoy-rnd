from http.server import BaseHTTPRequestHandler, HTTPServer
import json
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
_log_directory = '/logs/auth/'
_log_filename = 'auth.log'
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

class SimpleAuthHandler(BaseHTTPRequestHandler):

    def do_GET(self):
        self._handle_request()

    def do_POST(self):
        self._handle_request()

    def _handle_request(self):
        LOG.info(f"Method: {self.command} Headers received: {dict(self.headers)}")
        session_token = self.headers.get('X-Session-Token')
        LOG.info(f"Session header: {session_token}, path: {self.path}")
        response_body = {}
        response_code = 200
        response_headers = {
            'Content-type': 'application/json',
        }
        x_session_resp = 'empty'

        if session_token:
            if session_token == "send_error":
                response_body = {
                    "error": "Unauthorized",
                    "message": "Invalid session token"
                }
                response_code = 403
                x_session_resp = 'auth failed v2'
            else:
                x_session_resp = f'auth of {session_token} success'
        else:
            x_session_resp = 'auth failed'

        response_headers['X-Session-Resp'] = x_session_resp
        self.send_response(response_code)
        for key, value in response_headers.items():
            self.send_header(key, value)
        self.end_headers()
        self.wfile.write(json.dumps(response_body, indent=2).encode('utf-8'))
        LOG.info(f"Auth resp sent. status: {response_code}, header: {response_headers}, body: {response_body}")

def run(server_class=HTTPServer, handler_class=SimpleAuthHandler, port=8080):
    server_address = ('', port)
    httpd = server_class(server_address, handler_class)
    LOG.info(f'Starting httpd server on port {port}')
    httpd.serve_forever()

if __name__ == '__main__':
    run()
