import time
import serial
import re
import sys
import paho.mqtt.client as mqtt
import matplotlib.pyplot as mp
ser = serial.Serial(port='/dev/ttyACM0',baudrate = 9600,parity=serial.PARITY_NONE,stopbits=serial.STOPBITS_ONE,bytesize=serial.EIGHTBITS,timeout=1)
flag = 0
replay = 0
WINDOW = 60

temp1 = []
temp2 = []

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


def signalProcessing():
  global temp1
  global temp2 
  results = []
  x=ser.readline()
  print (len(x))
  #print (x)
  try:
   data = x.decode ()
   print (data)
  except UnicodeDecodeError:
   print ('error0')
   return 
  try:
   results = re.split('[+ \r \n]',data)
   if len(results) != 4:
    return
  except ValueError:
   print('error1')
   return 
  try:
   temp1.append(int (results[0]))

  except ValueError:
   print('error2')
   return 

  try:
   temp2.append(int (results[1]))

  except ValueError:
   print('error2')
   return 
   

  
def main ():
  #MQTT configuration
  global replay
  global flag
  global temp1
  global temp2
  client = mqtt.Client()
  client.on_message = on_message
  client.on_connect = on_connect
  client.connect(host="eclipse.usc.edu", port=11000, keepalive=60)
  client.loop_start()
  xx = 0
  while True:
    if (flag == 1):
      
      xx = 1
      signalProcessing()
    elif xx == 1:
      temp1 = temp1[40:]
      temp2 = temp2[40:]
      print (temp1)
      print (temp2)
      mp.plot(temp1)
      mp.plot(temp2)
      mp.show()
      xx = 0
      temp1 = []
      temp2 = []

 

    

main ()