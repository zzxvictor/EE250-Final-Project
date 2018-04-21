import time
import serial
import re
import pandas

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
  sensorList1 = pandas.rolling_mean(sensorList1, WINDOW)
  sensorList2 = pandas.rolling_mean(sensorList2, WINDOW)
  
  

def main ():
  while(True):
    readSerial()
    signalProcessing()
    
  
main ()
  
