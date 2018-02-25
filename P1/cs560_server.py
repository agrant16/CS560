#!/usr/bin/python3
"""
Names: Alan Grant, Dustin Mcafee
Class: COSC 560 - Advanced Operating Systems
Assignment: Programming Assignment 1 - Basic HTTP Server

This module contains two classes: CS560Handler and CS560Server. These two 
classes have been implemented as a solution to Programming Assignment 1 for
COSC 560 - Advanced Operating Systems at the University of Tennesee - Knoxville.
Combined the two classes create a basic HTTP server capabale of handling GET 
and HEAD requests. It is capable of serving the following static file types:

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
import os
import pathlib
import platform
import socket
import sys
import threading
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
