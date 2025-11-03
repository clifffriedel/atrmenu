#!/usr/bin/env python3

# PLEASE READ!  Curses uses y,x notation for things so make sure to enter values appropriately!

# import needed functions
import os
import sys
import argparse
import curses
import shlex
import subprocess
import time

# parse arguments
parser = argparse.ArgumentParser(description='Atari Menu');
parser.add_argument ('-d','--directory',default='.',help='Directory where your .atr files reside (default is current working directory');
parser.add_argument ('-s','--serial',default='/dev/ttyUSB0',help='Default serial port (default is /dev/ttyUSB0');
parser.add_argument ('-i','--sio2linux',default='.',help='Directory where sio2linux resides (default is current working directory.)');
parser.add_argument ('-e','--executable',default='sio2linux',help='Which executable to use (sio2linux for 64-bit systems, sio2linux32 for 32-bit systems)');
args = parser.parse_args()

# define needed variables
results = []
filepos = 0
myscreen = curses.initscr()
(h,w) = myscreen.getmaxyx()
p = None
dirpage = 0

# Prepare curses
curses.start_color()
curses.init_pair(1,curses.COLOR_WHITE, curses.COLOR_BLUE)
curses.init_pair(2,curses.COLOR_WHITE, curses.COLOR_RED)
curses.noecho()
curses.cbreak()
curses.curs_set(0)
myscreen.keypad(1)

# functions

def initialScreen(height,width,color,topline):
    myscreen.attron(curses.color_pair(color))
    myscreen.hline(0,0," ",width)
    myscreen.hline((height-1),0," ",width)
    myscreen.addstr(0,0,topline,curses.color_pair(color))
    myscreen.attroff(curses.color_pair(color))
    return 0

def showFiles(page,height):
    for i in range(1, height-1):
        if page*(height-2)+i > len(results):
            return 0
        myscreen.addstr(i,0,str(i+(page*(height-2))) + ". " +results[(i-1)+(page*(height-2))],curses.color_pair(0))
    return 0

def cleanScreen(height,width):
    for i in range(1, height-1):
        if i > len(results):
            return 0
        myscreen.attron(curses.color_pair(0))
        myscreen.hline(i,0," ",width)
        myscreen.attroff(curses.color_pair(0))

def cleanBottomLine(height,width):
    myscreen.attron(curses.color_pair(1))
    myscreen.hline(height-1,0," ",width)
    myscreen.attroff(curses.color_pair(1))
    return 0

#list all of the atr files in the directory into results.
results += [each for each in os.listdir(args.directory) if each.endswith('.atr')]
results = sorted(results,key=str.lower)

#Draw initial screen.

if (len(results)):   
    initialScreen(h,w,1,args.directory)
    showFiles(dirpage,h)
    myscreen.chgat(1,0,w,curses.A_REVERSE)
    myscreen.refresh()

#Ok, the initial screen is done, do a loop to catch characters and move the highlighter.  If we hit return, we run sio2linux with the 
#appropriate information.

    while True:
        chr = myscreen.getch()
        if chr == curses.KEY_UP:
            filepos -= 1
            if filepos < 0:
                filepos = 0
            myscreen.chgat(filepos+1,0,w,curses.A_REVERSE)
            myscreen.chgat(filepos+2,0,w,curses.A_NORMAL)
        if chr == curses.KEY_DOWN:
            filepos += 1
# why h-3:  h is the height of the window. -1 because the lines start with 0 instead of 1, -2 because we want to stop at second line from 
# the bottom
            if filepos > (h-3):
                filepos = h-3
            if (dirpage*(h-2))+filepos >= len(results):
                filepos -= 1 
            myscreen.chgat(filepos+1,0,w,curses.A_REVERSE)
            myscreen.chgat(filepos,0,w,curses.A_NORMAL)
        if chr == curses.KEY_LEFT:
            dirpage -= 1
            if dirpage < 0:
                dirpage = 0
            cleanScreen(h,w)
            showFiles(dirpage,h)
            myscreen.chgat(filepos+1,0,w,curses.A_REVERSE)
        if chr == curses.KEY_RIGHT:
            dirpage += 1
            if ((dirpage*(h-2)) > len(results)):
                dirpage -= 1
            cleanScreen(h,w)
            showFiles(dirpage,h)
            myscreen.chgat(filepos+1,0,w,curses.A_REVERSE)               
        if (chr == curses.KEY_ENTER) or (chr == 10):
            if (p is not None) and (alive is None):
                p.kill()
            commandstring = args.sio2linux + "/" + args.executable + " -s \'" + args.serial + "\' \'" + args.directory + "/" + results[filepos+(dirpage*(h-2))] + "\'" 
            p = subprocess.Popen(shlex.split(commandstring), stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            time.sleep(2)
            alive = p.poll()
            if alive is None:
                cleanBottomLine(h,w)
                myscreen.addstr(h-1,0,results[filepos+(dirpage*(h-2))] + " loaded as D1:",curses.color_pair(1))
            else:
                cleanBottomLine(h,w)
                myscreen.addstr(h-1,0,results[filepos+(dirpage*(h-2))] + " did not load successfully.",curses.color_pair(1))                
        if chr == 113:
            curses.endwin()
            if p is not None:
                p.kill()
            sys.exit(0)
        myscreen.refresh()

else:
    initialScreen(h,w,2,"No Atari files found!  Press key to close program")
    myscreen.refresh()
    myscreen.getch()
    curses.endwin()

