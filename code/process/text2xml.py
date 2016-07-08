import sys
import ply.lex as lex
import ply.yacc as yacc
import codecs

import actrules
import arrange_sections

def print_usage(progname):
    print 'Usage: %s input_textfile output_xmlfile' % sys.argv[0]

def main(infile, outfile, loghandle):
    inhandle  = codecs.open(infile, 'r', 'utf8')
    outhandle = codecs.open(outfile, 'w', 'utf8')

    text      = inhandle.read()
    inhandle.close()
    tokenizer = lex.lex(optimize=0, module = actrules)
    #lex.input(text)
    parser    = yacc.yacc(module = actrules)
    xmlact    = parser.parse(input = text, lexer = tokenizer)

    final_xml = arrange_sections.main(xmlact, loghandle)

    outhandle.write(final_xml)
    outhandle.close()

if __name__ == '__main__':
    if len(sys.argv) != 3:
        print_usage(sys.argv[0])
        sys.exit(0)

    loghandle = codecs.open('sections.log', 'a', 'utf8')
    main(sys.argv[1], sys.argv[2], loghandle)
    loghandle.close()

