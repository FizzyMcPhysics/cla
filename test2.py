# -*- coding: utf-8 -*-
"""
Created on Thu May  9 20:42:10 2013

@author: benjamin
"""

#!/usr/bin/python
from region import Region
from config import *
from inputbit import InputVector
from Robot import *
import matplotlib.pyplot as plt
import numpy as np

#from nxt.sensor import*    

#brick = nxt.locator.find_one_brick()

def experiment():
    rows = 5
    cols = 5
    coverage = 20
    numbits = 10 # I may need more bits for my readngs.
    numRounds = 10
    numRuns = 1
    minimum_distance = 7
    #trainingRounds = numRounds/4
    accuracies = []
    sonarPositionResults = []
    originalInputVector = InputVector(numbits)
    inputVector = InputVector(0)
    predictions = dict()
    state = "Going Forwards"

 
    # Repeat several times to increase activity:
    # Seems to just extend the number of elements in inputVector by numbits (10) 3 times. 
    # Why not extend it by 3*numbits?
    # I think becuase rather than make it 3 times as long, it actually repeats the vector three times,
    # probably so as to, as said above, increase activity in those cells and aid learning. 
    # Good old repartition. In which case, I'm not sure I want to use this in my tests...
    for i in range(3): 
        inputVector.extendVector(originalInputVector)
    
    # Get a non-local variable and feed it to a local one for local manipulation.
    desiredLocalActivity = DESIRED_LOCAL_ACTIVITY
    
    # This sets up a new region, called newRegion,
    # a variable called ouputVector, which calls a method to find just that,
    # and a variable for the number of correct prodicitons, initialised as 0. 
    newRegion = Region(rows,cols,inputVector,coverage,desiredLocalActivity)
    outputVector = newRegion.getOutputVector()
    correctBitPredictions = 0
    
    robot = Robot()
    starting_position = robot.sonarReading()
    robot.move()
 

    # This is where the action starts. This loop forms the main body of the test.
    # For every time round, an input is given, the CLA updates spacial and temporal 
    # poolers with this new input and an output is found.    
    for round in range(numRounds): 
        if state == "Kill Switch: Engage!":
            break
        end_this_round = False
        stuck_counter = 0
        print state
        round_number = round+1
        print ("Round: %d" % round_number) # Prints the number of the round
            #printStats(inputString, currentPredictionString)
        robot.move()
        
        while end_this_round is False:            
            val = robot.sonarReading()
            print ("Sonar: %d cm" % val)
            sonarPositionResults.append(robot.currentSonarReading)
            setInput(originalInputVector,val) # These next few lines convert the inputs and outputs from integers to bitstrings,
            inputString = inputVector.toString() # so that the CLA can handle them.
            outputString = outputVector.toString()
             #print(originalInputVector.toString())
                  
       	  #for bit in originalInputVector.getVector():
       	  #print(bit.bit)
       	  #print('')
       	  #print(inputString)       
       
            if outputString in predictions: # If output string has been seen before, 
                currentPredictionString = predictions[outputString] 
                # summon the last input that caused that prediction and make it the "currentPredictionString"? That's confusing...
            else:
                currentPredictionString = "[New input]" # If not seen before, 
            predictions[outputString] = inputString # Update the i/o record with the new relationship 
                            
            #if (round > trainingRounds): 
            correctBitPredictions += stringOverlap(currentPredictionString, predictions[outputString]) 
            #    without training rounds, stringOverlap will be trying to compare binary stings with the string 'New input'. So correct BitPredictions is going to be 0 for a while,
            #    until inputs start repeating.
                
            newRegion.runCLA() # The CLA bit!
            numRuns += 1
            
            #printColumnStats(newRegion) 
            accuracy = float(correctBitPredictions)/float(30*numRuns) 
            # Times thirty becuase it's measuring the correct prediction of BITS not whole bit-strings, and there are 30 bits per input.
            # This makes sense as bits have semantic meaning where as bit-strings dont!
            accuracies.append(accuracy)
            
            if robot.killSwitch() == True: # This will terminate all loops and move to the end of the program
                end_this_round = True
                state = "Kill Switch: Engage!"
                print state
            if state == "Going Forwards":
                if robot.currentSonarReading <= minimum_distance: 
                    stuck_counter += 1
                if stuck_counter == 2:     # This routine confirms that a wall is hit, then sends the robot back to the start position
                    robot.stop()             
                    print "Stuck Reflex"
                    state = "Reversing"
                    print state
                    stuck_counter = 0
                    robot.move(-75)
            if state == "Reversing":                   
                if (starting_position-3) < robot.currentSonarReading < (starting_position+3): # Clean this up
                    state = "Going Forwards"                    
                    end_this_round = True
                    
                
                
           
 
     
     # With the experiment now over, stat summaries are now printed. 
#    for key in predictions:
#        print("key: " + key + " predictions: " + predictions[key])
    robot.stop()    
    #print("Accuracy: " + str(float(correctBitPredictions)/float(30*(numRounds-trainingRounds))))
    
    #code below prints a graph of runs against accuracies
    runs = np.arange(1, numRuns, 1)
    plt.figure(1)
    plt.subplot(211)
    plt.grid(True)
    plt.plot(runs, accuracies)
    plt.plot(runs, accuracies, 'bo')
    plt.ylabel('Accuracy (correct preditions/predictions)')
    plt.title('Change in CLA accuracy of sonar position prediction')
    plt.subplot(212)
    plt.grid(True)
    plt.plot(runs, sonarPositionResults, 'r-')
    plt.plot(runs, sonarPositionResults, 'ro')
    plt.ylabel('Sonar Readings (cm)')
    plt.xlabel('Number of CLA runs')
    plt.show()

def stringOverlap(str1,str2):
    count = 0
    length = min(len(str1),len(str2)) # Returns the length of the smallest string
    for i in range(length):           # For the length of the smallest string, compare the bits
        if (str1[i] == str2[i]):    # If bits are equal, increment 'count'. 
            count += 1
    return count                     # Returns the number of bits in two strings which are the same. 


def printStats(inputVector,outputVector): # Does what it says in the name. 
    #print('Input-: ',end='')
    print('Input-:')
    print(inputVector)
    #print('Output: ',end='')
    print('Output-: ')
    print(outputVector)


def setInput(inputVector,bitArray): # Turns numbers into binary strings
    for i in range(inputVector.getLength()):
        bitValue = (bitArray & (1 << i) > 0)
        inputVector.getBit(i).setActive(bitValue)
        #print inputVector.toString()


def printColumnStats(region): # Called once on, or about, line 65
    alarmColumnCount = 0
    stableColumnCount = 0
    errorColumnsFound = 0
    for c in region.columns:
        if (not c.isActive()):
            continue
        allCellsActive = True
        cellActiveFound = False
        for cell in c.cells:
            if (not cell.isActive(CURRENT_TIME_STEP)):
                allCellsActive = False
            else:
                cellActiveFound = True
            if allCellsActive:
                alarmColumnCount += 1
            elif cellActiveFound:
                stableColumnCount += 1
            else:
                errorColumnsFound += 1
        print("Alarm Columns: " + str(alarmColumnCount) + " Stable Columns: " + str(stableColumnCount))


print("Searching for robot...")
experiment() 
# This is the only bit that really executes. Everythig else is just a method. The test count method calls all the others.
