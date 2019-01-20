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

"""
Status codes taken from https://www.w3.org/Protocols/rfc2616/rfc2616-sec10.html

Carriage Return and New Line taken from class notes
    CMPUT 404 Abram Hindle January 18, 2019
"""

OK = "HTTP/1.1 200 OK\n"
ERROR404 = "HTTP/1.1 404 Not Found\n"
ERROR405 = "HTTP/1.1 405 Method Not Found\n"
HTML = "Content-Type: text/html\r\n\r\n"
CSS = "Content-Type: text/css\r\n\r\n"


# ----------------- Classes --------------------- #

class MyWebServer(socketserver.BaseRequestHandler):

    def handle(self):
        self.data = self.request.recv(1024).strip().decode("utf-8")
        if self.data.startswith('GET'):
            print("Request: " + self.data.split("\r\n")[0])
            url_file, code = decompose_request(self.data)
            print("Sending Request Type: " + code + "\n")
            if code == '200':
                if url_file.endswith("index.html"):
                    sendall_html = generate_sendall(url_file, 'html')
                    self.request.sendall(sendall_html.encode())
                if url_file.endswith('.css'):
                    sendall_css = generate_sendall(url_file, 'css')
                    self.request.sendall(sendall_css.encode())
            elif code == '301':
                sendall_redirect = generate_sendall(url_file, 'redirect')
                self.request.sendall(sendall_redirect.encode())
            else:
                self.request.sendall(ERROR404.encode())

        else:
            # Return status code 405 Method not allowed for (POST/PUT/DELETE)
            self.request.sendall(ERROR405.encode())


# ------------ User Defined Functions ------------#

def decompose_request(data):
    """
    Takes the url of the get request and parse through it to generate the correct file path.
    :param data: the url
    :return: file path
    """
    url = data.split("\r\n")[0].split(" ")[1]
    prefix = 'www'
    delimiter = '/'
    spl = url.split("/")
    length = len(spl)
    if spl[length - 1] == "":
        return existing_file(spl, delimiter, prefix, 1)
    elif not spl[length - 1].endswith(".html") and not spl[length - 1].endswith(".css"):
        return existing_file(spl, delimiter, prefix, 2)
    elif spl[length - 1].endswith(".css"):  # Handle serving css
        return existing_file(spl, delimiter, prefix, 3)

    return prefix + delimiter.join(spl), '200'


def existing_file(spl, delimiter, prefix, if_type):
    """
    Checks if the file requested exists, and whether or not to send a 200, 301 or 404

    :param spl: The url split into a list
    :param delimiter: '/'
    :param prefix: www
    :param if_type: Integer
    :return: data, request type
    """
    if if_type in (1, 2):
        file_exists = os.path.isfile('www/{}/index.html'.format("/".join(spl)))
        if file_exists:
            if if_type == 1:
                return 'index.html', '301'
            else:
                spl.append("index.html")
                return delimiter.join(spl), '301'
        else:
            return "", '404'
    if if_type == 3:
        file_exists = os.path.isfile('www/{}'.format("/".join(spl)))
        if file_exists:
            return prefix + delimiter + "/".join(spl)[1:], '200'
        else:
            return "", '404'


def generate_sendall(file, req_type):
    """
    Adds the correct heading to the HTML/CSS files found in the www folder

    :param file: the html/css file to be opened and read
    :param req_type: either html/css/redirect
    :return: A complete string including the correct headings
    """
    if req_type == 'html':
        sendall = OK + HTML
    elif req_type == 'redirect':
        sendall = "HTTP/1.1 301 Moved Permanently\r\nLocation: {}\n".format(file)
        return sendall
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
