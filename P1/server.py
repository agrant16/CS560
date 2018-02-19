#!/usr/bin/python3
import http.server
import socketserver
import os

PORT = 8080

try:
    server = http.server.HTTPServer
    myHandler = http.server.CGIHTTPRequestHandler
    httpd = server(('', PORT), myHandler)
    print('Server is started listening at port {}...'.format(PORT))
    httpd.serve_forever()
except KeyboardInterrupt:
    print('Keyboard Interrupt received. Shutting down the webserver.')
    httpd.socket.close()
