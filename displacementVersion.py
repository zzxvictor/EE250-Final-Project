"""
this code is for EE250 Final project 
Author: Zixuan Zhang 
Main functionality:
	receive data from arduino 
	process the data and convert the displacement into movement signals
	transmite the data to the pololu robot


Major Bugs:
	sreial port connection is not always stable, sometimes the code captures garbish data
	the code is not really sensitive and accurate due to the low quality of the sensor/ noisy environment 

April 30 2018
"""
import time
import serial
import re
import sys
import paho.mqtt.client as mqtt
import matplotlib.pyplot as mp
import numpy as np
#serial port configuration
#buad rate 9600
ser = serial.Serial(port='/dev/ttyACM0',baudrate = 9600,parity=serial.PARITY_NONE,stopbits=serial.STOPBITS_ONE,bytesize=serial.EIGHTBITS,timeout=1)

#declare global variables
flag = 0 # flag for start/stop
replay = 0 #flag for replay
WINDOW = 30 #size of the window 
sensorList1 = [] #store the data from the first sensor 
sensorList2 = [] #store the data from the second sensor 
oX = 0
oY = 0
#call back function for start/stop
def commandCallBack(client, userdata, message):
   global flag 
   msg = str(message.payload, "utf-8")
   print ("command received")
   if (msg== 'start'):
      flag = 1
   elif (msg == 'end'):
      flag = 0

#call back function for setting origin, unused 
def originCallBack (client, userdata, message):
   global sensorList1 
   global sensorList2
   global oX
   global oY
   global WINDOW
   msg = str(message.payload, "utf-8")
   if (msg == 'set'):
      if len(sensorList1) == WINDOW and len(sensorList2) == WINDOW:
         oX = sum(sensorList1)/WINDOW
         oY = sum(sensorList2)/WINDOW
         print (oX)
         print (oY)
         print ("origin set")
         

#call back function for replaying 
def replayCallBack(client, userdata, message):
  global replay 
  msg = str(message.payload, "utf-8")
  print ("command received")
  if msg == 'show':
    print ("replay ")
    replay = 1
  else:
    replay = 0


#MQTT configuration 
def on_connect(client, userdata, flags, rc):
    print("Connected to server (i.e., broker) with result code "+str(rc))
    client.subscribe("pololu-13/record")
    client.subscribe("pololu-13/origin")
    client.subscribe("pololu-13/move")
    client.subscribe("pololu-13/replay")

    client.message_callback_add("pololu-13/record", commandCallBack)
    client.message_callback_add("pololu-13/origin", originCallBack)
    client.message_callback_add("pololu-13/replay", replayCallBack)
    
def on_message(client, userdata, msg):
    print("on_message: " + msg.topic + " " + str(msg.payload))

#read one single line from serial port, split the data into four segements
#only the first two are used 
def readSerial():
  global sensorList1 
  global sensorList2 
  results = []
  #read the serial port
  x=ser.readline()
  
  #try to decode the message, converting it from bytes code to strings
  try:
   data = x.decode ("ascii")
  except UnicodeDecodeError:
   print ('error0')
   return 

  #split the data 
  try:
   results = re.split('[+ \r \n]',data)
   if len(results) != 4:
   	return
  except ValueError:
   print('error1')
   return 

  #try to store the data correspondingly 
  try:
   sensorList1.append(int (results[0]))
   sensorList1 = sensorList1[-1*WINDOW:]
  except ValueError:
   print('error2')
   return 
	#try to store the data correspondingly
  try:
   sensorList2.append(int (results[1]))
   sensorList2 = sensorList2[-1*WINDOW:]
  except ValueError:
   print('error2')
   return 
   
def recording():
  global flag 
  global sensorList1
  global sensorList2
  global WINDOW
  print ("recording:")
  while flag == 1:
    print ('.')
    readSerial()
    

  xFinal = sum(sensorList1)/WINDOW
  yFinal = sum(sensorList2)/WINDOW
  return xFinal, yFinal

def calculateRoute(xFinal, yFinal):
  global oX, oY
  motionX = []
  motionY = []
  timeX = []
  timeY = []

  xDisplacement = xFinal - oX
  yDisplacement = yFinal - oY
  if xDisplacement > 0:
    motionX.append('w')
  elif xDisplacement < 0:
    motionX.append('s')
    xDisplacement = -1*xDisplacement
  timeX.append(int(xDisplacement))

  if yDisplacement>0:
    motionY.append('a')
  elif yDisplacement<0:
    motionY.append('d')
    yDisplacement = -1*yDisplacement
  timeY.append(int (yDisplacement))

  return motionX, motionY, timeX, timeY

#send data through MQTT using format:   angle+times
def sendData(motionX, motionY, timeX, timeY, client ):
  if len(motionX) > 0 and len(motionY) > 0:
    command = ( str(motionX[0]) + str(timeX[0]) )
    client.publish("pololu-13/move", command)
    command =  ( str(motionY[0]) + str(timeY[0]) )
    client.publish("pololu-13/move", command)





  
def main ():
  #MQTT configuration
  global replay
  global flag
  global oX
  global oY
  client = mqtt.Client()
  client.on_message = on_message
  client.on_connect = on_connect
  client.connect(host="eclipse.usc.edu", port=11000, keepalive=60)
  client.loop_start()
  while True:
  	#start recording 
    if flag == 1:
      discard = 30
      for i in range (discard + WINDOW):
        readSerial()
      xFinal, yFinal = recording()
      print (xFinal- oX)
      print (yFinal -oY)
    if flag == 0 and replay == 1:
      motionX,motionY, timeX, timeY = calculateRoute(xFinal, yFinal)
      sendData(motionX,motionY, timeX, timeY, client)
      xFinal = 0
      yFinal = 0
      motionX = []
      motionY = []
      timeX = []
      timeY = []
      replay = 0
      





#run the code 
main ()
