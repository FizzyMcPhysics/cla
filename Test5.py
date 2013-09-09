# -*- coding: utf-8 -*-
"""
Created on Sat June 1 18:43:34 2013

Moved robot states to Robot.py
Automated rows and cols


@author: benjamin
"""


#!/usr/bin/python
from region4 import Region
from config import *
from inputbit import InputVector
from Robot4 import Robot
import matplotlib.pyplot as plt
import numpy as np
from datetime import datetime
from time import sleep

#from nxt.sensor import*    

#brick = nxt.locator.find_one_brick()


def sensors(robo, timediff):
    senselist = [
                # sense, min value, max value
                robo.sonarReading(), 7, 65,                   # 1
                robo.sonarVelocity(timediff), -30, 30,        # 2
                robo.sonarAcceloration(timediff), -100, 100,  # 3
                
                robo.motorPositionA(), -10, 10,               # 4
                robo.motorVelocityA(timediff), -5, 5,         # 5
                robo.motorAccelorationA(timediff), -10, 10    # 6
                ]
    return senselist

def experiment(robot):
    senses = sensors(robot, 1) 
    rows = 10
    cols =10
    #rows = len(senses) # Rows x Cols is the number of Columns in the region. 
    #cols = numbits
    coverage = 120 #=10
    sensesToBePredicted = [1]
    motor_power = 70 # %
    highestStability = 0 # %
    plateauCounter = 0
    numRuns = 1
    round = 0
    testingRoundCounter = 0
    #trainingRounds = numRounds/4
    stabilities = []
    sonarPositionResults = []
    sonarVelocityResults = []
    sonarAccelorationResults = []
    motorPositionResults = []
    motorVelocityResults = []
    motorAccelorationResults = []
#    sonarPredictions = []
    inputVectors = InputVector(0)  # inputVectors is an InputVector() object of len 0.
    predictions = dict()
    robot.state = "Going Forwards"    
    # Get a non-local variable and feed it to a local one for local manipulation.
    desiredLocalActivity = DESIRED_LOCAL_ACTIVITY    
    # This sets up a new region, called newRegion,
    # a variable called ouputVector, which calls a method to find just that,
    # and a variable for the number of correct prodicitons, initialised as 0. 
    newRegion = Region(rows, cols, inputVectors, coverage, desiredLocalActivity,sensesToBePredicted,numbits)
    outputVector = newRegion.getOutputVector()
    correctBitPredictions = 0

    
    now = datetime.now()
    then = now
    sleep(1) # This sleep statment is important to prevent weird starting data from swamping the rest of the results. 
    robot.move(motor_power)
    print robot.state 

    # This is where the action starts. This loop forms the main body of the test.
    # For every time round, an input is given, the CLA updates spacial and temporal 
    # poolers with this new input and an output is found.    
    #for round in range(numRounds): 
    while testingRoundCounter == 0:   
   
        if robot.state == "Kill Switch: Engage!":
            break
        end_this_round = False
        stuck_counter = 0
        round += 1
        
        if plateauCounter >= 50:
            robot.trainingState == False
            testingRoundCounter += 1
            print ("Testing round: %d" % testingRoundCounter) 
        else:
            print ("Training round: %d" % round) # Prints the number of the round 
        
        #printStats(inputString, currentPredictionString)
        robot.move(motor_power)
        
        while end_this_round is False:            
            inputVectors.upDateVector(0)  # resets the vector bits
            
            then = now        
            now = datetime.now()    
            deltat = now - then
            timedifference = float(deltat.total_seconds())
            #timedifference = clockUpdate(now, then)
            #print timedifference
            
            senses = sensors(robot, timedifference)
    
            sonarPositionResults.append(robot.currentSonarReading)
            sonarVelocityResults.append(robot.currentSonarVelocity)
            sonarAccelorationResults.append(robot.currentSonarAcceloration)
            motorPositionResults.append(robot.currentMotorPosition)
            motorVelocityResults.append(robot.currentMotorVelocity)     
            motorAccelorationResults.append(robot.currentMotorAcceloration) 
            
#            print "sonar", robot.currentSonarReading, robot.currentSonarVelocity, robot.currentSonarAcceloration             
#            print "motor", robot.currentMotorPosition, robot.currentMotorVelocity, robot.currentMotorAcceloration
#            print ""
            
            numSenses = len(senses)/3
            for i in range(numSenses): # For each sense
                e = i*3 # Find the element number of the sense 
                reading = senses[e]
                minimum = senses[e+1]
                maximum = senses[e+2]
#                print reading
#                print minimum
#                print maximum
#                print ""
                setInput(numbits, reading, inputVectors, minimum, maximum)  # each sense as a bit
                
                
            inputString = inputVectors.toString() # Converts bit string into acutal string, so that the CLA can handle them?
            outputString = outputVector.toString()
            
            
