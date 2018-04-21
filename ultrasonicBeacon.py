import time
import serial
ser = serial.Serial(port='/dev/ttyACM0',baudrate = 9600,parity=serial.PARITY_NONE,stopbits=serial.STOPBITS_ONE,bytesize=serial.EIGHTBITS,timeout=1)
WINDOW = 5
LEGNTH = 50


def readSerial():
  sensorList1 = []
  sensorList2 = []
  x=ser.readline()
  data = x.decode("utf-8")
  data.split(',')
  sensorList1.append(data[0])
  sensorList2.append(data[1])
  sensorList1 = sensorList[-Length:]
  sensorList2 = sensorList[-Length:]
  
  return sensorList1, sensorList2


def main ():
  sensorList1, sensorList2 = readSerial()
  print (sensorList1)
  print (sensorList2)
  
main ()
  
