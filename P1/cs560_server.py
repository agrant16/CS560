#!/usr/bin/python3
"""
Names: Alan Grant, Dustin Mcafee
Class: COSC 560 - Advanced Operating Systems
Assignment: Programming Assignment 1 - Basic HTTP Server

This module contains two classes: CS560Handler and CS560Server. These two 
classes have been implemented as a solution to Programming Assignment 1 for
COSC 560 - Advanced Operating Systems at the University of Tennesee - Knoxville.
Combined the two classes create a basic HTTP server capabale of handling GET 
and HEAD requests. It is capable of running basic cgi scripts and of serving 
the following static file types:

    - TEXT FILES
        + HTML
        + CSS
        + PLAIN TEXT
    - IMAGES
        + PNG
        + GIF
        + JPEG
        + X-ICON
"""
import cgi
import http.server
import os
import pathlib
import platform
import socket
import sys
import _thread
import time

# Supported static content types
mimetypes = {'.html': 'text/html',
             '.htm': 'text/html',
             '.css': 'text/css',
             '.jpg': 'image/jpeg',
             '.jpeg': 'image/jpeg',
             '.png': 'image/png',
             '.gif': 'image/gif',
             '.txt': 'text/plain',
             '.ico': 'image/x-icon'}
             

class CS560Handler(object):
    """Custom request handler class. 
    
    This class is capable of handling the content types listed in the 
    above mimetypes dictionary."""
 
    
    def handle(self, request):
        """Performs initial request parsing.
        
        This function performs initial requesting handling by parsing out the
        request method and the requested content.
        
        Args:
            request (str) : HTTP request in str format.
            
        Returns:
            headers (bytes) : The proper headers for the content in bytes format.
            content (bytes) : The requested content in bytes format. 
        """
        req_headers = request.split('\r\n') # split to individual fields

        # Parse the method and the requested content
        request = req_headers[0].split(' ') 
        method = request[0].lower()
        if request[1] == '/':
            self._go_to_home()
            f = './index.html'
        elif request[1] == '/back':
            cwd = os.getcwd()
            self._go_to_home()
            f = '.' + '/'.join(cwd.split('P1')[1].split('/')[:-1])
            print(f)
        else:
            self._go_to_home()
            f = '.' + request[1]
            f = f.replace('server/server', 'server')
        # generate response content
        headers, content = self._respond(method, f) 
        return headers, content   


    def _go_to_home(self):
        """ Simple helper function to change the current directory to the 
        base project directory.
        """
        cwd = os.getcwd()
        new_dir = cwd.split('P1')[0] + 'P1'
        os.chdir(new_dir)
        
            
    def _respond(self, method, fp):
        """Base handler function for parsing requests and returning the 
        proper content. 
        
        Processes incoming requests and returns proper content. There are three 
        possiblities here:
        
            1. method=='GET'. The contents of the file and the proper headers  
               are retrieved.
               
            2. method=='HEAD'. Similar to method=='GET' except that only the 
               heades are sent.
               
            3. method is neither 'GET' or 'HEAD'. Build a basic webpage based 
               around a 405 error code and sends this as the content. 
        
        Args:
            method (str) : The type of request (GET, HEAD, POST, etc.)
            fp (str) : The file path to the requested content. 
            
        Returns:
            headers (bytes) : The proper headers for the content in bytes format.
            content (bytes) : The requested content in bytes format. 
        """                    
        if method == 'get':
            headers, content = self._do_GET(fp)
        elif method == 'head':
            headers, content = self._do_GET(fp)
            content = '' 
        else:
            content = ('<!doctype=html>\n<html>\n\t<body>\n\t\t<h1>Unsupported'
                        ' Request Method</h1>\n\t\t</br></br>\n\t\t<a href="./'
                        'index.html">Back to front page.</a>\n\t</body>\n'
                        '</html>').encode()
            headers = self._gen_headers(405, len(content), '.html')
        return headers, content
        

    def _do_GET(self, fp):
        """ Processes GET and HEAD requests.
        
        This function process GET requests and handles those requests 
        appropriately. There are four possibilities that are supported for GET 
        requests:
        
            1. The requested content is a supported static file. In this case
               the function retrieves the contents of the file. 
               
            2. The requested content is a directory. Here self._list_dir() is 
               called to dynamically generate a link page of the contents of 
               the directory. 
               
            3. The request contains a query string. In this case the client has
               submitted a form or performed some other action which requires
               the execution of a CGI script. self._run_script() is called and 
               the page generated by the script is retrieved. 
               
            4. The requested content is not found. A basic html page is created 
               to display the 404 error. 
               
        Args:
            fp (str) : The filepath to the requested content. 
            browser (str) : The browser being used to access the server.       
            opsys (str) : The operating system used by the client.
                    
        Returns:
            headers (bytes) : The proper headers for the content in bytes format.
            content (bytes) : The requested content in bytes format. 
        """
        content = ''
        ctype = '.html'
        try:
            if '?' in fp: # contains a query string run cgi script
                content = self._run_script(fp)
            elif pathlib.Path(fp).is_file(): # retrieve the contents of the file
                with open(fp, 'rb') as f:
                    content = f.read()
                    ctype = pathlib.Path(fp).suffix # for getting mimetype
            elif pathlib.Path(fp).is_dir(): # request is a directory
                content = self._list_dir(fp)
            else:
                raise IOError('File not found.')
            headers = self._gen_headers(200, len(content), ctype)
        except IOError as e: # Can't open the requested content.
            content = ('<!doctype=html>\n<html><body><h1>404 File Not Found'
                        '</h1></body></html>').encode()
            headers = self._gen_headers(404, len(content), ctype)
        return headers, content
 
         
    def _gen_headers(self, code, length, ctype):
        """ Generates HTTP response headers.
        
        Handles three possible response codes:
            
            1. 200 - Content is found and response is good.
            
            2. 404 - Content is not found.
            
            3. 405 - Unsupported request method was received. 
            
        Headers are sent in the following format:
        
            HTTP/1.1 {code}
            Connection: {connection response}
            Date: {current date time}
            Content-Type: {mimetype of requested content}
            Server: Alan and Dustin's CS560 Server {Server OS}
            
        Args:
            code (int) : Response code for the header.
            length (int) : Length of content in bytes. 
            ctype (str) : The content type, used to find the proper mimetype. 
            
        Returns:
            h (bytes) : The headers as a bytes object.
        """
        h = 'HTTP/1.1 ' # Every header starts with this. 
        # determine response code
        if (code == 200):
            h += '200 OK\n'
            h += 'Connection: keep-alive\n'
        elif(code == 404):
            h += '404 Not Found\n'
            h += 'Connection: close\n'
        elif(code == 405):
            h += '405 Unsupported Request Method\n'
            h += 'Connection: close\n'
        h += 'Date: {}\n'.format(time.strftime("%a, %d %b %Y %H:%M:%S", 
                                 time.localtime()))
        h += ('Server: Alan and Dustin\'s CS560 Server ({})\n'
              .format(platform.platform()))
        h += 'Content-Length: {}\n'.format(length)
        h += 'Content-Type: {}\n\n'.format(mimetypes.get(ctype))
        return h.encode()
      
    
    def _run_script(self, fp):
        """Handles running of basic CGI scripts using GET requests.
        
        This function handles running CGI scripts. With a GET request the 
        submitted data is sent as a sequence of (id, value) pairs in the
        following form:
        
            id1=value1&id2=value2&id3=value3
            
        We take this string and assign it to the environment variable 
        'QUERY_STRING' which allows us to access this data in a CGI script. 
        The appropriate script is then run and the output of the script 
        (generally an HTML page) is returned as the content.
        
        Args:
            fp (str) : The filepath to the requested content. 
            
        Returns:
            content (bytes) : The HTML page generated by the CGI script. 
        """
        fp, query = fp.split('?')
        os.environ['QUERY_STRING'] = query
        content = os.popen(fp).read()
        return content.encode()
  
  
    def _list_dir(self, my_dir):
        """Lists the contents of a directory as a simple HTML page.
        
        Creates a basic HTML page listing the contents of the given directory. 
        A link is created to each item in the directory.

        Args:
            my_dir (str) : The filepath to the requested directory.
                                    
        Returns:
            content (bytes) : The directory listing as an HTML page in bytes 
                           format.
        """
        # Basic html page with placeholders for inserting links later. 
        dir_listing = ('<!doctype=html>\n<html lang="en"><head>'
                       '<meta charset="utf-8">\n<title>Alan & Dustin\'s '
                       'Webserver</title>\n<meta name="description" '
                       'content="Alan & Dustin\'s Webserver">\n</head>\n'
                       '<body>\n<h1>{0}</h1>\n<ul>\n{1}\n</ul>\n</body>\n'
                       '</html>\n')
                       
        # Store the links in a list for insertion into the unordered list 
        # on the web page.
        self._go_to_home()
        back_link = '/'.join(my_dir[2:].split('/')[:-1])
        if back_link == '':
            back_link = '/'
        ul = []
        for e in os.listdir(my_dir):
            my_dir1 = my_dir[2:]
            ul.append('<li><a href="{0}/{1}">{2}</a></li>'.format(my_dir1, e, e))
        # Join the links with a linefeed and carriage return and insert 
        # them into the webpage. 
        content = dir_listing.format(my_dir[1:], '\n'.join(ul))
        return content.encode()   
        
        
