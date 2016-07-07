#!/usr/bin/python 

from xml.dom import minidom, Node
import sys
import xmlExtract
import re
import string
import codecs
import logging

ARTICLE      = 4
DECIMAL      = 3
SMALLSTRING  = 2
GENSTRING    = 1
ROMAN        = 0

DEBUG        = None

logger = logging.getLogger('act.arrange_section')

class HierarchyNode:
    def __init__(self, loghandle, name, number):
        self.children  = [] # to child 
        self.parent    = None
        self.name      = name
        self.number    = number
        self.data      = '' 
        self.loghandle = loghandle

    def add_child(self, childNode):
        self.children.append(childNode)
        childNode.parent = self

    def get_node_tags(self, depth): # for section node 
        tags = '<%s>%s' % (self.name, self.data)
        # log this event
        tabstring = ''
        for i in xrange(0, depth):
            tabstring += '\t' 
        logmessage(self.loghandle, '%s%s: %s' % (tabstring, self.name, self.number))
        depth += 1
        for childNode in self.children:
            tags += childNode.get_node_tags(depth)
        tags+= '</%s>\n\n' % self.name
        return tags 

def logmessage(loghandle, message):
    loghandle.write(message)
    loghandle.write('\n')

def num_section_nodes(articleNode):
    n = 0
    for sectionNode in articleNode.childNodes:
        if sectionNode.nodeType == Node.ELEMENT_NODE and sectionNode.tagName == 'section':
            n += 1
    return n

def main(input_xml, loghandle):
    xmlhandle    = minidom.parseString(input_xml)
    documentNode = xmlhandle.childNodes[0].childNodes

    tags        = '<act>'

    for articleNode in documentNode:
        if articleNode.nodeType != Node.ELEMENT_NODE:
            tags += articleNode.data
        else:
            if articleNode.tagName != 'article':
                tags += xmlExtract.get_complete_tag(articleNode)
            else:
                tags += get_article_data(articleNode, loghandle)
    tags +=  '</act>\n'

    return tags

class CompareNumber:
    def __init__(self, val, depthType):
        self.depthTypes = [depthType, -1, -1, -1, -1, -1]
        self.valnum     = [val, None, None, None, None, None]   
        self.nextvals =  self.get_next_vals()

    def get_next_vals(self):
        nextvals = {}
        nextvals[DECIMAL] = ['1', '2', '3', '4', '5', '6', '7', '8', '9', '10',\
                             '11', '12', '13', '14', '15', '16', '17', '18', '19', '20']
        nextvals[ROMAN]   = ['i', 'ii', 'iii', 'iv', 'v', 'vi', 'vii', 'viii', 'ix', 'x',\
                             'xi', 'xii', 'xiii', 'xiv', 'xv', 'xvi', 'xvii', 'xviii', 'xix', 'xx']
        nextvals[SMALLSTRING]  = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l',\
                                  'm', 'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z']
        nextvals[GENSTRING] = []
        for valueType in nextvals.keys():
            i = 0
            x = {}
            for a in nextvals[valueType]:
                x[a] = i
                i+= 1
            nextvals[valueType] = x
        return nextvals

    def is_next_val(self, nextval, value1, value2):
        if nextval.has_key(value1) and nextval.has_key(value2) and nextval[value2] == nextval[value1] + 1:
            return True
        else:
            return False

    def is_roman(self, number):
        #check if a number is a roman numeral
        #reg = '^M{0,4}(CM|CD|D?C{0,3})(XC|XL|L?X{0,3})(IX|IV|V?I{0,3})$'
        if number in ['iia', 'iib', 'iic', 'iid', 'iiia', 'iiib', 'iva', 'va', 'vb', 'vc', 'vd', 'via', 'viia']:
            return True

        reg = '^(X|IX|IV|V?I{0,3})$'
        tmp = str(number)
        if re.search(reg, tmp.upper()):
            return True
        else:
            return False

    def is_decimal(self, value):
        if re.match('\d+[a-zA-Z]*$', value) != None:
            return True
        else:
            return False
    
    def value_type(self, value):
        isDecimal  = self.is_decimal(value)
        if isDecimal == True:
            return DECIMAL 
        isRoman = self.is_roman(value)
        if isRoman == True:
            return ROMAN 
        elif re.match('[a-z]+$', value) != None:
            return SMALLSTRING
        else:
            return GENSTRING 
    
    # compares two section numbers and returns 
    # 0 if value1 and value2 are at the same level
    # 1 if value2 is higher in hierarchy that value1
    # -1 if value2 is lower in hierarchy than value1
    # Example: (1,a) = -1
    #          (a,2) = 1
    #          (a,b) = 0 
    def comp_special_nums(self, value1, value2):
        if value1 == 'i' and value2 == 'j':
            retval = (SMALLSTRING, 0) 
        elif value2 == 'i' and (value1 == 'h' or value1 == 'hh' or value1 == 'ha'):
            retval = (SMALLSTRING, 0) 
        elif value2 == 'x' and value1 == 'w':
            retval = (SMALLSTRING, 0) 
        elif value2 == 'y' and value1 == 'x':
            retval = (SMALLSTRING, 0) 
        elif value2 == 'x' and value1 == 'ix':
            retval = (ROMAN, 0) 
        elif value2 == 'xi' and value1 == 'x':
            retval = (ROMAN, 0) 
        elif value2 == 'v' and value1 == 'u':
            retval = (SMALLSTRING, 0) 
        elif value2 == 'w' and value1 == 'v':
            retval = (SMALLSTRING, 0) 
        else:
            retval = None

        return retval

    def comp_nums(self, depth, value1, value2, valueType1):
        #print 'value1: %s type:%d value2: %s type: %d' % (value1, valueType1, value2, valueType2)
        # handle the special case of i
        valueType2 = self.value_type(value2)
        if valueType1 == ARTICLE:
            compval = -1
        else:
            retval = self.comp_special_nums(value1, value2)
            if retval != None:
                (valueType2, compval) = retval
            else:
                if valueType1 == None:
                    valueType1 = self.value_type(value1)

                compval    = self.comp_level(depth, value1, value2, valueType1, valueType2)

        i = compval 
        while i < 0:
            self.depthTypes[depth-i] = -1
            self.valnum    [depth-i] = -1
            i += 1
        # store the state
        self.valnum    [depth - compval] = value2
        self.depthTypes[depth - compval] = valueType2
        return (valueType2, compval)

    def prev_level_match(self, value, valueType, depth):
        matches = []
        for i in range(0, depth):
            if valueType == self.depthTypes[i]:
                matches.append(i)

        if len(matches) <= 0:
            depthmatch = None
        else:
            finalmatch = []
            nextval    = self.nextvals[valueType]
            for match in matches:    
               if self.is_next_val(nextval, self.valnum[match], value):
                  finalmatch.append(match)
            if len(finalmatch) <= 0:
                matches.sort(reverse=True)
                depthmatch = matches[0]
            else:
                finalmatch.sort(reverse=True)
                depthmatch = finalmatch[0]
        if depthmatch == None:
            compval = None
        else:
            compval = depth - depthmatch
        return compval

    def comp_level(self, depth, value1, value2, valueType1, valueType2):
        if valueType1 == valueType2:
            compval =  0
        else:
            # its a new level if it starts with the starting of each type
            if value2 in ['A', '1', 'a']:
                compval = -1
            else:
                compval = self.prev_level_match(value2, valueType2, depth)
                if compval == None: 
                    # move up one level
                    compval = -1

        return compval

