from socketserver import TCPServer, BaseRequestHandler

class MyTCPHandler(BaseRequestHandler):
    def handle(self):
        self.data = self.request.recv(1024).strip()
        print(f"{self.client_address} wrote: {self.data}")
        self.request.sendall(self.data.upper())


if __name__ == "__main__":
    HOST, PORT = "localhost", 9999
    with TCPServer((HOST, PORT), MyTCPHandler) as server:
        server.serve_forever()
