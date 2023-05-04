import socket
import sys
from hashlib import sha1
from base64 import b64encode

HOST, PORT = "localhost", 9999

sec_websocket_key = "dGhlIHNhbXBsZSBub25jZQ=="

client_handshake = \
    "GET /chat HTTP/1.1\r\n"\
    f"Host: {HOST}:{PORT}\r\n"\
    "Upgrade: websocket\r\n"\
    "Connection: Upgrade\r\n"\
    f"Sec-WebSocket-Key: {sec_websocket_key}\r\n"\
    f"Origin: http://{HOST}:{PORT}\r\n"\
    "Sec-WebSocket-Protocol: chat, superchat\r\n"\
    "Sec-WebSocket-Version: 13\r\n"\
    "\r\n"

def check_response_key(key : str):
    GUID = "258EAFA5-E914-47DA-95CA-C5AB0DC85B11"
    response_key = b64encode(sha1(sec_websocket_key.encode() + GUID.encode()).digest())
    return response_key == key.encode()

def check_server_handshake(received : str) -> bool:
    lines = received.split("\r\n")
    assert lines[0] == "HTTP/1.1 101 Switching Protocols"
    headers = {}
    for line in lines[1:]:
        if line:
            key, value = line.split(":", 1)
            headers[key.lower().strip()] = value.strip()
    
    assert headers["upgrade"] == "websocket"
    assert headers["connection"] == "Upgrade"
    assert check_response_key(headers["sec-websocket-accept"])


with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
    sock.connect((HOST, PORT))
    sock.sendall(client_handshake.encode())
    received = sock.recv(1024).decode()
    check_server_handshake(received)

