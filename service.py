import os
import socket
import json
from dataclasses import dataclass

@dataclass
class Request():
    msg: str
    addr: str = ""
    content: str = ""

    def __post_init__(self):
        self.addr = self.msg[:5]
        self.content = json.loads(self.msg[5:])

@dataclass
class Response():
    addr: str
    content: json
    msg: bytes = b''

    def __post_init__(self):
        content_string = json.dumps(self.content)
        length = len(self.addr + content_string)
        self.msg = f'{length:05}{self.addr}{content_string}'.encode()

@dataclass
class Service:
    name: str
    sock: socket.socket = None
    init: bool = False

    def sinit(self):
        if self.sock is None:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        host = os.getenv('HOST', 'localhost')
        server_address = (host, 5000)
        print('starting up on {} port {}'.format(*server_address))
        try:
            self.sock.connect(server_address)
            length = len('sinit' + self.name)
            rs = f'{length:05}sinit{self.name}'.encode()
            print(f'sending: {rs}')
            self.sock.sendall(rs)
            print ("Waiting for transaction")
            amount_received = 0
            amount_expected = int(self.sock.recv(5))
            while amount_received < amount_expected:
                content = self.sock.recv(amount_expected - amount_received)
                amount_received += len (content)
                print('received {!r}'.format(content))
            request = content.decode(encoding="utf-8")
            if len(request) == 12 and request[5:7] == "OK":
                print("Service initialized")
                self.init = True
            else:
                print("Service initialization failed")
                self.sock = None
        except socket.error as e:
            print(f'socket error during initialization: {e}')
            self.sock = None

    def receive(self):
        if self.sock is None:
            raise ValueError("Socket is not initialized.")
        
        print ("Waiting for transaction")
        amount_received = 0
        try:
            amount_expected = int(self.sock.recv(5))
            while amount_received < amount_expected:
                content = self.sock.recv(amount_expected - amount_received)
                amount_received += len (content)
                print('received {!r}'.format(content))
            request = Request(msg=content.decode(encoding="utf-8"))
            return request
        except socket.error as e:
            print(f'socket error during receive: {e}')
            self.sock = None
            return ""
    
    def send(self, response: Response):
        if self.sock is None:
            raise ValueError("Socket is not initialized.")
        
        print('sending {!r}'.format(response.msg))
        try:
            self.sock.sendall(response.msg)
        except socket.error as e:
            print(f'socket error during send: {e}')
            self.sock = None

    def close(self):
        if self.sock:
            print('closing socket')
            self.sock.close()
            self.sock = None