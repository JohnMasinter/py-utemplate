#!/usr/bin/env python
"""
util.sh
copy me as starting point for a python command line utility

Copyright (c) 2025-2026, John F Masinter, MIT License, free to use, see "LICENSE"

Version History
1.0 - initial release, John F Masinter, 15-Dec-2026
"""
sVer = "1.0"

import sys
import os
import signal
import time
from datetime import datetime
import platform

sMe = "" # our program name for log messages

#--------------------------------------------------------------------------------
# help text for fUsage()
sHelpText = """
Usage: %s [-d] [-e] [-f value] [action] [value]...

This utility is a starting point for writing a new bash utility. 
Just copy it and start modifying to add everything you want.
It demonstrates parsing several types of cmd line arguments.
It is helpful to give usage examples in this help test.

Actions:
ECHO  print the -f val and value args, minimum one or more value arguments.
DATE  print the -f val if any, and date to console, value args not allowed.
OVER  print os version on console, no -f nor extra value args allowed.

-d    enable debug messages, default off 
-e    enable arbitrary Easy flag, off default
-f    specify arbitrary value, -fval, or -f val, or -f=val

Example 1, echo arguments, specify fish:
$ util.sh -d -f Carp ECHO "one arg" "all second arg" three
Output:
Carp: one two three

Example 2, print date
$ util.sh -a -d -f Bass DATE
Outpuut:
Bass: Wed Dec 24 13:09:00 MST 2025

Version %s, John F Masinter, 10/07/2025
"""

#--------------------------------------------------------------------------------
# global dictionary of parsed command line arguments, set default values here
dArgs = { 
        "Dbug":False,  # debug flag, disabled, -d to enable
        "Easy":False,  # Easy  flag, disabled, -e to enable, arbitrary example
        "Fish":"",     # Fish -fValue, arbitrary example
         "Act":"",     # action word
        "Valc":0,      # number of optional args
        "Vals":[],     # list of optional args
        "argc":0,      # number of cmd line args in argv
        "argp":1       # index as we step thru argv
}

#--------------------------------------------------------------------------------
def fPrnArgs(sSel: str=''):
    """
    Debug, print cmd line args and/or parsed args
    Input: sSel = "" print both, "c" cmdline args only, "p" 2=parsed args only
    """
    global dArgs

    # print raw argv args
    # e.g. util.sh -d -f "Big Carp" ECHO "this is one" "now arg two" three
    # Debug:ARGC=7,ARGV:0=[util.sh],1=[-d],2=[-f],3=[Big Carp],4=[ECHO],5=[this is one],6=[now arg two],7=[three],
    if sSel == "" or sSel == "c":
        print(f"Debug:ARGC={dArgs['argc']},ARGV:", sep="", end="")
        i = 0
        while i < dArgs['argc']:
            print(f"{i}=[{sys.argv[i]}],", sep="", end="")
            i += 1
        print("")
    #if

    # print parsed args
    # e.g. util.sh -d -f "Big Carp" ECHO "this is one" "now arg two" three
    # Debug:Args:Dbug=[y],Easy=[],Fish=[Big Carp],Act=[ECHO],iVal=[3],aVal[0]=[this is one],aVal[1]=[now arg two],aVal[2]=[three],
    if sSel == "" or sSel == "p":
        print(f"Debug:Args:Dbug=[{dArgs['Dbug']}],Easy=[{dArgs['Easy']}],Fish=[{dArgs['Fish']}],Act=[{dArgs['Act']}],Valc={dArgs['Valc']},Vals:", sep="", end="")
        i=0
        while i < dArgs['Valc']:
            val = dArgs['Vals'][i] # easier to read than putting inline
            print(f"[{i}]=[{val}],", sep="", end="")
            i += 1
        print("")
    #fi
# fPrnArgs

#--------------------------------------------------------------------------------
def fUsage(msg: str=""):
    """
    if msg is empty string (""), then print full usage and exit.
    if msg is not empty, then print msg and one line help, and exit.
    this function always exits.
    """
    global sMe, sVer

    # print full usage and exit
    if msg == "":
        print(sHelpText % (sMe,sVer))

    else:
        print(msg,'\n',"For full help use -h or --help", sep="")

    sys.exit(1)
# fUsage

