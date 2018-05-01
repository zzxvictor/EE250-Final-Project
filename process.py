import time
import serial
import re
import sys
import paho.mqtt.client as mqtt

ser = serial.Serial(port='/dev/ttyACM0',baudrate = 19200,parity=serial.PARITY_NONE,stopbits=serial.STOPBITS_ONE,bytesize=serial.EIGHTBITS,timeout=1)
flag = 0
replay = 0
WINDOW = 60
sensorList1 = []
sensorList2 = []


def commandCallBack(client, userdata, message):
   global flag 
   msg = str(message.payload, "utf-8")
   print ("command received")
   if (msg== 'start'):
      flag = 1
   elif (msg == 'end'):
      flag = 0


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

def replayCallBack(client, userdata, message):
  global replay 
  msg = str(message.payload, "utf-8")
  print ("command received")
  if msg == 'show':
    print ("replay ")
    replay = 1
  else:
    replay = 0



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


def readSerial():
  global sensorList1 
  global sensorList2 
  results = []
  x=ser.readline()
  #print (x)
  try:
   data = x.decode ("ascii")
  except UnicodeDecodeError:
   return 
  try:
   results = re.split('[+ \r \n]',data)
  except ValueError:
   return 

  try:
   sensorList1.append(int (results[0]))
   sensorList2.append(int (results[1]))
   sensorList1 = sensorList1[-1*WINDOW:]
   sensorList2 = sensorList2[-1*WINDOW:]
  except ValueError:
   return 
   
  
def motionDetectX():
  global sensorList1
  if len (sensorList1) == WINDOW:
    deviat = sum(sensorList1[-10:]) - sum(sensorList1[0:10])
    if deviat > 70:
      return 'W'
    elif deviat < -70:
      return 'S'
    else:
      return '*'

def motionDetectY():
  global sensorList2
  if len (sensorList2) == WINDOW:
    deviat = sum(sensorList2[-10:]) - sum(sensorList2[0:10])
    if deviat > 70:
      return 'A'
    elif deviat < -70:
      return 'D'
    else:
      return '*'
      """
  if len(sensorList1) == WINDOW:
  	deviat = sum(sensorList1[-20:]) - sum(sensorList1[0:20])
  	if deviat > 200:
  		print ("W")
  		print (deviat)
  		client.publish("pololu-13/move",'w')
  	elif deviat < -200:
  		print ("S")
  		print (deviat)
  		client.publish("pololu-13/move",'s')
  	else:
  		print ("------------")"""
def signalProcessing():
  global flag
  xMotionList = []
  yMotionList = []
    #recording
  while (flag == 1):
    readSerial()
    xMotionList.append(motionDetectX())
    yMotionList.append(motionDetectY())
    #feature extraction
  print (xMotionList)
  print (yMotionList)
  return xMotionList , yMotionList

  
def featureExtraction(xMotionList, yMotionList):
  counter = 0
  timeFeature = []
  motionFeature = []
  for i in range (len (xMotionList)):
  	item = getDirection(xMotionList[i],yMotionList[i])
  	if item != None:
  		motionFeature.append(item)
  print ('------------------------------------------------------')
  print (motionFeature)
  print ('------------------------------------------------------')
  """
  for i in range (len (xMotionList)):
  	if xMotionList[i] != None and yMotionList[i] != None:
  		temp = getDirection(xMotionList[i], yMotionList[i])

  for i in range (len (xMotionList)):
  	item = getDirection(xMotionList[i], yMotionList[i])
  	if item == None:
  		next
  	elif item == temp:
  		counter+=1
  	else:
  		if counter > 4:
  			timeFeature.append(counter)
  			motionFeature.append(temp)
  			temp = item
  			counter = 0
  		else:
  			counter = 0

"""
  """
  for item in  xMotionList:
    if item != None:
      temp = item
      break

  for item in xMotionList:
    if item == None:
      next
    elif item == temp:
      counter +=1
    else:
      if counter > 10:
        timeFeature.append(counter)
        motionFeature.append(temp)
      temp = item
      counter = 0
"""

  print (motionFeature)
  print (timeFeature)


def getDirection(x, y):
	if x == 'W' and y == 'A':
		return 'Q'
	elif x == 'W' and y == 'D':
		return 'E'
	elif x == 'S' and y == 'A':
		return 'Z'
	elif x == 'S' and y == 'D':
		return 'C'
	elif x == '*' and y == '*':
		return '*'
	elif x == '*':
		return y
	elif y == '*':
		return x
	elif x == None or y == None:
		return None
	else:
		return '0'
  
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
    if (flag == 1):
      xMotion, yMotion = signalProcessing()
    if replay ==1:
      replay = 0
      featureExtraction(xMotion, yMotion)
      


main ()
