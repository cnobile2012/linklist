#!/usr/bin/env python
#
# Determine what functions a variable is used in. I didn't get fancy
# with this program so it has to be run in the directory tree as is.
# If the ../dll_main.c changes then the line numbers and/or functions
# will need to be changed in the funclines.txt file.
#
# $Author$
# $Date$
# $Revision$
#

import sys, string, regex
from regex_syntax import *

funcfile = "funclines.txt"
srcfile = "../dll_main.c"
## searchlist = ["DLL_ORIGIN_DEFAULT", "DLL_HEAD", "DLL_CURRENT", "DLL_TAIL",
##               "DLL_DIRECTION_DEFAULT", "DLL_DOWN", "DLL_UP",
##               "DLL_INSERT_DEFAULT", "DLL_ABOVE", "DLL_BELOW", "head", "tail",
##               "current[^_]", "saved", "infosize", "listsize", "current_index",
##               "save_index", "modified", "search_origin", "search_dir"]
searchlist = ["head", "tail", "current[^_]", "saved", "infosize", "listsize",
              "current_index", "save_index", "modified", "search_origin",
              "search_dir"]
## searchlist = ["DLL_HEAD"]

#---- Functions ----------------------------------
def showline(filename, lineno, line, prog):
    if line[-1:] == '\n':
        line = line[:-1]

    prefix = string.rjust(`lineno`, 3)
    return([prefix, line])

def ggrep(syntax, pat, files):
    if len(files) == 1 and type(files[0]) == type([]):
        files = files[0]

    try:
        prog = regex.compile(pat)
    finally:
        syntax = regex.set_syntax(syntax)

    for filename in files:
        fp = open(filename, 'r')
        lineno = 0
        out = []

        while 1:
            line = fp.readline()

            if not line:
                break

            lineno = lineno + 1

            if prog.search(line) >= 0:
                out.append(showline(filename, lineno, line, prog))
        fp.close()
    return(out)

def grep(pat, *files):
        return ggrep(RE_SYNTAX_GREP, pat, files)

def egrep(pat, *files):
        return ggrep(RE_SYNTAX_EGREP, pat, files)

#---- Start Main ---------------------------------
try:
    fdl = open(funcfile, "r")
except:
    print 'Error: Could not open file:' + funcfile
    sys.exit(1)

list = []
line = fdl.readline()

while line != '':
    list.append(string.split(string.strip(line), ' '))
    line = fdl.readline()

#print list

# Find pattern in source file
for pat in searchlist:
    srclines = egrep(pat, srcfile)
    #print srclines
    i = 0
    func = []

    # Get 1st occurrence of found pattern
    for srcline in srclines:
        # Look up functions and get ranges
        for funcrange in list:
            if string.atoi(srcline[0]) >= string.atoi(funcrange[1]) and \
               string.atoi(srcline[0]) <= string.atoi(funcrange[2]):
#                print "func: %s" % (func)
                flag = 0

                if i == 0:
                    print pat + ":"
                    i = i + 1

                for dup in func:
#                    print "funcrange[0]: %s, dup: %s" % (funcrange[0], dup)
                    if cmp(funcrange[0], dup) == 0:
                        flag = 1
                        break

                if flag == 0:
                    func.append(funcrange[0])

    func.sort()
    for occur in func:
        print "          " + occur
