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
   msg = str(message.payload, "utf-8")
   if (msg == 'set'):
      if len(sensorList1) != 0 and len(sensorList2) !=0:
         oX = sensorList1[-1]
         oY = sensorList2[-1]
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
   
 
#calculate the movement on x axis, reurn the displacment 
def motionDetectX():
  global sensorList1
  if len (sensorList1) == WINDOW:
  	#use window as a whole instead of using single element, more stable and accurate
    deviat = sum(sensorList1[-10:]) - sum(sensorList1[0:10])

    #threshold 
    if deviat > 50:
      return deviat/10
    elif deviat < -50:
      return deviat/10
    else:
      return 0

#calculate the movement on y axis, reurn the displacment 
def motionDetectY():
  global sensorList2
  if len (sensorList2) == WINDOW:
    deviat = sum(sensorList2[-10:]) - sum(sensorList2[0:10])
    if deviat > 50:
      return deviat/10
    elif deviat < -50:
      return deviat/10
    else:
      return 0

#convert displacement into angle 
def getDirection(x, y):
	if x == 0:
		if y > 0:
			return 0
		elif y < 0 :
			return -180
		else:
			return '*'
	angle = np.arctan(y/x) * 180 / 3.1415
	if x<0 and y<0:
		angle = -180 + angle
	elif x<0 and y >= 0:
		angle = 180 + angle 

	return angle

#discard the first 40 elements due to bad connection/synchronization at the very beginning 
def signalProcessing():
  global flag
  xMotionList = []
  yMotionList = []
    #recording
  counter = 0
  while (flag == 1):
    readSerial()
    if counter > 70:
    	print ("recording")
    	#add the displacement to the lists
    	xMotionList.append(motionDetectX())
    	yMotionList.append(motionDetectY())
    counter += 1
    #feature extraction

  # plot the displacement
  print ("ploting ")

  mp.plot(xMotionList)
  mp.plot(yMotionList)
  mp.show()

  return xMotionList , yMotionList

 
#extract the features 
def featureExtraction(xMotionList, yMotionList):
  counter = 0
  merge = []
  timeFeature = []
  motionFeature = []

  #merge the two lists into one list, converting displacements into angle

  for i in range (len (xMotionList)):
  	item = getDirection(xMotionList[i],yMotionList[i])
  	if item != None:
  		merge.append(item)
  print ('------------------------------------------------------')
  print (merge)
  print ('------------------------------------------------------')
  temp = merge[0]

  #shrink the data
  #instead of having [1,1,1,1,1,1,1], the data now has [1], [6]//angle = 1, occurred 6 times 
  for i in range (len(merge) - 1):
  	if temp == merge[i+1]:
  		counter += 1
  	else:
  		motionFeature.append(temp)
  		timeFeature.append(counter)
  		counter = 0
  		temp = merge[i + 1]
  motionFeature.append(temp)
  timeFeature.append(counter)

  print ("********************************")
  #print the data 
  print (motionFeature)
  print (timeFeature)
  
  print ("********************************")
  return motionFeature, timeFeature

#send data through MQTT using format:   angle+times
def sendData(motion, time, client ):
	for i in range (len (motion) ):
		command = str(motion[i]) + ',' + str(time[i])
		client.publish("pololu-13/move", command)




  
def main ():
  #MQTT configuration
  global replay
  global flag
  client = mqtt.Client()
  client.on_message = on_message
  client.on_connect = on_connect
  client.connect(host="eclipse.usc.edu", port=11000, keepalive=60)
  client.loop_start()
  while True:
  	#start recording 
    if (flag == 1):
      xMotion, yMotion = signalProcessing()

    #start replaying 
    if replay ==1:
      replay = 0
      #delete the data from previous run 
      motion = []
      time = []
      motion, time = featureExtraction(xMotion, yMotion)
      sendData(motion, time, client )
      





#run the code 
main ()