#--------------------------------------------------------------------------------
def fLog(msg, ARG):
    """
    Central logging function, adds timestamp, could also log to file, etc.
    """
    sTime = time.strftime("%H:%M.%S:") 
    print(f"{sTime}:{sMsg}")
# fLog

#--------------------------------------------------------------------------------
def fParseFlags():
    """
    Parse flags from cmd line args into dArgs dictionary
    Return: on success return, on error print usage and exit
    """

    while dArgs['argp'] < dArgs['argc']:

        A = sys.argv[dArgs['argp']] # current arg
        B = ""                      # next arg, if any
        if dArgs['argp']+1 < dArgs['argc']:
            B = sys.argv[dArgs['argp']+1]

        # no more flags? done in this loop
        if A[0:1] != '-':
            break

        # parse binary flags
        if A in ("-d", "-e"):
            if A == "-d": dArgs['Dbug'] = True
            if A == "-e": dArgs['Easy'] = True

        # parse -f value
        elif A[0:2] == "-f":
            if   A[2:3] == "=":
                dArgs['Fish'] = A[3:]       # e.g. -f=Carp -> Carp
            elif len(A) > 2:
                dArgs['Fish'] = A[2:]       # e.g. -fCarp  -> Carp
            elif B != "":       
                dArgs['Fish'] = B           # e.g. -f Carp -> Carp 
                dArgs['argp'] += 1          # used B, so next arg
            else:
                fUsage("*** Error: -f requires an argument.")

        # unexpected "-" flag
        else:
            fUsage("*** Error: -f requires an argument.")

        dArgs['argp'] += 1                  # next arg
    # while
# fParseFlags

#--------------------------------------------------------------------------------
def fParseAct():
    """
    Parse action word (command) from cmd line, comes after flags, before value args
    Return: on success return, on error print usage and exit
    """
    A = "" # current arg
    if dArgs['argp'] < dArgs['argc']:
        A = sys.argv[dArgs['argp']]
    A = A.lower() # e.g. echo

    # parse action word
    if A in ("echo", "date", "over"):
        dArgs['Act'] = A
        dArgs['argp'] += 1   # next arg

    # missing aciton word
    elif A == "":
        fUsage("*** Error: Missing required action word.")

    # unexpected action word
    else:
        fUsage(f"*** Error: Unrecognized action [{A}]")
# fParseAct

#--------------------------------------------------------------------------------
def fParseVals():
    """
    Parse 0 or more action arguments, store in array, preserve spaces
    Return: always succeeds and returns, no errors possible
    """
    while dArgs['argp'] < dArgs['argc']:
        valc = dArgs['Valc']  # easier to read than putting inline
        argp = dArgs['argp']  # ^^^
        dArgs['Vals'].append(sys.argv[argp])
        dArgs['Valc'] += 1 # count Vals
        dArgs['argp'] += 1 # next arg
# fParseVals

#--------------------------------------------------------------------------------
def fValidate():
    """
    Perform additional checks on arguments
    Return: on success return, on error print usage and exit. 
    """
    # ECHO allows -f and requires at least one cmd-arg
    if dArgs['Act'] == "echo" and dArgs['Valc'] < 1:
        fUsage("*** Error: Action ECHO requires one or more value arguments.")

    # DATE allows -f but no extra vals
    if dArgs['Act'] == "date" and dArgs['Valc'] > 0:
        fUsage("*** Error: Action DATE does not allow extra value arguments.")

    # OVER does not allows -f nor extra vals
    if dArgs['Act'] == "over":
        if dArgs['Fish'] != "" or dArgs['Valc'] > 0:
            fUsage("*** Error: Action OVER does not allow -f nor extra value arguments.")
# fValidate

#--------------------------------------------------------------------------------
def fParse():
    """
    Parse the command line arguments into dArgs dictionary.
    command line has three sections in order: flags, action, action-values
    Return: on success return, on error print usage and exit. 
    """
    global dArgs                            # dict to hold cmd line args

    dArgs['argc'] = len(sys.argv)           # num of cmd line args
    if dArgs['argc'] < 2:                   # check number of args
        fUsage()

    if sys.argv[1] in ("-h","-?","--help"): # help requested?
        fUsage()

    # debug, print cmdline args
    if sys.argv[1] == "-d": fPrnArgs("c")

    fParseFlags()                           # parse flags
    fParseAct()                             # parse action
    fParseVals()                            # parse variable values
    fValidate()                             # additional validation

    # debug, print parsed args
    if sys.argv[1] == "-d": fPrnArgs("p")
