import time
import serial
import re
import sys
import paho.mqtt.client as mqtt

ser = serial.Serial(port='/dev/ttyACM0',baudrate = 19200,parity=serial.PARITY_NONE,stopbits=serial.STOPBITS_ONE,bytesize=serial.EIGHTBITS,timeout=1)
flag = 0
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


def on_connect(client, userdata, flags, rc):
    print("Connected to server (i.e., broker) with result code "+str(rc))
    client.subscribe("anrg-pi1/lcd")
    client.message_callback_add("anrg-pi1/lcd", commandCallBack)
    
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
  #print (results)
  try:
   sensorList1.append(int (results[0]))
   sensorList2.append(int (results[1]))
  except ValueError:
   return 
   
  
def signalProcessing():
  global sensorList1
  global sensorList2
  if len(sensorList1) != 0 and len(sensorList2) !=0:
   print (sensorList1[-1])
   print (sensorList2[-1])
  
  
def main ():
  global flag
  client = mqtt.Client()
  client.on_message = on_message
  client.on_connect = on_connect
  client.connect(host="eclipse.usc.edu", port=11000, keepalive=60)
  client.loop_start()
  while(True):
    if flag == 1:
         readSerial()
         signalProcessing()

    
main ()
  
