import time
import shlex
import os
import subprocess
from threading import Thread
from os import listdir
from os.path import isfile, join
from subprocess import Popen, PIPE
from Adafruit_CharLCDPlate import Adafruit_CharLCDPlate

COLUMNS = 16
ROWS = 2
imagePath = "images/"

imageNames = []

currentImageSelection = 0
listOfDrives = []

writeStatusLine = ""

justCompleted = False
nowWriting = False
stopWritingNow = False

lastPressedTime = time.time()

lcd = Adafruit_CharLCDPlate()
lcd.begin(COLUMNS, ROWS)
lcd.clear()

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
    runCommandAndGetStdout("poweroff")



def refreshSystem():
    global imageNames
    global listOfDrives

    filesfound = [ f for f in listdir(imagePath) if isfile(join(imagePath,f)) ]

    imageNames = []
    for file in filesfound:
        if file != ".gitignore":
            imageNames.append(file)


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

    driveMessage = ""

    if nowWriting:
        driveMessage = writeStatusLine + "% complete"
    else :
        if justCompleted :
            driveMessage = "Write complete!"
        else :
            driveMessage = str(numDrives) + " Drive(s)"

    lcd.setCursor(0, 0)
    lcd.message(imageMessage[:COLUMNS])
    print imageMessage

    lcd.setCursor(0, 1)
    lcd.message(driveMessage[:COLUMNS])
    print driveMessage




def runCommandAndGetStdout(cmd):
    proc = Popen(cmd, stdout=PIPE, stderr=PIPE, shell=True)
    out, err = proc.communicate()
    return out

def writeThreadFunction(arg):
    global nowWriting
    global writeStatusLine
    global stopWritingNow
    global justCompleted

    process = Popen(arg, stdout=PIPE, stderr=PIPE, shell=True, executable='/bin/bash')
    lines_iterator = iter(process.stderr.readline, b"")
    for line in lines_iterator:

        if stopWritingNow :
            runCommandAndGetStdout("killall pv")
            runCommandAndGetStdout("killall dd")
            process.kill()
            break


        line = line.rstrip()
        
        if line == "100" :
            line = "99" #To not give the impression that write has completed as the value stays at 100% for some time

        if writeStatusLine != line:
            writeStatusLine = line
            refreshLcd()



    if stopWritingNow :
        stopWritingNow = False
        justCompleted = False
    else :
        justCompleted = True

    nowWriting = False
    refreshLcd()


def writeImage():

    global nowWriting
    global writeStatusLine
    global stopWritingNow

    if len(imageNames) == 0 or len(listOfDrives) == 0:
        return

    imagingCommand = constructCommand()

    nowWriting = True
    stopWritingNow = False

    writeStatusLine = "0"
    refreshLcd()

    thread = Thread(target = writeThreadFunction, args = (imagingCommand, ))
    thread.start()




def constructCommand():
    command = "pv -n " + imagePath + "\"" +  imageNames[currentImageSelection] +  "\""
    numDrives = len(listOfDrives)

    firstDriveName = listOfDrives[0]
    firstDriveCommand = " | dd of=/dev/" + firstDriveName + " bs=1M"


    for i in range(1, numDrives):
        nextDriveCommand = " | tee >(dd of=/dev/" + listOfDrives[i] + " bs=1M)"
        command += nextDriveCommand


    command += firstDriveCommand
    print command
    return command



refreshSystem()
refreshLcd()

while True:
    time.sleep(0.01) #To prevent excessive CPU use
    currentTime = time.time()
    
    if (currentTime - lastPressedTime) >= 0.2:

        if lcd.buttonPressed(lcd.UP):
            lastPressedTime = currentTime
            
            if nowWriting :
                stopWritingNow = True
                continue


            if justCompleted :
                justCompleted = False
                continue
        
            currentImageSelection += 1
                
            if currentImageSelection >= len(imageNames):
                currentImageSelection = 0
            
            refreshLcd()

        elif lcd.buttonPressed(lcd.DOWN):
            lastPressedTime = currentTime
            
            if nowWriting :
                stopWritingNow = True
                continue

            if justCompleted :
                justCompleted = False
                continue

            currentImageSelection -= 1
        
            if currentImageSelection < 0:
                currentImageSelection = len(imageNames) - 1

            refreshLcd()


        if lcd.buttonPressed(lcd.LEFT):
            lastPressedTime = currentTime
            
            if nowWriting :
                stopWritingNow = True
                continue

            if justCompleted :
                justCompleted = False
                continue
        
            refreshSystem()
            refreshLcd()
    
        elif lcd.buttonPressed(lcd.SELECT):
            lastPressedTime = currentTime
            
            justCompleted = False
            powerOff()


        elif lcd.buttonPressed(lcd.RIGHT):
            lastPressedTime = currentTime
            
            if justCompleted :
                justCompleted = False
                continue
        
            if nowWriting :
                stopWritingNow = True
            else :
                writeImage()