class CS560Server(object):
    """ Simple socket server which uses CS560Handler to act as a basic HTTP 
    server.
    
    Creates a connection on localhost at the given port and runs the webserver
    from the current directory.
    
    Args:
        port (int) : The port the server is to listen on.
    
    Attributes:
        host (str) : The hostname the server is running on (we use localost).
        port (int) : The port the server is to listen on.
        handler (CS560Handler) : The request handler used to retreive content. 
    """


    def __init__(self, port):
        self.host = 'localhost'
        self.port = port
        self.handler = CS560Handler()
        
        
    def start_server(self):
        """ Function to start the server running.

        This function attempts to open a connection with self.port and bind 
        that connection to (self.host, self.port). If port is successfully 
        connected to we begin serving content to that port forever. If the 
        port cannot be connected to, we report this to the user and shutdown 
        the server. 
        """
        try:
            print('Starting server on {}...'.format(self.port))
            self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.s.bind((self.host, self.port))
            print('Port acquired. Listening...')
            print('Press CTRL+C to shutdown server.\n')
            self._serve_forever()
        except OSError as e:
            print("Warning: Could not acquire port:", self.port,"\n")
            
        
    def shutdown(self):
        """Basic shutdown function to close the open socket."""
        self.s.shutdown(socket.SHUT_RDWR)


    def _threaded_response(self, conn, addr):
        """This function responds to requests from clients.
        
        Creates an instance of CS560Handler to handle HTTP requests from 
        clients. The function is used as a threaded function so each new
        client runs on its own thread. 
        
        Args:
            conn : The connection to the socket from client att addr.
            addr : The address of the client connected to the server.
        """
        handler = CS560Handler()
        while True:
            try:
                msg = conn.recv(1024)
                if msg: 
                    request = bytes.decode(msg) #receive data from client
                    print(str(request))
                    headers, content = handler.handle(request)
                    print(bytes.decode(headers))
                    conn.sendall(headers + content)
                else:
                    raise error('Connection from {} has been closed.\n'
                                .format(addr))                       
            except:
                conn.close()  
                return False      
                
    
    def _serve_forever(self):
        """ Main loop of the socket server.
        
        This function provides the main loop for the server. Here we constantly 
        listen at self.port and wait for connections. When a new connection is
        established that client is given its own thread to process requests.  
        """
        while True:
            self.s.listen(5)
            conn, addr = self.s.accept()
            conn.settimeout(120)
            print('Connection from {}.\n'.format(addr))
            _thread.start_new_thread(self._threaded_response,(conn, addr))
            
            
# Execute this code if the program is run as an executable.                 
if __name__ == '__main__':
    port = 8080
    try:
        if len(sys.argv) > 1:
            port = sys.argv[1]
        server = CS560Server(port)
        server.start_server()
    except KeyboardInterrupt:
        print(' pressed.')
        print('Server is shutting down.')
        server.shutdown()
