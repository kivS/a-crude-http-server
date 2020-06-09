import os
import socket
import mimetypes
from http import HTTPStatus
from typing import Dict

HTTP_VERSION = '2.0'


class TCPServer:

    def __init__(self, host='127.0.0.1', port=8888):
        self.host = host
        self.port = port

    def start(self):

        # create a IPv4 socket of the TCP type
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s. setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        # bind the sockets to the address + port
        s.bind((self.host, self.port))

        # start listening for connections with a max of 5 before being recycled
        s.listen(5)

        print(f'Listening at: { s.getsockname() }')

        while True:
            # accept new connection
            conn, addr = s.accept()

            print(f'Connected by: {addr}')

            # read the data sent by the client(1024 bytes)
            data: bytes = conn.recv(1024)

            response = self.handle_request(data)

            # send reponse to the client
            conn.sendall(response)
            conn.close()

    def handle_request(self, data: bytes):
        return data


class HTTPRequest:
    '''
        Representation of an HTTP request coming from client
    '''

    def __init__(self, data: bytes):
        self.method = None
        self.uri = None
        self.http_version = HTTP_VERSION
        self.headers = {}

        # call self.parse method to parse the request data
        self.parse(data)

    def parse(self, data):
        lines = data.split(b'\r\n')

        request_line = lines[0]
        self.parse_request_line(request_line)

    def parse_request_line(self, request_line):
        '''
            Parse the first line of the request
        '''
        words = request_line.split(b' ')
        self.method = words[0]
        self.uri = words[1]

        if len(words) > 2:
            self.http_version = words[2]


class HTTPResponse:
    '''
        Representation of an HTTP response returned by server
    '''

    BASE_HEADERS = {
        'Server': 'Flying Potato'
    }

    BLANK_LINE = '\r\n'

    def __init__(
        self,
        status_code: int,
        headers: Dict = {},
        http_version: str = HTTP_VERSION,
        body: bytes = b''
    ):

        self.headers = headers
        self.status_code = status_code
        self.http_version = http_version
        self.body = body

    def response_line(self):
        '''
            Build the first line of the response
        '''

        # get the http reason out of the http status code integer
        http_reason = HTTPStatus(self.status_code).name

        return f'HTTP/{self.http_version} {self.status_code} {http_reason}\r\n'

    def response_headers(self) -> str:
        '''
            Build the final headers using the base headers as 'seed'
        '''

        headers = self.BASE_HEADERS.copy()

        headers.update(self.headers)

        # build header string
        header_output = ''
        for header, value in headers.items():
            header_output += f'{header}: {value}\r\n'

        return header_output

    def serialize(self) -> bytes:
        '''
            Return a serialized response
        '''

        data = (
            # response line
            self.response_line(),
            # Headers
            self.response_headers(),
            # CRLF
            self.BLANK_LINE,
        )

        data = bytes(''.join(data), 'utf-8')

        return data + self.body


class HTTPServer(TCPServer):

    def handle_request(self, data: bytes):

        # parse the request
        request = HTTPRequest(data)

        # select which handler to call based on the HTTP method
        try:
            handler = getattr(self, f'handle_{request.method.decode()}')
            response = handler(request)
        except AttributeError:
            return HTTPResponse(
                status_code=501,
                body=b'<h1>501 Not Implemented</h1>',
            ).serialize()
        else:
            return response

    def handle_OPTIONS(self, request: HTTPRequest):
        '''
            Handle OPTIONS HTTP requests
        '''

        response = HTTPResponse(
            status_code=200,
            headers={'Allow': 'OPTIONS, GET'}
        )
        return response.serialize()

    def handle_GET(self, request: HTTPRequest):
        '''
            Handle GET HTTP requests
        '''

        filename = request.uri.strip(b'/')

        if os.path.exists(filename):

            with open(filename, 'rb') as file:
                body = file.read()

            # let's guess the file type in order for it to render properly on the browser, eg: image file
            content_type = mimetypes.guess_type(filename.decode())[0] or 'text/html'

            response = HTTPResponse(
                status_code=200,
                headers={'Content-Type': content_type},
                body=body
            )
            return response.serialize()

        else:
            return HTTPResponse(
                status_code=404,
                body=b'<h1> 404 Not Found </h1>'
            ).serialize()


if __name__ == '__main__':
    # server = TCPServer()
    server = HTTPServer()
    server.start()
