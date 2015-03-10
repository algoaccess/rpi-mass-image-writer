import time
import shlex
import os
from os import listdir
from os.path import isfile, join
from subprocess import Popen, PIPE
from Adafruit_CharLCDPlate import Adafruit_CharLCDPlate

lcd = Adafruit_CharLCDPlate()

nowWriting = False

lcd.clear()

mypath = "images"

imageNames = []

currentImageSelection = 0
listOfDrives = []

def getConnectedDrives():
    commandOutput = runCommandAndGetStdout("lsblk -d | awk -F: '{print $1}' | awk '{print $1}'")
    splitted = commandOutput.splitlines()

    drives = []

    for drive in splitted:
        if drive != "NAME" and not drive.startswith("mmc"):
            drives.append(drive)
            

    return drives

def powerOff():
    lcd.clear()
    lcd.message("Shutting down...")



def refreshSystem():
    global imageNames
    global listOfDrives

    imageNames = [ f for f in listdir(mypath) if isfile(join(mypath,f)) ]
    currentImageSelection = 0;
    listOfDrives = getConnectedDrives()


def refreshLcd():
    numDrives = len(listOfDrives)
    numImages = len(imageNames)

    imageMessage = ""

    if numImages == 0:
        imageMessage = "No images found"
    else:
        imageMessage = imageNames[currentImageSelection]

    lcd.clear()

    message = imageMessage + "\n" + str(numDrives) + " Drive(s)"
    lcd.message(message)



def runCommandAndGetStdout(cmd):
    proc = Popen(cmd, stdout=PIPE, stderr=PIPE, shell=True)
    out, err = proc.communicate()
    return out


def writeImage():

    if len(imageNames) == 0 or len(listOfDrives) == 0:
        return




refreshSystem()
refreshLcd()

while True:
    time.sleep(0.15) #To debounce and prevent excessive CPU use

    if lcd.buttonPressed(lcd.UP):
        currentImageSelection += 1
        
        if currentImageSelection >= len(imageNames):
            currentImageSelection = 0

        refreshLcd()

    elif lcd.buttonPressed(lcd.DOWN):
        currentImageSelection -= 1
        
        if currentImageSelection < 0:
            currentImageSelection = len(imageNames) - 1

        refreshLcd()


    if lcd.buttonPressed(lcd.LEFT):
       refreshSystem()
       refreshLcd()
    
    elif lcd.buttonPressed(lcd.SELECT):
       powerOff()


    elif lcd.buttonPressed(lcd.RIGHT):
        writeImage()
