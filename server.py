from base64 import b64encode
import hashlib
import logging
import socket
from termcolor import colored
from socketserver import TCPServer, StreamRequestHandler

from log import create_logger

HOST, PORT = "localhost", 9999

class WebSocketServer(TCPServer):
    allow_reuse_address = True
    def __init__(self, address : tuple[str, int], handler : "WebSocketHandler"):
        super().__init__(address, handler)

class WebSocketHandler(StreamRequestHandler):
    def __init__(self, request : socket.socket, client_address : tuple[str, int], server : WebSocketServer):
        super().__init__(request, client_address, server)
    
    def setup(self):
        self.log = logging.getLogger("ws_server")
        super().setup()
        self.keep_alive = True
        self.handshake_done = False
        self.valid_client = False
    
    def handle(self):
        while self.keep_alive:
            if not self.handshake_done:
                self.handshake()
            elif self.valid_client:
                self.read_next_message()
                self.server.shutdown()
    
    def read_next_message(self):
        thing = self.read_bytes(2)
        self.log.debug(thing)

    def read_bytes(self, no_bytes : int):
        return self.rfile.read(2)

    def read_http_headers(self):
        headers = {}
        http_get = self.rfile.readline().decode().strip()
        if not http_get.startswith("GET"):
            raise Exception("Invalid HTTP request. Handshake doesn't start with GET")

        while True:
            header = self.rfile.readline().decode().strip()
            if not header:
                break
            key, value = header.split(":", 1)
            headers[key.lower().strip()] = value.strip()
        
        self.log.debug("Read HTTP headers")

        return headers

    @staticmethod
    def generate_handshake_response(websocket_key : str) -> str:
        server_handshake = \
            "HTTP/1.1 101 Switching Protocols\r\n"\
            "Upgrade: websocket\r\n"\
            "Connection: Upgrade\r\n"\
            f"Sec-WebSocket-Accept: {generate_response_key(websocket_key)}\r\n"\
            "Sec-WebSocket-Protocol: chat\r\n"\
            "\r\n"

        return server_handshake
    
    def handshake(self):
        self.log.info("Client connected. Starting handshake...")
        headers = self.read_http_headers()
        try:
            assert headers["upgrade"].lower() == "websocket"
        except KeyError:
            self.log.warning("Invalid HTTP request. Missing upgrade.")
            self.keep_alive = False
            return None
        except AssertionError:
            self.log.warning("Invalid HTTP request. Missing upgrade.")
            self.keep_alive = False
            return None
        
        self.log.info("Received valid HTTP request")
        self.log.info("Generating response")
        response = self.generate_handshake_response(headers["sec-websocket-key"])
        self.log.debug(response)
        self.wfile.write(response.encode())
        self.handshake_done = True
        self.valid_client = True

def generate_response_key(websocket_key : str) -> str:
    GUID = "258EAFA5-E914-47DA-95CA-C5AB0DC85B11"
    response_key = b64encode(hashlib.sha1(websocket_key.encode() + GUID.encode()).digest())
    return response_key.decode()

if __name__ == "__main__":
    create_logger("ws_server", logging.DEBUG)
    with WebSocketServer((HOST, PORT), WebSocketHandler) as server:
        try: 
            server.serve_forever()
        except KeyboardInterrupt:
            server.server_close()

