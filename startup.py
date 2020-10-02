#startup.py v4 - by Mark Harris with contribution from Stuart. Thank you for your help.
#    Used to start 3 scripts, one to run the metar leds and one to update an LCD display or OLED displays. A 3rd as watchdog.
#    Taken from https://raspberrypi.stackexchange.com/questions/39108/how-do-i-start-two-different-python-scripts-with-rc-local

import time
import threading
import os
import config
import sys
import logging
import logzero                                  #had to manually install logzero. https://logzero.readthedocs.io/en/latest/
from logzero import logger
import config                                   #Config.py holds user settings used by the various scripts
import admin
from subprocess import PIPE, Popen
import string

# Setup rotating logfile with 3 rotations, each with a maximum filesize of 1MB:
version = admin.version                         #Software version
loglevel = config.loglevel
loglevels = [logging.DEBUG, logging.INFO, logging.WARNING, logging.ERROR]
logzero.loglevel(loglevels[loglevel])           #Choices in order; DEBUG, INFO, WARNING, ERROR
logzero.logfile("/NeoSectional/logfile.log", maxBytes=1e6, backupCount=3)
logger.info("\n\nStartup of startup.py Script, Version " + version)
logger.info("Log Level Set To: " + str(loglevels[loglevel]))

#misc settings
displayused = config.displayused                #0 = no, 1 = yes. If no, then only the metar.py script will be run. Otherwise both scripts will be threaded.
autorun = config.autorun                        #0 = no, 1 = yes. If yes, live sectional will run on boot up. No, must run from cmd line.
screenused = config.screenused                  #0 = no, 1 = yes. If yes, commands will be run in screen; otherwise run normally

# Labels for screen sessions in "screen -ls"; these must be unique
screen1 = "metar"
screen2 = "display"
screen3 = "check"

# Thread title names (generally the filenames for the script run)
title1 = "metar-v4.py"                          #define the filename for the metar.py file
title2 = "metar-display-v4.py"                  #define the filename for the display.py file
title3 = "check-display.py"                     #define the filename for the check-display.py file

# Command lines to be run for each program
prog1 = "sudo python3 /NeoSectional/metar-v4.py"
prog2 = "sudo python3 /NeoSectional/metar-display-v4.py"
prog3 = "sudo python3 /NeoSectional/check-display.py"

# Runs a shell command and returns the text output
def runCommand(command):
    process = Popen(
        args=command,
        stdout=PIPE,
        shell=True
    )
    return process.communicate()[0]

# Check to see if a screen session with that name is already running
def checkForRunningScreen (name):
    cmdOutput = runCommand("screen -ls | grep " + name + " | wc -l")
    cmdOutput = cmdOutput.strip()
    number = int(cmdOutput)
    print(str(number) + " of screens of type " + str(name) + " found.")
    if number > 0:
        return True
    else:
        return False

def startprgm(i):
    logger.info("Running thread %d" % i)
    if (i == 0):                                #Run first program prog1
        time.sleep(1)
        logger.info("Running " + title1)        #display filename being run
        # To run the program, either 
        if screenused:
            if not checkForRunningScreen (screen1):
                logger.info("starting screen " + screen1)
                runCommand("screen -dmS " + screen1)
            logger.info("running screen command " + prog1)
            runCommand("screen -S " + screen1 + " -X stuff \"" + prog1 + "^M\"")
        else:
            os.system(prog1)                        #execute filename
    if (i == 1) and (displayused):              #Run second program prog2 if display is  being used.
        logger.info("Running " + title2)                     #display filename being run
        time.sleep(1)
        if screenused:
            if not checkForRunningScreen (screen2):
                runCommand("screen -dmS " + screen2)
            runCommand("screen -S " + screen2 + " -X stuff \"" + prog2 + "^M\"")
        else:
            os.system(prog2)                        #execute filename
    if (i == 2) and (displayused):              #Run second program prog3 if display is  being used (watchdog for displays).
        logger.info("Running " + title3)                     #display filename being run
        time.sleep(1)
        if screenused:
            if not checkForRunningScreen (screen3):
                runCommand("screen -dmS " + screen3)
            runCommand("screen -S " + screen3 + " -X stuff \"" + prog3 + "^M\"")
        else:
            os.system(prog3)                        #execute filename
    pass

if screenused:
    logger.info("Commands will be started with screen utility")
else:
    logger.info("Commands started directly from shell")

if len(sys.argv) > 1 or autorun == 1:
#       print (sys.argv[1] + " from cmd line") #debug
    for i in range(3):
        t = threading.Thread(target=startprgm, args=(i,))
        t.start()
