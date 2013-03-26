#!/usr/bin/python
from region import Region
from config import *
from inputbit import InputVector
import nxt.locator
from nxt.sensor import*   

brick = nxt.locator.find_one_brick()

def testCount():
	rows = 5
	cols = 5
	coverage = 20
	numbits = 10
	numRounds = 500
	trainingRounds = numRounds/4
	originalInputVector = InputVector(numbits)
	inputVector = InputVector(0)

	predictions = dict()
	#repeat several times to increase activity:
	for i in range(3):
		inputVector.extendVector(originalInputVector)

	desiredLocalActivity = DESIRED_LOCAL_ACTIVITY

	newRegion = Region(rows,cols,inputVector,coverage,desiredLocalActivity)
	outputVector = newRegion.getOutputVector()
	correctBitPredictions = 0
 
	for round in range(numRounds): # This test executes the CLA for a set number of rounds. 
     
		#print("Round: " + str(round))
		# if (round % 2 == 0):
		# 	val = 682
		# else:
		# 	val = 341
		val = Ultrasonic(brick, PORT_1).get_sample()
		setInput(originalInputVector,val)
		inputString = inputVector.toString()
		outputString = outputVector.toString()
		#print(originalInputVector.toString())
           
		#for bit in originalInputVector.getVector():
		# 	print(bit.bit)
		# print('')
		# print(inputString)


		if outputString in predictions:
			currentPredictionString = predictions[outputString]
		else:
			currentPredictionString = "[New input]"
			pred[outputString] = inputString # I'm sure this should be indented like this...
		print("Round: %d" % round) # Prints the number of the round
		printStats(inputString, currentPredictionString)
		if (round > trainingRounds):
			correctBitPredictions += stringOverlap(currentPredictionString, predictions[outputString])
				 

		newRegion.doRound()
		printColumnStats(newRegion)
	for key in predictions:
		print("key: " + key + " predictions: " + predictions[key])

	print("Accuracy: " + str(float(correctBitPredictions)/float((30*(numRounds-trainingRounds)))))


def stringOverlap(str1,str2):
	count = 0
	length = min(len(str1),len(str2)) # Returns the length of the smallest string
	for i in range(length):           # For the length of the smallest string, compare the bits
		if (str1[i] == str2[i]):    # If bits are equal, increment 'count'. 
			count += 1
	return count                     # Returns the number of bits in two strings which are the same. 


def printStats(inputVector,outputVector):
	#print('Input-: ',end='')
      print('Input-:')
      print(inputVector)
      #print('Output: ',end='')
      print('Output-: ')
      print(outputVector)


def setInput(inputVector,bitArray):
	for i in range(inputVector.getLength()):
		bitValue = (bitArray & (1 << i) > 0)
		inputVector.getBit(i).setActive(bitValue)


def printColumnStats(r):
	alarmColumnCount = 0
	stableColumnCount = 0
	errorColumnsFound = 0
	for c in newRegion.columns:
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

# debug main run
print("Running!")
testCount()