#            for i in range(numSenses): # Prints out each sense's input string in a block. 
#                start = i*numbits
#                end = start+numbits
#                print inputString[start:end]
#                print ""
#            print ""
 
       
            if outputString in predictions: # If output string has been seen before, 
                currentPredictionString = predictions[outputString] 
                # summon the last input that caused that prediction and make it the "currentPredictionString"? That's confusing...
            else:
                currentPredictionString = "[New input]" # If not seen before, 
            predictions[outputString] = inputString # update the i/o record with the new relationship 
            correctBitPredictions += stringOverlap(currentPredictionString, predictions[outputString]) 
            #    without training rounds, stringOverlap will be trying to compare binary stings with the string 'New input'. So correct Bitoutputs is going to be 0 for a while,
            #    until inputs start repeating.
                
                
            newRegion.runCLA() # The CLA bit!
            numRuns += 1
            
            
            """ Experimental Code """
            #newRegion.getPredicitions(sensesToBePredicted,numbits)
            #sonaroutputs.append(newRegion.predictions[0])
            
#            prediction = outputString[0:10]
#            prediction = int(prediction,2)
#            sonarPredictions.append(prediction)
            """ """
            
            Stability = int(float(correctBitPredictions)*100/float(len(senses)/3*numbits*numRuns))
            stabilities.append(Stability)            
            #print ("Stability: %d" % Stability)
            if plateauCounter < 50:
                if Stability > highestStability:
                    highestStability = Stability
                    plateauCounter = 0
                elif Stability <= highestStability:
                    plateauCounter += 1            
            
            if robot.killSwitch() == True: # This will terminate all loops and move to the end of the program
                end_this_round = True
                robot.state = "Kill Switch: Engage!"
                print robot.state

            #print robot.currentSonarReading
            independantReading = robot.sonarReading()
            if robot.state == "Going Forwards":
                if independantReading <= 8: 
                    stuck_counter += 1
                    if stuck_counter == 2:     # This routine confirms that a wall is hit, then sends the robot back to the start position
                        robot.stop()             
                        #print "Stuck Reflex"
                        robot.state = "Reversing"
                        stuck_counter = 0
                        motor_power = -motor_power
                        robot.move(motor_power)
            elif robot.state == "Reversing":                   
                if independantReading >= 65: 
                    stuck_counter += 1
                    if stuck_counter == 2:     # This routine confirms that a wall is hit, then sends the robot back to the start position
                        robot.stop()             
                        #print "Stuck Reflex"
                        robot.state = "Going Forwards"
                        stuck_counter = 0
                        motor_power = -motor_power
                        robot.move(motor_power)                
                        end_this_round = True 
 
             
#            if robot.trainingState == True:
#                print ("Highest Stability: %d percent" % highestStability)
     
     # With the experiment now over, stat summaries are now printed. 
#    for key in predictions:
#        print("key: " + key + " predictions: " + predictions[key])
    robot.stop()    
    print ("Highest Stability: %d percent" % highestStability)
    print "Number of runs:", numRuns
    #print("Stability: " + str(float(correctBitPredictions)/float(30*(numRounds-trainingRounds))))
    
    #code below prints a graph
#    runs = np.arange(1, numRuns, 1)

#    plt.figure(1)
#    plt.subplot(321)
#    plt.grid(True)
#    plt.plot(runs, sonarPositionResults, 'b-')
#    plt.ylabel("Sonar Position, cm")
##    plt.title("Robot sonar Position results")
#    plt.subplot(323)
#    plt.grid(True)
#    plt.plot(runs, sonarVelocityResults, 'g-')
#    plt.ylabel("Sonar Velocity, cm/s")
#    plt.subplot(325)
#    plt.grid(True)
#    plt.plot(runs, sonarAccelorationResults, 'r-')
#    plt.ylabel("Sonar Acceloration, cm/s/s")
#    plt.xlabel("Number of CLA runs")
#    plt.subplot(322)
#    plt.grid(True)
#    plt.plot(runs, motorPositionResults, 'b-')
#    plt.ylabel("Motor Position, rotations")
##    plt.title(graphTitle)
#    plt.subplot(324)
#    plt.grid(True)
#    plt.plot(runs, motorVelocityResults, 'g-')
#    plt.ylabel("Motor Velocity, rotations/s")
#    plt.subplot(326)
#    plt.grid(True)
#    plt.plot(runs, motorAccelorationResults, 'r-')
#    plt.ylabel("Motor Acceloration, rotations/s/s")
#    plt.xlabel("Number of CLA runs")
#    plt.show()

def stringOverlap(str1,str2):
    count = 0
    length = min(len(str1),len(str2)) # Returns the length of the smallest string
    for i in range(length):           # For the length of the smallest string, compare the bits
        if (str1[i] == str2[i]):    # If bits are equal, increment 'count'. 
            count += 1
    return count                     # Returns the number of bits in two strings which are the same. 
    
#def clockUpdate(now, then):
#    then = now        
#    now = datetime.now()    
#    deltat = now - then
#    return float(deltat.total_seconds())

def setInput(vectorLength, senseValue, newVector, Min, Max): # Turns numbers into binary strings
    vector = InputVector(vectorLength)   
    Range = Max - Min      
    if Min <= 0:
        Range += 1
    bucketStart = int( (senseValue-Min)*numstates/Range )
#    print Range
#    print bucketStart
    bucketEnd = bucketStart + bucketWidth
    for i in range(vectorLength):
        if ((i >= bucketStart) and (i <= bucketEnd)):
            vector.getBit(i).setActive(True)
        else:
            vector.getBit(i).setActive(False)       
    newVector.extendVector(vector)


robot = Robot()
print robot.state
experiment(robot) 
# This is the only bit that really executes. Everythig else is just a method. The test count method calls all the others.
