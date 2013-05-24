# -*- coding: utf-8 -*-
"""
Created on Fri May 10 22:30:52 2013

It works!

A version of forward_test5.py but in class form. 

A class for files like test2.py and experiment1.py to call sensory information from. 

@author: benjamin
"""


from nxt.motor import Motor, PORT_A, PORT_C, SynchronizedMotors
from nxt.sensor import Ultrasonic, PORT_1, Touch, PORT_4
import nxt.locator
import string

class Robot(object):
    def __init__(self):
                     
        self.brick = nxt.locator.find_one_brick()
        self.left = Motor(self.brick, PORT_C)
        self.right = Motor(self.brick, PORT_A)
        self.tracks = SynchronizedMotors(self.left, self.right, 0)
        self.scale_factor = 0.1 # A factor for reducing the size of input measurements
        self.motorZero = [0,0] # An array for resetting the motor readings.
        
        self.currentMotorPosition = [0,0] 
        self.previousMotorPosition = [0,0]
        self.currentMotorVelocity = [0,0] 
        self.previousMotorVelocity = [0,0] 
        self.currentMotorAcceloration = [0,0] 
        
        self.currentSonarReading = 0 
        self.previousSonarReading = 0
        self.currentSonarVelocity = 0 
        self.previousSonarVelocity = 0  
        self.currentSonarAcceloration = 0
        
    def resetMotors(self):
        self.motorZero = self.motorPosition()
    
    """ Static Afferents """
    # This function is rediculously over complicated! It stems from the fact that the NXT library is a mess and is therefore
    # not my fault!
    
    def motorPosition(self):
        get_motor = str(self.tracks.get_tacho()) # Gets motor readings in the string form: 'tacho: ' + t1 + ' ' + t2
        motor_strings = string.split(get_motor) # Splits string into array form ['tacho: ', 't1', 't2']
        
        motor_reading = [] # new array
        motor_reading.append(int( float(motor_strings[1])*self.scale_factor - self.motorZero[0] )) # Turns 't1' back into an integer and appends to new array
        motor_reading.append(int( float(motor_strings[2])*self.scale_factor - self.motorZero[1] )) # Turns 't2' back into an integer and appends to new array   
        
        self.previousMotorPosition = self.currentMotorPosition # updating the motor record
        self.currentMotorPosition = motor_reading
        return motor_reading
        
    def sonarReading(self):
        x = Ultrasonic(self.brick, PORT_1).get_sample()
        self.previousSonarReading = self.currentSonarReading
        self.currentSonarReading = x
        return x
        
    def killSwitch(self):
        touch = Touch(self.brick, PORT_4).get_sample()
        return touch
    
    """ Dynamic Afferents """
    # These next two functions do EXACTLY the same thing, but have different names. I belive that this makes the code lower
    # down, where they are called, more readable, so I've decided to keep them seperate. 
       
    def motorVelocity(self, time_interval): # Claculates change in position over time. 
        xdot = []
        xdot.append(int( (self.currentMotorPosition[0]-self.previousMotorPosition[0]) /time_interval )) 
        xdot.append(int( (self.currentMotorPosition[1]-self.previousMotorPosition[1]) /time_interval ))
        self.previousMotorVelocity = self.currentMotorVelocity
        self.currentMotorVelocity = xdot
        return xdot
        
    def motorAcceloration(self, time_interval): # Claculates the change in velocity over time.
        xdotdot = []
        xdotdot.append(int( (self.currentMotorVelocity[0]-self.previousMotorVelocity[0]) / time_interval ))
        xdotdot.append(int( (self.currentMotorVelocity[1]-self.previousMotorVelocity[1]) / time_interval ))
        self.currentMotorAcceloration = xdotdot
        return xdotdot      
        
    def sonarVelocity(self, time_interval): # Claculates change in position over time. 
        xdot = int( (self.currentSonarReading-self.previousSonarReading) /time_interval )
        self.previousSonarVelocity = self.currentSonarVelocity
        self.currentSonarVelocity = xdot
        return xdot
      
    def sonarAcceloration(self, time_interval): # Claculates the change in velocity over time.
        xdotdot = int( (self.currentSonarVelocity-self.previousSonarVelocity) / time_interval )
        self.currentSonarAcceloration = xdotdot
        return xdotdot
        
    """ Motor Efferents """
    
    def move(self, power=75):
        self.tracks.run(power) # Takes +ve and -ve values =)
        
    def stop(self):
        self.tracks.idle()
        
#    """ Reflex Actions """
#
#    NOT WORKING SO WELL.
#
#import threading
#        
#class Reflex(threading.Thread):    
#    def __init__(self):
#        threading.Thread.__init__(self)
#        self.brick = nxt.locator.find_one_brick()
#
#    def run(self):
#        global killState 
#        killState = False
#        touch = Touch(self.brick, PORT_4).get_sample()
#        if touch == True:
#            killState = True
#        print touch
        
        
        













