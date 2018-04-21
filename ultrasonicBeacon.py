import time
import serial
import re
#import pandas

ser = serial.Serial(port='/dev/ttyACM0',baudrate = 9600,parity=serial.PARITY_NONE,stopbits=serial.STOPBITS_ONE,bytesize=serial.EIGHTBITS,timeout=1)
WINDOW = 5
LEGNTH = 30
sensorList1 = []
sensorList2 = []

def readSerial():
  global sensorList1 
  global sensorList2 
  x=ser.readline()
  data = x.decode()
  results = re.split('[+ \r \n]',data)
  try:
    sensorList1.append(int (results[0]))
    sensorList2.append(int (results[1]))
  except ValueError:
    print ("********")
    
  sensorList1 = sensorList1[-1*LEGNTH:]
  sensorList2 = sensorList2[-1*LEGNTH:]

  
def signalProcessing():
  global sensorList1
  global sensorList2
  #moving average filter
  if len(sensorList1) > WINDOW:
    sensorList1[-1] = sum (sensorList1[-1*WINDOW:])/WINDOW
    sensorList2[-1] = sum (sensorList2[-1*WINDOW:])/WINDOW
  
def convertToDistance():
  global sensorList1
  global sensorList2
  dist1 = sensorList1[-1]
  dist2 = sensorList2[-1]
  print (str(dist1) + " cm from sensor1")
  print (str(dist1) + " cm from sensor2")
  
def main ():
  while(True):
    readSerial()
    signalProcessing()
    convertToDistance()
  
main ()
  
