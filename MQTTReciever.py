import sys
import paho.mqtt.client as mqtt
import time


def lcdCallBack(client, userdata, message):
   print ("lcd Message received")


def ledCallBack(client, userdata, message):
   print ("led message received")

def on_connect(client, userdata, flags, rc):
    print("Connected to server (i.e., broker) with result code "+str(rc))
    client.subscribe("anrg-pi1/lcd")
    client.subscribe("anrg-pi1/led")
    client.subscribe("anrg-pi1/ultrasonicRanger")
    client.subscribe("anrg-pi1/button")
    client.message_callback_add("anrg-pi1/led", ledCallBack)
    client.message_callback_add("anrg-pi1/lcd", lcdCallBack)
    
def on_message(client, userdata, msg):
    print("on_message: " + msg.topic + " " + str(msg.payload))

if __name__ == '__main__':

    client = mqtt.Client()
    client.on_message = on_message
    client.on_connect = on_connect
    client.connect(host="eclipse.usc.edu", port=11000, keepalive=60)
    client.loop_start()
    while True:
        time.sleep(1)
            