def get_article_data(articleNode, loghandle):
    articleNumber  = xmlExtract.get_number(articleNode.childNodes)
    topNode        = HierarchyNode(loghandle, 'article', articleNumber)
    currentNode    = topNode

    depth          = 0 # section heading
    compObj        = CompareNumber(articleNumber, ARTICLE)
    nodeNames  = ['article', 'section', 'subsection', 'subsubsection', 'subsubsubsection', 'subsubsubsubsection']

    previousNumber = articleNumber 

    if DEBUG:
        print 'article: ', articleNumber
    valueType1 = ARTICLE 
    # construct the section hierarchy
    for sectionNode in articleNode.childNodes:
        if sectionNode.nodeType != Node.ELEMENT_NODE or sectionNode.tagName != 'section':
            if sectionNode.nodeType == Node.ELEMENT_NODE:
                currentNode.data += xmlExtract.get_complete_tag(sectionNode)
            else:
                currentNode.data += sectionNode.data
        else: 
            currentNumber = xmlExtract.get_number(sectionNode.childNodes)
            data          = xmlExtract.get_tag_elements(sectionNode)
            #logmessage(loghandle, 'Section: %s' % currentNumber)
            (valueType2, compValue) = compObj.comp_nums(depth, previousNumber, currentNumber, valueType1)
            if DEBUG:
                print depth, previousNumber, currentNumber, compValue, valueType2, compObj.valnum
            valueType1 = valueType2
            if compValue == 0:
                # first find the appropriate type
                nodeName = nodeNames[depth]
                newNode = HierarchyNode(loghandle, nodeName, currentNumber)
                newNode.data = data
                currentNode.parent.add_child(newNode)
                currentNode = newNode
            elif compValue < 0: # start of subsections
                depth       -= compValue
                nodeName     = nodeNames[depth]
                newNode      = HierarchyNode(loghandle, nodeName, currentNumber)
                newNode.data = data
                currentNode.add_child(newNode)
                currentNode  = newNode

            elif compValue > 0: # end of subsections
                parent = currentNode.parent
                for i in range(0, compValue):
                    parent = parent.parent

                nodeName     = nodeNames[depth - compValue]
                newNode      = HierarchyNode(loghandle, nodeName, currentNumber)             
                newNode.data = data

                parent.add_child(newNode)
                currentNode = newNode
                depth      -= compValue
            previousNumber = currentNumber
    return topNode.get_node_tags(0)
 
def print_usage(progname): 
        print 'Usage: %s input_xmlfile output_xmlfile' % progname 
# MAIN
if __name__ == '__main__':
    if len(sys.argv) != 3:
        print_usage(sys.argv[0])
        sys.exit(0)
 
    inhandle = codecs.open(sys.argv[1], 'r', 'utf8')
    xmlstr   = inhandle.read()
    inhandle.close()

    loghandle = codecs.open('sections.log', 'a', 'utf8')
    final_xml = main(xmlstr, loghandle)
    loghandle.close()

    outhandle = codecs.open(sys.argv[2], 'w', 'utf8')
    outhandle.write(final_xml)
    outhandle.close()
