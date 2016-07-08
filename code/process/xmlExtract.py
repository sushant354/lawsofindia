from xml.dom import Node
import string
from xml.sax import saxutils
import re
import sys
from datetime import datetime, date

punctuation = [':', '.', ',', ';', ':', '"']

def get_unescaped_data(xmlNode):
    return saxutils.unescape(xmlNode.childNodes[0].data)

def get_xml_tag(tagName, tagValue, escape = True):
    if isinstance(tagValue, int):
        xmltag = u'<%s type="int">%d</%s>' % (tagName, tagValue, tagName)
    elif isinstance(tagValue, float):
        xmltag = u'<%s type="float">%f</%s>' % (tagName, tagValue, tagName)
    elif isinstance(tagValue, datetime):
        xmltag = u'<%s type="datetime">%s</%s>' % (tagName, tagValue.strftime('%Y-%m-%d %H:%M:%S'), tagName)
    elif isinstance(tagValue, date):
        if tagValue.year <1900:
            value = '%d-%d-%d' % (tagValue.year, tagValue.month, tagValue.day)
        else:
            value = tagValue.strftime('%Y-%m-%d')
        xmltag = u'<%s type="date">%s</%s>' % (tagName, value, tagName)
    elif tagValue:
        if escape:
            if not isinstance(tagValue, unicode):
                print 'NON-UNICODE TAG VALUE', type(tagValue), tagName, tagValue
                sys.stdout.flush()
                assert 0

            tagValue = escape_xml(tagValue)

        xmltag = u'<%s>%s</%s>' % (tagName, tagValue, tagName)
    else:
        xmltag = u'<%s></%s>' % (tagName, tagName)
    return xmltag 

def get_number(xmlNodes):
    for element in xmlNodes:
        if element.nodeType == Node.ELEMENT_NODE and element.tagName == 'number':
            number = get_unescaped_data(element)
            number = re.sub('-', '', number)
            return number
    return None

def get_tag_data(tagName, xmlNodes):
    for element in xmlNodes:
        if element.nodeType == Node.ELEMENT_NODE and element.tagName == tagName:
            return get_unescaped_data(element)
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
            tobeAdded = get_xml_tag(element.tagName, get_data(element.childNodes))

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

# xml 1.0 valid characters:
#    Char ::= #x9 | #xA | #xD | [#x20-#xD7FF] | [#xE000-#xFFFD] | [#x10000-#x10FFFF]
# so to invert that, not in Char ::
#       x0 - x8 | xB | xC | xE - x1F 
#       (most control characters, though TAB, CR, LF allowed)
#       | #xD800 - #xDFFF
#       (unicode surrogate characters)
#       | #xFFFE | #xFFFF |
#       (unicode end-of-plane non-characters)
#       >= 110000
#       that would be beyond unicode!!!
_illegal_xml_chars_RE = re.compile(u'[\x00-\x08\x0b\x0c\x0e-\x1F\uD800-\uDFFF\uFFFE\uFFFF]')

def replace_xml_illegal_chars(val, replacement=' '):
    """Filter out characters that are illegal in XML."""

    return _illegal_xml_chars_RE.sub(replacement, val)

def escape_xml(tagvalue):
    tagvalue = replace_xml_illegal_chars(tagvalue)
    return saxutils.escape(tagvalue)


