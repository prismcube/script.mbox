#!/usr/bin/env python

try:
    import fintl
    _ = fintl.gettext
except ImportError:
    _ = lambda s: s

import os, sys, re, token, tokenize, operator

EMPTYSTRING = ''
default_keywords = ['MR_LANG']

def safe_eval(s):
    return eval(s, {'__builtins__':{}}, {})

class TokenEater:
    def __init__(self, options):
        self.__options = options
        self.__messages = {}
        self.__state = self.__waiting
        self.__data = []
        self.__lineno = -1
        self.__freshmodule = 1
        self.__curfile = None
        self.__index = 0

    def __call__(self, ttype, tstring, stup, etup, line):
        self.__state(ttype, tstring, stup[0])

    def __waiting(self, ttype, tstring, lineno):
        opts = self.__options
        if opts.docstrings and not opts.nodocstrings.get(self.__curfile):
            if self.__freshmodule:
                if ttype == tokenize.STRING:
                    self.__addentry(safe_eval(tstring), lineno, isdocstring=1)
                    self.__freshmodule = 0
                elif ttype not in (tokenize.COMMENT, tokenize.NL):
                    self.__freshmodule = 0
                return
            if ttype == tokenize.NAME and tstring in ('class', 'def'):
                self.__state = self.__suiteseen
                return
        if ttype == tokenize.NAME and tstring in opts.keywords:
            self.__state = self.__keywordseen

    def __suiteseen(self, ttype, tstring, lineno):
        if ttype == tokenize.OP and tstring == ':':
            self.__state = self.__suitedocstring

    def __suitedocstring(self, ttype, tstring, lineno):
        if ttype == tokenize.STRING:
            self.__addentry(safe_eval(tstring), lineno, isdocstring=1)
            self.__state = self.__waiting
        elif ttype not in (tokenize.NEWLINE, tokenize.INDENT,
                           tokenize.COMMENT):
            self.__state = self.__waiting

    def __keywordseen(self, ttype, tstring, lineno):
        if ttype == tokenize.OP and tstring == '(':
            self.__data = []
            self.__lineno = lineno
            self.__state = self.__openseen
        else:
            self.__state = self.__waiting

    def __openseen(self, ttype, tstring, lineno):
        if ttype == tokenize.OP and tstring == ')':
            if self.__data:
                self.__addentry(''.join(self.__data))
            self.__state = self.__waiting
        elif ttype == tokenize.STRING:
            self.__data.append(safe_eval(tstring))
        elif ttype not in [tokenize.COMMENT, token.INDENT, token.DEDENT, token.NEWLINE, tokenize.NL]:
            print >> sys.stderr, _('   - %(lineno)s: Unexpected token "%(token)s"') % { 'token': tstring, 'lineno': self.__lineno }
            self.__state = self.__waiting

    def __addentry(self, msg, lineno=None, isdocstring=0):
        if lineno is None:
            lineno = self.__lineno
        if not msg in self.__options.toexclude:
            entry = (self.__curfile, lineno)
            self.__messages.setdefault(msg, {})[entry] = isdocstring

    #def exchange(self, fp):
    def exchange(self, strings):
        reverse = {}
        for k, v in self.__messages.items():
            keys = v.keys()
            keys.sort()
            reverse.setdefault(tuple(keys), []).append((k, v))
        rkeys = reverse.keys()
        rkeys.sort()
        for rkey in rkeys:
            rentries = reverse[rkey]
            rentries.sort()
            for k, v in rentries:
                isdocstring = 0
                if reduce(operator.__add__, v.values()):
                    isdocstring = 1
                v = v.keys()
                v.sort()
                #print >> fp, '<string id="__INDEX@HERE__">%s</string>' %(repr(k))
                ret = repr(k)
                #print ret[1:len(ret)-1]
                #strings.append(ret[1:len(ret)-1])
                if ret[0] == '"' :
           	        strings.append(ret[1:len(ret)-1])
                else :
                    strings.append(repr(k))


def main():
    class Options:
        keywords = []
        docstrings = 0
        nodocstrings = {}

    options = Options()

    fpbase = open(sys.argv[1])
    #print >> sys.stdout, "[*]",sys.argv[1]
    #(name, ext) = os.path.splitext(sys.argv[1])
    #resultname = name + ".xml"

    options.keywords.extend(default_keywords)
    options.toexclude = []

    eater = TokenEater(options)
    tokenize.tokenize(fpbase.readline, eater)
    #eater.exchange(open(resultname, 'w'))

    strings=[]
    eater.exchange(strings)
    print strings

if __name__ == '__main__':
    main()

