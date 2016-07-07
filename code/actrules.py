#---------------------------------------------------
# A parser for Indian acts 
# Author: Sushant Sinha
# Date: 11/18/2006
#--------------------------------------------------

import sys
import ply.lex as lex
import ply.yacc as yacc 
import string

tokens = (
    'FOOTNOTES',
    'SPACE',
    'LPAREN',
    'RPAREN',
    'FAKELPAREN',
    'FAKERPAREN',
    'CARRET',
    'NEWLINE',
    'PUNCTUATION',
    'DOT',
    'STAR',
    'NUMBER',
    'NUMBERALPH',
    'WORD',
    'PAGENUMSTART',
    'PAGENUMEND',
    'FOOTNOTESTART',
    'FOOTNOTEEND',
    'CITENUMSTART',
    'CITENUMEND',
)
# ignore these tokens
t_ignore_SPACE       = r'(\t|\ )+'
t_ignore_STAR        = r'\*'
#t_ignore_QOUTES      = r'(\"|\')'
t_ignore_CARRET    = r'(\^(\t|\ )*\d+)'
#t_ignore_DOT       = r'\.'

# xml tags

t_PAGENUMSTART  = '<pagenumber>'
t_PAGENUMEND    = '</pagenumber>'
t_FOOTNOTESTART = '<pagefootnote>'
t_FOOTNOTEEND   = '</pagefootnote>'
t_CITENUMSTART  = '<footcitenum>'
t_CITENUMEND    = '</footcitenum>'
t_FAKELPAREN    = '<fakelparen>'
t_FAKERPAREN    = '<fakerparen>'

t_FOOTNOTES = 'FootNotes'
t_LPAREN      = r'\('
t_RPAREN      = r'\)'
t_NEWLINE     = r'\n'
t_PUNCTUATION = r'''[;:,'"\[\]&-]'''
t_DOT         = r'[.]'
t_NUMBER      = r'\d+'
 
t_NUMBERALPH  = r'(\d+-?[a-zA-Z]+)'
t_WORD        = r'[a-zA-Z]+'
#t_URL       = r'(ftp|http|file)://'+t_

def t_error(t):
    #print "Illegal character '%s'" % t.value[0]
    t.lexer.skip(1)

def p_act(p):
    'act         : sentence newline newline paragraph articles footnotes'
    p[0] = '<act>\n' + '<title>'+ p[1] + '</title>\n\n'+  p[4] + '\n\n'+ p[5] + '\n\n' + p[6] + '</act>\n'
#    'act         : sentence newline newline sentence newline newline paragraph articles footnotes'
#    p[0] = '<act>\n' + '<title>\n'+ p[1] + '\n</title>'+ p[2] + p[3] + p[4] + p[5] + p[6] + p[7] + p[8] + p[9] + '</act>\n'
    return p[0]

def p_articles(p):
    '''articles : articles article
                 | article'''
    if len(p) == 3:
        p[0] = p[1] + '\n\n' + p[2]
    elif len(p) == 2:
        p[0] = p[1]

def p_dot(p):
    'dot : DOT'
    p[0] = p[1]

def p_article(p):
    '''article : number dot paragraph sections
               | NUMBERALPH dot paragraph sections
               | number dot paragraph
               | NUMBERALPH dot paragraph'''
    if len(p) == 5:
        p[0]  = '<article>\n' +  '<number> ' + p[1] + '</number> ' + p[3] + p[4] + '</article>'
    elif len(p) == 4:
        p[0]  = '<article>\n' +  '<number>' + p[1] + '</number>' + p[3] + '</article>'
    # print 'article: ', p[0]

def p_sections(p):
    '''sections : sections section
                   | section'''
    if len(p) == 3:
        p[0] = p[1] + p[2]
    elif len(p) == 2:
        p[0] = p[1] 

def p_section(p):
    '''section : LPAREN WORD RPAREN paragraph
                  | LPAREN NUMBERALPH RPAREN paragraph
                  | LPAREN number RPAREN paragraph'''
    p[0] = '<section>\n' + '<number>' + p[2] + '</number>'+ p[4] + '</section>\n'
    #print 'section: ',p[2]

def p_paragarph(p):
    '''paragraph : paragraph sentence newline newline
                 | sentence newline newline
                 | paragraph newline
                 | paragraph pagefootnote'''
    if   len(p) == 5:
        p[0] = p[1] + p[2] + p[3] + p[4]
    elif len(p) == 4:
        p[0] = p[1] + p[2] 
    elif len(p) == 3:
        p[0] = p[1] + p[2]
def p_lparen(p):
    '''lparen : LPAREN
              | FAKELPAREN'''
    if p[1] == '(':
        p[0] = p[1]
    else:
        p[0] = 'FAKELPAREN'

def p_rparen(p):
    '''rparen : RPAREN
              | FAKERPAREN'''
    if p[1] == ')':
        p[0] = p[1]
    else:
        p[0] = 'FAKERPAREN'

def p_numberdot(p):
    '''numberdot : NUMBER 
                 | NUMBERALPH
                 | numberdot DOT 
                 | numberdot NUMBER
                 | numberdot NUMBERALPH'''
    if len(p) == 3:
        if p[2] == '.':
            p[0] = p[1] + p[2]
        else:
            p[0] = p[1] + ' ' + p[2]
    elif len(p) == 2:
        p[0] = p[1]

