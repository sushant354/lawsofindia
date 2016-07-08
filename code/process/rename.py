from xml.dom import minidom, Node
import string
from xml.sax import saxutils
import re
import os

import xmlExtract

reobj = re.compile('\w+')

def get_title_node(xmlnode):
    node = xmlExtract.get_node(xmlnode.childNodes[0].childNodes, 'title')
    return node 

def get_data(xmlnode):
    data = []

    for childnode in xmlnode.childNodes:
        if childnode.nodeType == Node.ELEMENT_NODE:
            data.append(get_data(childnode))
        elif childnode.nodeType == Node.TEXT_NODE:
            data.append(saxutils.unescape(childnode.data))

    return u''.join(data)

def get_title(filename):
    xmlnode = minidom.parse(filename)
    title_node = get_title_node(xmlnode)

    if title_node == None:
        title = xmlExtract.get_unescaped_data(xmlnode.childNodes[0])
    else:
        title = get_data(title_node)

    title = title.title()
    words = reobj.findall(title)        
    words.append(filename)
    
    return '_'.join(words)

if __name__ == '__main__':
    files = []
    for filename in os.listdir('.'):
        if filename.endswith('swp'):
            continue
        
        newfile = get_title(filename)
        files.append((filename, newfile))

    for f in files:
        print 'git mv %s %s' % (f[0], f[1])

