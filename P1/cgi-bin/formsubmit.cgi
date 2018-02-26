#!/usr/bin/python3
"""
Names: Alan Grant, Dustin Mcafee
Class: COSC 560 - Advanced Operating Systems
Assignment: Programming Assignment 1 - Basic HTTP Server

CGI script to take submitted form data and append it to server/messages.txt. 
"""
import cgi
import datetime
import sys

now = datetime.datetime.now()
form = cgi.FieldStorage()

with open ('./server/messages.txt','a+') as outf:
    outf.write(now.strftime("%Y-%m-%d %H:%M") + '\n')
    outf.write('Name: ' + form['name'].value + '\n')
    outf.write('Message: ' + form['message'].value + '\n')
    outf.write('\n')

htmlFormat = """
<html lang="en">
    <head>
        <meta charset="utf-8">
        <title>Alan & Dustin's Webserver</title>
        <meta name="description" content="Alan & Dustin's Webserver">
    </head>

    <body>
        <h1>MESSAGE SUBMITTED</h1>
        </br>
        Messages can be viewed in the file messages.txt when viewing the 
        server contents.
        </br>
        </br>
        <a href="../index.html">Back</a>
    </body>
</html>"""

print(htmlFormat.format(**locals()))