def p_withinbrackets(p):
    '''withinbrackets : sentence
                      | numberdot
                      | numberdot sentence'''
    if len(p) == 2:
        p[0] = p[1]
    elif len(p) == 3:
        p[0] = p[1] + ' ' + p[2]
    elif len(p) == 4:
        p[0] == p[0] + p[1] + ' ' + p[2]
    elif len(p) == 5:
        p[0] == p[0] + p[1] + ' ' + p[2] + ' ' + p[3]
                      
def p_sentence(p):
    '''sentence : sentence WORD
		| sentence number
		| sentence NUMBERALPH
                | sentence newline
                | sentence PUNCTUATION
                | sentence lparen withinbrackets rparen
                | sentence CITENUMSTART NUMBER CITENUMEND
                | sentence DOT
                | PUNCTUATION
                | CITENUMSTART NUMBER CITENUMEND
                | WORD'''
    if len(p)   == 5:
        p[0] = p[1] + ' ' + p[2] + p[3]  + p[4] 
    elif len(p) == 4:
        p[0] = p[1]+p[2]+p[3] 
    elif len(p) == 3:
        length = len(p[1])
        if p[2] == '&':
            p[2] = 'and'
 
        if p[2] in [',', ';', ':', '.', ']', '[', "'", '"', '-'] or p[1][length-1] == '\n':
            p[0] = p[1] + p[2]
        else:
            p[0] = p[1] + ' ' + p[2]
    elif len(p) == 2:
        if p[1] == '&':
            p[0] = 'and'
        else:
            p[0] = p[1]


def p_pagefootnote(p):
    '''pagefootnote : FOOTNOTESTART newlines pagenotes pagenum FOOTNOTEEND
                    | FOOTNOTESTART newlines pagenum FOOTNOTEEND'''
    if len(p) == 6:
        p[0] = '<pagefootnote>%s\n%s\n</pagefootnote>' % (p[4], p[3])
    elif len(p) == 5:
        p[0] = '<pagefootnote>%s\n</pagefootnote>' % p[3]

def p_pagenum(p):
    '''pagenum : PAGENUMSTART NUMBER PAGENUMEND
               | PAGENUMSTART NUMBERALPH PAGENUMEND'''
    p[0] = '<pagenum>%s</pagenum>' % p[2]
def p_pagenotes(p):
    '''pagenotes : pagenotes pagenote
                 | pagenote'''
    if len(p) == 2:
        p[0] = p[1]
    elif len(p) == 3:
        p[0] = p[1] + '\n\n' + p[2]

def p_pagenote(p):
    '''pagenote : NUMBER dot pagenotedesc
                | NUMBER pagenotedesc''' 
    if len(p) == 4:
        p[0] = '<pagenote><number>%s</number>%s</pagenote> ' % (p[1],  p[3])
    elif len(p) == 3:
        p[0] = '<pagenote><number>%s</number>%s</pagenote> ' % (p[1],  p[2])

def p_pagenotedesc(p):
    '''pagenotedesc : pagenotedesc LPAREN NUMBER RPAREN sentence newline newline
		    | pagenotedesc LPAREN NUMBERALPH RPAREN sentence newline newline
                    | pagenotedesc LPAREN WORD RPAREN sentence newline newline
                    | pagenotedesc sentence newline newline
                    | pagenotedesc newline
                    | sentence newline newline'''
    if len(p) == 8:
        p[0] = p[1] + p[2] + p[3] + p[4] + ' ' + p[5] + p[6]+ p[7]
    elif len(p) == 5:
        p[0] = p[1] + p[2] + p[3] + p[4]
    elif len(p) == 3:
        p[0] = p[1] + p[2]
    elif len(p) == 4:
        p[0] = p[1] + p[2] + p[3] 

def p_footnotes(p):
    '''footnotes : footnote newline newline ammendments
               | empty'''
    if len(p) == 5:
        p[0] = '<footnote>' + p[4] + '</footnote>'
    else:
        p[0] = ' '        

def p_footnote(p):
    'footnote : FOOTNOTES'
    p[0] = p[1]

def p_ammendments(p):
    '''ammendments : ammendments ammendment
                 | ammendment'''
    if len(p) == 3:
        p[0] = p[1] + p[2]
    elif len(p) == 2:
        p[0] = p[1]

def p_newlines(p):
    '''newlines : newlines newline
                | newline'''
    if len(p) == 3:
        p[0] = p[1] + p[2]
    else: 
        p[0] = p[1]
     
def p_newline(p):
    'newline : NEWLINE'
    p[0] = '\n'
    p.lexer.lineno += 1
   # print "Line Number %d" %   p.lexer.lineno 

def p_empty(p):
    'empty : '
    pass

def p_ammendment(p):
    '''ammendment : number dot sentence newline newline
                | NUMBERALPH dot sentence newline newline'''
    p[0] = '<ammendment>\n' + '<number>' + p[1] + '</number>' + p[3] + '\n</ammendment>' + p[4] + p[5]

def p_number(p):
    'number : NUMBER'
    if 1800 < string.atoi(p[1]) < 2010:
        p[0] = '<year>' + p[1] + '</year>'
    else:
        p[0] = p[1]

#def p_ammendment(p):
#    '''ammendment : CARRET NUMBER
#                  | CARRET WORD''' 
#    print "Ammendment number ",p[2]

def p_error(p):
    print >>sys.stderr, "Syntax error at token", p
    sys.exit(0) 
    # Just discard the token and tell the parser it's okay.
    #yacc.errok()