# fParse

#--------------------------------------------------------------------------------
def fHandler(signo, frame):
    """catch ctl-C and exit, nice to have when stuck in loop or non-responsive"""
    print >> sys.stderr, "\nExiting."
    sys.exit(0)
# fHandler

#--------------------------------------------------------------------------------
def fEcho():
    """
    Execute command ECHO, print args
    return 0 if success, !0 otherwise
    """
    rc = 0

    # print -f value, if any
    if dArgs['Fish'] != "":
        print(f"\"{dArgs['Fish']}\" ", end="")

    # print all act values
    i = 0
    while i < dArgs['Valc']:
        val = dArgs['Vals'][i]
        print(f"\"{val}\" ", end="")
        i += 1
    print("")

    return rc
# fEcho

#--------------------------------------------------------------------------------
def fDate():
    """
    Execute command DATE, display date
    return 0 if success, !0 otherwise
    """
    rc = 0

    # print -f value, if any
    if dArgs['Fish'] != "":
        print(f"{dArgs['Fish']} ", end="")

    # print date and time
    sDate = datetime.today().strftime('%Y-%m-%d %H:%M:%S')
    print(f"{sDate}")

    return rc
# fDate

#--------------------------------------------------------------------------------
def fOver():
    """
    Execute command OVER, display os version
    return 0 if success, !0 otherwise
    """
    rc = 0
    p = platform.system()
    r = platform.release()
    print(f"{p} {r}")
    return rc
# fOver

#--------------------------------------------------------------------------------
def fMain():
    """
    main entry point of program
    parse cmd line args
    dispatch command
    exit with status code of command
    """
    rc = 0                                  # status, 0 = success, !0 = error
    global dArgs, sMe                       # dict to hold cmd line args
    sMe = os.path.basename(sys.argv[0])     # our name for log messages

    signal.signal(signal.SIGINT, fHandler)  # catch ctl-C for controlled exit
    fParse()                                # parse cmd line args into a dictionary

    # Dispatch commands
    if dArgs['Act'] == 'echo': rc = fEcho() # ECHO
    if dArgs['Act'] == 'date': rc = fDate() # DATE
    if dArgs['Act'] == 'over': rc = fOver() # OVER

    sys.exit(rc)
# fMain

#--------------------------------------------------------------------------------
if __name__ == "__main__":
    fMain()

#--------------------------------------------------------------------------------
"""
Examples:

$ python util.py
Usage: util.py [-d] [-e] [-f value] [action] [value]...
...<snip>...

$ python util.py -d -e -f "Big Carp" Echo "Arg one and" two "and three"
Debug:ARGC=9,ARGV:0=[util.py],1=[-d],2=[-e],3=[-f],4=[Big Carp],5=[Echo],6=[Arg one and],7=[two],8=[and three],
Debug:Args:Dbug=[True],Easy=[True],Fish=[Big Carp],Act=[echo],Valc=3,Vals:[0]=[Arg one and],[1]=[two],[2]=[and three],
"Big Carp" "Arg one and" "two" "and three"

$ python util.py -f "Today's Date:"  Date
Today's Date: 2025-12-25 19:01:41

$ python util.py Over
Darwin 25.2.0
## ^^^ on my Mac

## Testing some error conditions

$ python util.py -d -e -f "Big Carp" Echo
Debug:ARGC=6,ARGV:0=[util.py],1=[-d],2=[-e],3=[-f],4=[Big Carp],5=[Echo],
*** Error: Action ECHO requires one or more value arguments.
For full help use -h or --help

$ python util.py -d -e Date one two three
Debug:ARGC=7,ARGV:0=[util.py],1=[-d],2=[-e],3=[Date],4=[one],5=[two],6=[three],
*** Error: Action DATE does not allow extra value arguments.
For full help use -h or --help

$ python util.py -f "Version:" Over
*** Error: Action OVER does not allow -f nor extra value arguments.
For full help use -h or --help

"""
