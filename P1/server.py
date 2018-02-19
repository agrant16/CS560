#!/usr/bin/python3
import http.server
import socketserver
import os

PORT = 8080

try:
    # Create a basic HTTP server
    server = http.server.HTTPServer

    # Create a handler capable of handling basic requests and CGI scripts
    myHandler = http.server.CGIHTTPRequestHandler

    # Open a socket at PORT and start a daemon
    httpd = server(('', PORT), myHandler)
    print('Server is started listening at port {}...'.format(PORT))
    
    # Listen forever at PORT or until the user stops the server.
    httpd.serve_forever()
except KeyboardInterrupt:
    # If the processes is interrupted by CTRL+C close the open socket.
    print('Keyboard Interrupt received. Shutting down the webserver.')
    httpd.socket.close()
