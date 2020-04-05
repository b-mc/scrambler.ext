#!/usr/bin/env python

"""
Scrambler is a small commandline script made to randomize file names. It stores
a log of all the file renaming events which it later uses to unscramble the
names. This script may not guard against intentional dishonesty, but it does
protect one from unconscious bias.

All of the matching options may be used simultaneously, but only files which
satisfy each restriction will be scrambled (the intersection of each match set).

The log file will always be (initially) located in the directory where the
scrambling took place.

Written by Paul Barton with input from Rachel Vistein
This script may be freely modified and distributed.

Usage:
    scrambler.py (--help | --version)
    scrambler.py [--directory=<dir>] [--extension=<ext>...]
                 [--substring=<sub>...] [--regex=<regex>...] [--log=<filename>]
    scrambler.py [--unscramble=<log>]

Matching Options:
    -e --extension=<ext>...  List one or more file extensions to narrow down
                             which kinds of files will be scrambled.
    -s --substring=<sub>...  Only files which match *at least one of* the
                             provided substrings will be scrambled.
    -r --regex=<regex>       Only files which match the regex will be scrambled.

Location Options:
    -d --directory=<dir>     Specify a nonlocal path location to scramble.
    -l --log=<log>           Manually name the resulting log file, an automatic
                             one will be applied otherwise.

Command Options:
    -u --unscramble=<log>    The scrambler log to use as a reference for
                             unscrambling.
"""

#This is free and unencumbered software released into the public domain.
#
#Anyone is free to copy, modify, publish, use, compile, sell, or
#distribute this software, either in source code form or as a compiled
#binary, for any purpose, commercial or non-commercial, and by any
#means.
#
#In jurisdictions that recognize copyright laws, the author or authors
#of this software dedicate any and all copyright interest in the
#software to the public domain. We make this dedication for the benefit
#of the public at large and to the detriment of our heirs and
#successors. We intend this dedication to be an overt act of
#relinquishment in perpetuity of all present and future rights to this
#software under copyright law.
#
#THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
#EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
#MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
#IN NO EVENT SHALL THE AUTHORS BE LIABLE FOR ANY CLAIM, DAMAGES OR
#OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE,
#ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR
#OTHER DEALINGS IN THE SOFTWARE.
#
#For more information, please refer to <http://unlicense.org/>

import os
import re
import sys
import string
import random
import argparse

#Some agnosticism of Python2 and Python3 names
try:
    input = raw_input
except NameError:
    pass
try:
    range = xrange
except NameError:
    pass

__version__ = '0.2'


def matching(location, extensions, substrings, regex):
    #Compile regex if it was used
    if regex is not None:
        regex = re.compile(regex)

    #Add periods to extensions if not used
    extensions = [ext if ext.startswith('.') else '.' + ext for ext in extensions]

    #Everything in directory
    all_items = os.listdir(location)

    #Remove all directories
    all_files = [item for item in all_items if os.path.isfile(os.path.join(location, item))]

    #Remove all files with .py, .pyc, or .log extensions, also hidden files
    files = []
    for name in all_files:
        base, ext = os.path.splitext(name)
        if ext in ['.py', '.pyc', '.log']:
            continue
        if base[0] == '.':  # hidden file on unix
            continue
        files.append(name)

    #Find files with matches
    if not extensions:
        ext_matches = set(files)
    else:
        ext_matches = set()
    if not substrings:
        sub_matches = set(files)
    else:
        sub_matches = set()
    if regex is None:
        regex_matches = set(files)
    else:
        regex_matches = set()

    for name in files:
        base, ext = os.path.splitext(name)
        #Extension matching
        if ext in extensions:
            ext_matches.add(name)
        #Substring matching
        for substring in substrings:
            if substring in base:
                sub_matches.add(name)
        #Regex matching
        if regex is not None:
            if regex.match(name) is not None:
                regex_matches.add(name)

    return ext_matches & sub_matches & regex_matches


def random_name(name, length=8, chars=string.ascii_uppercase+string.digits):
    '''Creates a random string containing ASCII character'''
    ext = os.path.splitext(name)[1]
    r_name = ''
    for each in range(length):
        r_name += random.choice(chars)
    return('{0}{1}'.format(r_name,ext))


def main():
    #This makes parsing commandline arguments simple
    p = argparse.ArgumentParser(description='Scrambler Parser')
    p.add_argument('-v', '--version', action='version',
                   version='Scrambler {0}'.format(__version__))
    p.add_argument('-d', '--directory', action='store', default=os.getcwd(),
                   help='Specify a nonlocal path location to scramble.')
    p.add_argument('-e', '--extension', action='store', nargs='+', default=[],
                   help='''List one or more file extensions to narrow down \
which kinds of files will be scrambled.''')
    p.add_argument('-s', '--substring', action='store', nargs='+', default=[],
                   help='''Only files which match *at least one of* the \
provided substrings will be scrambled.''')
    p.add_argument('-r', '--regex', action='store', default=None,
                   help='Only files which match the regex will be scrambled.')
    p.add_argument('-l', '--log', action='store', default=False,
                   help='''Manually name the resulting log file, an automatic \
one will be applied otherwise.''')
    p.add_argument('-u', '--unscramble', action='store', default=False,
                   help='Unscramble the filenames from the specified log file.')
    #args will hold the argument values as attributes
    args = p.parse_args()
    #Workflow for scrambling
    if not args.unscramble:
        #Get all of the files that satisfy the matching criteria
        files = matching(args.directory, args.extension,
                         args.substring, args.regex)
        #Move to the new directory
        os.chdir(args.directory)
        #Check for a valid logname
        if args.log:
            logname = args.log
        else:
            logname = '{0}_scramble.log'.format(os.path.split(os.getcwd())[1])

        #Check for pre-existence of the log file, treat
        while os.path.isfile(logname):
            print('The logname \"{0}\" already exists.'.format(logname))
            raw = input('Enter a new name? (Leave blank to abort) ')
            if not raw:
                print('Scrambling Aborted')
                sys.exit()
            else:
                r = os.path.splitext(raw)[0]
                logname = '{0}.log'.format(r)
                print('Logname changed to \"{0}\".'.format(logname))

        print('Writing scrambling events to {0}'.format(logname))

        with open(logname, 'w') as log:
            log.write('Scrambler.py Log\n')
            for each in files:
                new = random_name(each)
                log.write('{0} --> {1}\n'.format(each, new))
                os.rename(each, new)

    else:
        #Split the path into the directory and the name of the log file
        d, log = os.path.split(args.unscramble)
        #Move to the new directory
        d = os.path.abspath(d)
        os.chdir(d)
        #Locate the listed logfile
        if os.path.isfile(log):
            with open(log, 'r') as logfile:
                lines = logfile.readlines()
            if lines[0] != 'Scrambler.py Log\n':
                print('WARNING: {0} does not appear to be Scrambler log!'.format(log))
                sys.exit(1)
            for line in lines[1:]:
                orig, new = line.rstrip().split(' --> ')
                os.rename(new, orig)
            os.remove(log)
        else:
            print('The log file was not found.')

if __name__ == '__main__':
    main()
