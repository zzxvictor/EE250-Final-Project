import sys
import paho.mqtt.client as mqtt
import time
import grovepi
import grove_rgb_lcd 
#from pynput import keyboard

def lcdCallBack(client, userdata, message):
   grove_rgb_lcd.setText(str(message.payload,"utf-8"))
   #print ("sdf")


def ledCallBack(client, userdata, message):
    #----------------------
    #depends on which port is being used
    led = 2
    #----------------------
    msg = str(message.payload, "utf-8")
    if msg == "LED_ON":
        grovepi.digitalWrite(led, 1)

    elif msg == "LED_OFF":
        grovepi.digitalWrite(led, 0)

def on_connect(client, userdata, flags, rc):
    print("Connected to server (i.e., broker) with result code "+str(rc))
    client.subscribe("anrg-pi1/lcd")
    client.subscribe("anrg-pi1/led")
    client.subscribe("anrg-pi1/ultrasonicRanger")
    client.subscribe("anrg-pi1/button")
    client.message_callback_add("anrg-pi1/led", ledCallBack)
    client.message_callback_add("anrg-pi1/lcd", lcdCallBack)
    
    #client.message_callback_add("anrg-pi1/ultrasonicRanger", ultraCallBack)
    
    
    #subscribe to topics of interest here

#------------------------------------------------------------------------
#three call back functions need to be implemented!!!



#def ultraCallBack(client, userdata, message):
    #----------May have bugs---------------
 #   message = ultrasonicRead(ultrasonic_ranger)
  #  client.publish("anrg-pi1/ultrasonicRanger", 'ultrasonic sensor: ' + str(message))
    #--------------------------------------
#---------------------------------------------------------------------------
def on_message(client, userdata, msg):
    print("on_message: " + msg.topic + " " + str(msg.payload))

if __name__ == '__main__':
    #this section is covered in publisher_and_subscriber_example.py
    button = 7
    button_val =  grovepi.digitalRead(button)
    grove_rgb_lcd.setRGB(0,64,128)

    client = mqtt.Client()
    client.on_message = on_message
    client.on_connect = on_connect
    client.connect(host="eclipse.usc.edu", port=11000, keepalive=60)
    client.loop_start()
    while True:
        #print("delete this line")

        if button_val != grovepi.digitalRead(button):
            client.publish("anrg-pi1/button", "Button Pressed!")
        message = grovepi.ultrasonicRead(8)
        client.publish("anrg-pi1/ultrasonicRanger", 'ultrasonic sensor: ' + str(message))
        time.sleep(1)
            
