#  coding: utf-8 
import socketserver
import signal
import sys
import os

# Copyright 2019 Carlo Oliva
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

# --------- Globally Defined Variables ---------- #

OK = "HTTP/1.1 200 OK\n"
ERROR404 = "HTTP/1.1 404 Not Found\n"
ERROR405 = "HTTP/1.1 405 Method Not Found\n"
HTML = "Content-Type: text/html\r\n\r\n"
CSS = "Content-Type: text/css\r\n\r\n"


# ----------------- Classes --------------------- #

class MyWebServer(socketserver.BaseRequestHandler):

    def handle(self):
        start_os = os.path.abspath("www/")  # Used to find CSS files from the www/ directory
        self.data = self.request.recv(1024).strip().decode("utf-8")
        # print(self.data.split("\r\n")[0])
        if self.data.startswith('GET'):
            print(self.data.split("\r\n")[0])
            # print(self.data.split("\r\n"))
            url_file, error = decompose_request(self.data)
            if error:
                self.request.sendall(bytearray(ERROR404, 'utf-8'))
                pass
            try:
                open(url_file)
            except FileNotFoundError:
                print("File not found")
                self.request.sendall(bytearray(ERROR404, 'utf-8'))
            if url_file.endswith("index.html"):
                sendall_html = generate_sendall(url_file, 'html')
                self.request.sendall(bytearray(sendall_html, 'utf-8'))
            if url_file.endswith('.css'):
                sendall_css = generate_sendall(url_file, 'css')
                self.request.sendall(bytearray(sendall_css, 'utf-8'))
        else:
            # Return status code 405 Method not allowed for (POST/PUT/DELETE)
            self.request.sendall(bytearray(ERROR405, 'utf-8'))


# ------------ User Defined Functions ------------#

def decompose_request(data):
    """
    Takes the url of the get request and parse through it to generate the correct file path.
    :param data: the url
    :return: file path
    """
    start_os = os.path.abspath("www/")  # Used to find CSS files from the www/ directory
    url = data.split("\r\n")[0].split(" ")[1]
    prefix = 'www'
    delimiter = '/'
    spl = url.split("/")
    length = len(spl)
    print(spl)
    print(length)
    if spl[length - 1] == "":
        spl[length - 1] = "index.html"
    elif not spl[length - 1].endswith(".html") and not spl[length - 1].endswith(".css"):
        spl.append("index.html")
    elif spl[length - 1].endswith(".css"):  # Find the CSS file, assuming that each CSS file is uniquely named.
        abs_path = find(spl[length - 1], start_os)
        abs_file = abs_path.split('www/')
        print(abs_file[1])
        if str(abs_file[1]).count('/') != length:
         return prefix + delimiter + str(abs_file[1]), True
        else:
            return prefix + delimiter + str(abs_file[1]), False

    return prefix + delimiter.join(spl), False


def find(name, path):
    """
    Finds a file based on the directory given as well as the file name. Returns the path.

    Taken from: https://stackoverflow.com/questions/1724693/find-a-file-in-python on January 15/19
    Author: https://stackoverflow.com/users/97828/nadia-alramli
    :param name: the file name
    :param path: path
    :return: file path
    """
    for root, dirs, files in os.walk(path):
        if name in files:
            return os.path.join(root, name)


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
        sendall = OK + CSS
    with open(file, 'r', encoding='utf-8') as infile:
        for line in infile:
            sendall += line
    return sendall


def signal_handler(sig, frame):
    """
    Checks if control+c is pressed to stop the web server for a more graceful exit than displaying the exception
    messages.

    Taken from https://stackoverflow.com/questions/1112343/how-do-i-capture-sigint-in-python on January 14/19
    Author: https://stackoverflow.com/users/18528/matt-j
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
