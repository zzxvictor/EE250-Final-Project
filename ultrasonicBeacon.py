import time
import serial
import re
import sys
import paho.mqtt.client as mqtt

ser = serial.Serial(port='/dev/ttyACM0',baudrate = 9600,parity=serial.PARITY_NONE,stopbits=serial.STOPBITS_ONE,bytesize=serial.EIGHTBITS,timeout=1)
WINDOW = 1
LEGNTH = 30
sensorList1 = []
sensorList2 = []

def commandCallBack(client, userdata, message):
   print ("command received")


def on_connect(client, userdata, flags, rc):
    print("Connected to server (i.e., broker) with result code "+str(rc))
    client.subscribe("anrg-pi1/lcd")
    client.message_callback_add("anrg-pi1/led", commandCallBack)
    
def on_message(client, userdata, msg):
    print("on_message: " + msg.topic + " " + str(msg.payload))

def readSerial():
  global sensorList1 
  global sensorList2 
  results = []
  x=ser.readline()
  print (x)
  data = x.decode ()
  print (data)
  results = re.split('[+ \r \n]',data)
  print (results)
"""
  try:
   data = x.decode()
   results = re.split('[+ \r \n]',data)
   print (results)
  except UnicodeDecodeError:
   print ("*********")
   
  try:
      sensorList1.append(int (results[0]))
      sensorList2.append(int (results[1]))
  except ValueError:
      print ("******") 
  
  sensorList1 = sensorList1[-1*LEGNTH:]
  sensorList2 = sensorList2[-1*LEGNTH:]"""

  
def signalProcessing():
  global sensorList1
  global sensorList2
  print (sensorList1)
  print (sensorList2)
  
def convertToDistance():
  global sensorList1
  global sensorList2
  dist1 = sensorList1[-1]
  dist2 = sensorList2[-1]
  print (str(dist1) + " cm from sensor1")
  print (str(dist2) + " cm from sensor2")
  print ("____----------------------------____")
  
def main ():
  client = mqtt.Client()
  client.on_message = on_message
  client.on_connect = on_connect
  client.connect(host="eclipse.usc.edu", port=11000, keepalive=60)
  client.loop_start()
  while(True):
    readSerial()
    signalProcessing()
    
main ()
  
