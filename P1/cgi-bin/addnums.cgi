#!/usr/bin/python3
import cgi
import operator
import sys

ops = {'add': (operator.add, ' + '),
       'sub': (operator.sub, ' - '),
       'div': (operator.truediv, ' &#247 '),
       'mul': (operator.mul, ' &#215 '),
       'mod': (operator.mod, ' % ')}
       

form = cgi.FieldStorage()


n1 = float(form['num1'].value)
n2 = float(form['num2'].value)
op = form['op'].value

n3 = ops[op][0](n1, n2)
    
htmlFormat = """<!doctype=html>
<html lang="en">
    <head>
        <meta charset="utf-8">
        <title>Alan & Dustin's Webserver</title>
        <meta name="description" content="Alan & Dustin's Webserver">
    </head>
    <body>
        <h1> Your Math Problem </h1>
        </br>
        </br>
        <h3> {0}{1}{2} = {3:.2f}</h3>
        </br>
        </br>
        <a href="../index.html">Back</a>
    </body>
</html>""".format(n1, ops[op][1], n2, n3)

print(htmlFormat.format(**locals()))
