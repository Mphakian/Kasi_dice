import socket
import sys

class Client:
    def __init__(self):
        self.localhost = socket.gethostbyname_ex(socket.gethostname())[-1][0]
        self.remote_host = self.localhost
        self.port = 8888
        self.bufsize = 256
        self.data = b''
        self.connected = False
        self.address = (self.remote_host, self.port)
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def connect(self):
        try:
            self.client.connect(self.address)

            while not self.connected:
                data = self.client.recv(self.bufsize)
                status = data.decode()
                if status == "ok":
                    print(f"Connected to server @ {self.address}")
                    self.connected = True
                elif status == "wait":
                    print(f"Waiting for an opponent to join...")
                    self.connected = False
                elif status == "refused":
                    print(f"Connection refused - server is full...")
                    sys.exit()

        except Exception as e:
            self.connected = False
            print(f"Error connecting to server - {e}")
            sys.exit()

    def send(self, message):
        try:
            data = message.encode("utf-8")
            self.client.sendall(data)
            response = self.client.recv(self.bufsize)
            if response:
                return response.decode("utf-8")
            else:
                print(f"Server stopped responding...")
                sys.exit()

        except:
            print("Your opponent left the game...")
            sys.exit()
