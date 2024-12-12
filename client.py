import socket
import json
from dataclasses import dataclass

@dataclass
class Response():
    msg: str
    addr: str = ""
    status: str = ""
    content: json = None
    
    def __post_init__(self):
        self.addr = self.msg[:5]
        self.status = self.msg[5:7]
        self.content = json.loads(self.msg[7:])

@dataclass
class Request():
    addr: str
    content: json
    msg: bytes = b''

    def __post_init__(self):
        content_string = json.dumps(self.content)
        length = len(self.addr + content_string)
        self.msg = f'{length:05}{self.addr}{content_string}'.encode()

@dataclass
class Client:
    sock: socket.socket = None

    def __post_init__(self):
        if self.sock is None:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        bus_address = ('localhost', 5000)
        print('connecting to {} port {}'.format(*bus_address))
        try:
            self.sock.connect(bus_address)
        except socket.error as e:
            print(f'socket error during initialization: {e}')
            self.sock = None

    
    def receive(self):
        if self.sock is None:
            raise ValueError("Socket is not initialized.")
    
        amount_received = 0
        try:
            amount_expected = int(self.sock.recv(5))
            content = b""
            while amount_received < amount_expected:
                chunk = self.sock.recv(amount_expected - amount_received)
                if not chunk:
                    break
                content += chunk
                amount_received += len(chunk)

            print(f"Mensaje recibido (raw): {content}")  # Depuración del mensaje recibido

            # Validar y decodificar
            try:
                msg = Response(content.decode(encoding="utf-8"))
                return msg
            except json.JSONDecodeError as e:
                print(f"Error al decodificar JSON: {e}")
                print(f"Contenido bruto problemático: {content.decode(encoding='utf-8', errors='replace')}")
                raise
        except socket.error as e:
            print(f"Socket error durante la recepción: {e}")
            self.sock = None
            return None
    
    def send(self, request: Request):
        if self.sock is None:
            raise ValueError("Socket is not initialized.")
        
        try:
            self.sock.sendall(request.msg)
        except socket.error as e:
            print(f'socket error during send: {e}')
            self.sock = None

    def close(self):
        if self.sock:
            print('closing socket')
            self.sock.close()
            self.sock = None
    
    