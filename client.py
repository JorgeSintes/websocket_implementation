from base64 import b64encode
import logging
from secrets import token_bytes
import socket

from log import create_logger
from server import generate_response_key

HOST, PORT = "localhost", 9999

def generate_random_key() -> str:
    return b64encode(token_bytes(16)).decode()

class WebSocketMessage:
    def __init__(self, message : str):
        self.message = message.encode("utf-8")

    def build_frame(self):
        ...

class WebSocketClient:
    def __init__(self, log : logging.Logger, address : tuple[str, int]):
        self.log = log
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.address = address
        self.sec_websocket_key = generate_random_key()

    def _check_response_key(self, key : str):
        response_key = generate_response_key(self.sec_websocket_key)
        return response_key == key

    def _check_server_handshake(self, received : str) -> bool:
        lines = received.split("\r\n")
        assert lines[0] == "HTTP/1.1 101 Switching Protocols"
        headers = {}
        for line in lines[1:]:
            if line:
                key, value = line.split(":", 1)
                headers[key.lower().strip()] = value.strip()
        
        assert headers["upgrade"] == "websocket"
        assert headers["connection"] == "Upgrade"
        assert self._check_response_key(headers["sec-websocket-accept"])
    
    def connect(self):
        self.log.info("Attempting to connect.")
        client_handshake = \
            "GET /chat HTTP/1.1\r\n"\
            f"Host: {self.address[0]}:{self.address[1]}\r\n"\
            "Upgrade: websocket\r\n"\
            "Connection: Upgrade\r\n"\
            f"Sec-WebSocket-Key: {self.sec_websocket_key}\r\n"\
            f"Origin: http://{self.address[0]}:{self.address[1]}\r\n"\
            "Sec-WebSocket-Protocol: chat, superchat\r\n"\
            "Sec-WebSocket-Version: 13\r\n"\
            "\r\n"

        self.socket.connect((HOST, PORT))
        self.socket.sendall(client_handshake.encode())
        received = self.socket.recv(1024).decode()
        self._check_server_handshake(received)

        self.log.info("Connection established!")

    def close(self):
        self.socket.close()


if __name__ == "__main__":
    log = create_logger("ws_client", logging.DEBUG)
    ws_client = WebSocketClient(log, (HOST, PORT))
    ws_client.connect()
