#!/usr/bin/env python3

from sys import argv
from sys import exit
from os import path
from time import sleep


criticalTemperature = 57  # Critical temperature
idealTemperature = 38  # Desired temperature
gpioPin = 3  # GPIO PIN number, BOARD style

cycleRange = criticalTemperature - idealTemperature
realPath = path.abspath(path.dirname(argv[0]))
scriptPath = path.join(realPath, argv[0])
scriptPath = scriptPath.replace("./", "")
pidFile = path.join('/tmp/fanControl.pid')  # Daemon process ID file
thermalSensor = "/sys/class/thermal/thermal_zone0/temp"  # Thermal zone data
termalRecordCycle = 600  # How many seconds will keep historical data of thermal status (Increasing this value, will increase RAM usage)


def fanSpeedControl(pinHandler, desiredSpeed):
    if desiredSpeed == 1:
        pinHandler.ChangeDutyCycle(45)
        # print("40")
    elif desiredSpeed == 2:
        pinHandler.ChangeDutyCycle(50)
        # print("50")
    elif desiredSpeed == 3:
        pinHandler.ChangeDutyCycle(60)
        # print("60")
    elif desiredSpeed == 4:
        pinHandler.ChangeDutyCycle(70)
        # print("70")
    elif desiredSpeed == 5:
        pinHandler.ChangeDutyCycle(80)
        # print("80")
    elif desiredSpeed == 6:
        pinHandler.ChangeDutyCycle(90)
        # print("90")
    elif desiredSpeed == 7:
        pinHandler.ChangeDutyCycle(100)
        # print("100")
    elif desiredSpeed == 8:
        pinHandler.ChangeDutyCycle(0)
        # print("OFF")
    elif desiredSpeed == 9:
        pinHandler.ChangeDutyCycle(45)
        sleep(5)
        pinHandler.ChangeDutyCycle(38)
        # print("27")


if len(argv) > 1:
    if argv[1] == '--start':
        if path.isfile(pidFile):
            print("Daemon already started or pid file exists")
            exit(1)
        import subprocess
        subprocess.Popen([scriptPath, '--daemon'], stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        exit(0)

    elif argv[1] == '--stop':
        from os import remove
        import RPi.GPIO as GPIO

        GPIO.setwarnings(False)
        GPIO.setmode(GPIO.BOARD)
        GPIO.setup(gpioPin, GPIO.OUT)
        pinHandler = GPIO.PWM(gpioPin, 50)
        pinHandler.start(0)
        try:
            remove(pidFile)
            sleep(3)
            exit(0)
        except:
            pass

    elif argv[1] == '--daemon':
        if path.isfile(pidFile):
            print("Daemon already started or pid file exists")
            exit(1)
        else:
            from math import ceil
            from time import time
            import RPi.GPIO as GPIO

            GPIO.setwarnings(False)
            GPIO.setmode(GPIO.BOARD)
            GPIO.setup(gpioPin, GPIO.OUT)
            pinHandler = GPIO.PWM(gpioPin, 50)
            pinHandler.start(0)

            open(pidFile, 'w').close()
            dutyPhase = 0
            while path.isfile(pidFile):
                filePointer = open(thermalSensor, 'r')
                currentTemperature = ceil(int(filePointer.readline()) / 1000)
                if currentTemperature >= criticalTemperature and dutyPhase != 7:
                    fanSpeedControl(pinHandler, 7)
                    dutyPhase = 7
                elif currentTemperature <= idealTemperature and dutyPhase != 8:
                    fanSpeedControl(pinHandler, 8)
                    dutyPhase = 8
                else:
                    currentDifference = criticalTemperature - currentTemperature
                    fanSpeed = 100 - ceil((currentDifference / cycleRange) * 100)
                    if fanSpeed > 25 and fanSpeed <= 30 and dutyPhase != 9:
                        fanSpeedControl(pinHandler, 9)
                        dutyPhase = 9
                    elif fanSpeed > 30 and fanSpeed < 40 and dutyPhase != 1:
                        fanSpeedControl(pinHandler, 1)
                        dutyPhase = 1
                    elif fanSpeed >= 100 and dutyPhase != 7:
                        fanSpeedControl(pinHandler, 7)
                        dutyPhase = 7
                    else:
                        if fanSpeed > 40 and fanSpeed <= 50 and dutyPhase != 2:
                            fanSpeedControl(pinHandler, 2)
                            dutyPhase = 2
                        elif fanSpeed >= 50 and fanSpeed < 60 and dutyPhase != 3:
                            fanSpeedControl(pinHandler, 3)
                            dutyPhase = 3
                        elif fanSpeed >= 60 and fanSpeed < 70 and dutyPhase != 4:
                            fanSpeedControl(pinHandler, 4)
                            dutyPhase = 4
                        elif fanSpeed >= 70 and fanSpeed < 80 and dutyPhase != 5:
                            fanSpeedControl(pinHandler, 5)
                            dutyPhase = 5
                        elif fanSpeed >= 80 and fanSpeed < 90 and dutyPhase != 6:
                            fanSpeedControl(pinHandler, 6)
                            dutyPhase = 6
                        elif fanSpeed >= 90 and dutyPhase != 7:
                            fanSpeedControl(pinHandler, 7)
                            dutyPhase = 7
                sleep(7)
                filePointer.close()
            exit(0)
    elif argv[1] == '--test':
        if path.isfile(pidFile):
            print("Stopping current instance for test sequence...")
            import subprocess
            subprocess.Popen([scriptPath, '--stop'], stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            sleep(3)
        print("Test sequence starting")
        import RPi.GPIO as GPIO
        GPIO.setwarnings(False)
        GPIO.setmode(GPIO.BOARD)
        GPIO.setup(gpioPin, GPIO.OUT)
        pinHandler = GPIO.PWM(3, 60)
        pinHandler.start(0)
        print("Fan power 0%")
        sleep(5)
        print("Fan power 90%")
        fanSpeedControl(pinHandler, 8)
        sleep(1)
        fanSpeedControl(pinHandler, 6)
        sleep(6)
        print("Fan power 80%")
        fanSpeedControl(pinHandler, 5)
        sleep(6)
        print("Fan power 70%")
        fanSpeedControl(pinHandler, 8)
        sleep(1)
        fanSpeedControl(pinHandler, 4)
        sleep(6)
        print("Fan power 60%")
        fanSpeedControl(pinHandler, 3)
        sleep(6)
        print("Fan power 50%")
        fanSpeedControl(pinHandler, 2)
        sleep(6)
    else:
        print("Sen beni calistirmayi pek bilmiyorsun sanirim?")

else:
    pass
    '''    from io import StringIO
    from time import time
    from time import sleep
    from math import ceil

    ramPointer = StringIO()
    epochTime = str(time())

    maxTemp = 55
    minTemp = 47

    thermalSource = "/sys/class/thermal/thermal_zone0/temp"
    loopCycle = True
    loopLifeTime = 600

    def accelFan(currentSpeed, targetSpeed):
        if currentSpeed > targetSpeed:
            accelSteps = currentSpeed = targetSpeed

    while loopCycle:
        filePointer = open(thermalSource, 'r')
        singleLine = ceil((int(filePointer.readline()) / 1000))
        ramData = "{},{}".format(epochTime, singleLine)
        ramPointer.write(str(ramData))
        print(ramPointer.getvalue())
        # sleep(1)
        filePointer.close()'''