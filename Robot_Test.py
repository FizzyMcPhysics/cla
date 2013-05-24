# -*- coding: utf-8 -*-
"""
Created on Mon May 13 18:07:03 2013

It works!

@author: benjamin
"""
from Robot import *
from time import sleep
import matplotlib.pyplot as plt
import numpy as np

sleepytime = 1 # Time between readings in seconds
steps = 8
sonarPositionResults = []
sonarVelocityResults = []
sonarAccelorationResults = []

#touch = Touch(brick, PORT_4)


robot = Robot() # new nerve object for reading and controlling the motors and sensors

    
#robot.resetMotors()     # resets the tachometer
initialPosition = robot.sonarReading()
robot.move()           # moves the robot



for i in range(steps):   
    robot.motorPosition()
    robot.motorVelocity(sleepytime)
    robot.motorAcceloration(sleepytime)
   
    robot.sonarReading()    
    robot.sonarVelocity(sleepytime)
    robot.sonarAcceloration(sleepytime)
   
    print robot.currentMotorPosition, robot.currentMotorVelocity, robot.currentMotorAcceloration
    print robot.currentSonarReading, robot.currentSonarVelocity, robot.currentSonarAcceloration 
    print ' '
    
    sonarPositionResults.append(robot.currentSonarReading)
    sonarVelocityResults.append(robot.currentSonarVelocity)
    sonarAccelorationResults.append(robot.currentSonarAcceloration)

    if robot.killSwitch() == True:  # This works!
       break
    if robot.currentSonarReading <= 8:
       robot.move(-75)
       #robot.stop()
    if robot.currentSonarReading >= initialPosition:
       robot.move(75)
   
    sleep(sleepytime)   
    
robot.stop()    

time = np.arange(0, int(steps*sleepytime), 1) # from 0 to blah, in steps of  1. 
plt.figure(1)
plt.subplot(311)
plt.plot(time, sonarPositionResults)
plt.plot(time, sonarPositionResults, 'bo')
plt.ylabel('Distance cm')
plt.title('Robot sonar readings relative to oncoming wall')
plt.grid(True)

plt.subplot(312)
plt.plot(time, sonarVelocityResults)
plt.plot(time, sonarVelocityResults, 'ro')
plt.ylabel('Velocity cm/s')
plt.grid(True)

plt.subplot(313)
plt.plot(time, sonarAccelorationResults)
plt.plot(time, sonarAccelorationResults, 'go')
plt.ylabel('Acceloration cm/s/s')
plt.xlabel('Time in seconds')
plt.grid(True)

plt.show()
