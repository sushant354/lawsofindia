from xml.dom import Node
import string
from indianlaw.utils import xml_ops
import re

punctuation = [':', '.', ',', ';', ':', '"']

def get_number(xmlNodes):
    for element in xmlNodes:
        if element.nodeType == Node.ELEMENT_NODE and element.tagName == 'number':
            number = xml_ops.get_data(element)
            number = re.sub('-', '', number)
            return number
    return None

def get_tag_data(tagName, xmlNodes):
    for element in xmlNodes:
        if element.nodeType == Node.ELEMENT_NODE and element.tagName == tagName:
            return xml_ops.get_data(element)
    return None

def get_node(xmlNodes, name):
    for node in xmlNodes:
        if node.nodeType == Node.ELEMENT_NODE and node.tagName == name:
            return node
    return None

def get_node_value(xmlNodes):
    value = ''
    ignoreValues = ['\n']
    for node in xmlNodes:
        if node.nodeType == Node.TEXT_NODE:
            if node.data not in ignoreValues:
                value += node.data
            else:
                value += ' '
    return value

def get_complete_tag(xmlNode):
    data = '<%s>' % xmlNode.tagName
    for element in xmlNode.childNodes:
        if element.nodeType == Node.TEXT_NODE: # base case for recursion
            data += element.data
        elif element.nodeType == Node.ELEMENT_NODE:
            data +=  get_complete_tag(element)
    data += '</%s>' % xmlNode.tagName
    return data
def get_tag_elements(xmlNode):
    data = '' 
    for element in xmlNode.childNodes:
        if element.nodeType == Node.TEXT_NODE: # base case for recursion
            data += element.data
        elif element.nodeType == Node.ELEMENT_NODE:
            tagName = element.tagName
            data +=  get_complete_tag(element)
    return data

def sanitize_data(data):
    retData = ''
    global punctuation
    i = 0
   
    lines = string.split(data, '\n')
    for line in lines: 
        words = string.split(line)
        for word in words:
            if i == 0:
                retData = word
            else:
                if word in punctuation:
                    retData += word
                else:
                    retData += ' ' + word
            i += 1
    return retData

def xml_to_data(xmlNode):
    global punctuation

    data = ''
    i = 0
    for node in xmlNode.childNodes:
        if node.nodeType == Node.ELEMENT_NODE:
            tobeAdded = xml_to_data(node)
        elif node.nodeType == Node.TEXT_NODE:
            tobeAdded = sanitize_data(node.data)
        else:
            assert 0
        if i == 0:
            data = tobeAdded 
        else:
            if tobeAdded in punctuation:
                data = data + tobeAdded
            else:
                data = data + ' ' + tobeAdded

        i += 1
    return data

def get_data(xmlNodes):
    i = 0
    for element in xmlNodes:
        tobeAdded = None

        if element.nodeType == Node.ELEMENT_NODE and (element.tagName == 'year' or element.tagName == 'cite_number'):
            tobeAdded = xml_ops.get_xml_tag(element.tagName, get_data(element.childNodes))

        elif element.nodeType == Node.TEXT_NODE:
            if element.data != '\n':
                tobeAdded = string.strip(element.data)

        # add the string if it is not null
        if tobeAdded != None:
            if i > 0:
                data = data + ' ' + tobeAdded
            else: 
                data = tobeAdded
            i += 1

    if i == 0 or data == '':
        return None
    else:
        return data

