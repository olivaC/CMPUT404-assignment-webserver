#  coding: utf-8 
import socketserver
import signal
import sys

# Copyright 2013 Abram Hindle, Eddie Antonio Santos
# 
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
# 
#     http://www.apache.org/licenses/LICENSE-2.0
# 
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
#
# Furthermore it is derived from the Python documentation examples thus
# some of the code is Copyright © 2001-2013 Python Software
# Foundation; All Rights Reserved
#
# http://docs.python.org/2/library/socketserver.html
#
# run: python freetests.py

# try: curl -v -X GET http://127.0.0.1:8080/

# --------- Globally Defined Variables ---------- #

OK = "HTTP/1.1 200 OK\n"
ERROR = "HTTP/1.1 404 Not Found\n"
HTML = "Content-type: text/html\r\n\r\n"
CSS = "Content-type: text/css\r\n\r\n"


# ----------------- Classes --------------------- #

class MyWebServer(socketserver.BaseRequestHandler):

    def handle(self):
        self.data = self.request.recv(1024).strip().decode("utf-8")
        print(self.data)
        if self.data.startswith('GET'):
            print(self.data)
            url = decompose_request(self.data)
            if url in ('/', '/index.html'):
                sendall = generate_sendall('www/index.html', 'html')
                self.request.sendall(bytearray(sendall, 'utf-8'))
            elif url in ('/deep/', '/deep', '/deep/index.html'):
                sendall = generate_sendall('www/deep/index.html', 'html')
                self.request.sendall(bytearray(sendall, 'utf-8'))
            else:
                self.request.sendall(bytearray(ERROR, 'utf-8'))


# ------------ User Defined Functions ------------#

def decompose_request(data):
    url = data.split("\r\n")[0].split(" ")[1]
    print("url is: " + url)
    return url


def generate_sendall(file, req_type):
    """
    Adds the correct heading to the HTML/CSS files found in the www folder
    :param file: the html/css file to be opened and read
    :param req_type: either html or css
    :return: A complete string including the correct headings
    """
    if req_type == 'html':
        sendall = OK + HTML
    else:
        sendall = OK + HTML
    with open(file, 'r', encoding='utf-8') as infile:
        for line in infile:
            sendall += line
    return sendall


def signal_handler(sig, frame):
    """
    Taken from https://stackoverflow.com/questions/1112343/how-do-i-capture-sigint-in-python on January 14/19
    Author: https://stackoverflow.com/users/18528/matt-j

    Checks if control+c is pressed to stop the web server for a more graceful exit than displaying the exception
    messages.
    :param sig:
    :param frame:
    :return: None
    """
    print('\nStopping server!')
    sys.exit(0)


if __name__ == "__main__":
    HOST, PORT = "localhost", 8080

    socketserver.TCPServer.allow_reuse_address = True
    # Create the server, binding to localhost on port 8080
    server = socketserver.TCPServer((HOST, PORT), MyWebServer)

    # Print starting state
    print("Server started on http://127.0.0.1:8080/")
    print("To exit press Ctrl-c")
    signal.signal(signal.SIGINT, signal_handler)

    # Activate the server; this will keep running until you
    # interrupt the program with Ctrl-C
    server.serve_forever()

    signal.pause()
