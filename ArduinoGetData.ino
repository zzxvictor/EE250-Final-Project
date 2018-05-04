
// These constants won't change. They're used to give names to the pins used:
const int analogInPin1 = A0;  // Analog input pin that the potentiometer is attached to
const int analogInPin2 = A1;  // Analog input pin that the potentiometer is attached to


int sensorValue1 = 0;        // value read from the pot
int sensorValue2 = 0;        // value output to the PWM (analog out)

float Vscale = 5.05 / 1023;


int historyLog1[6] = {};
int historyLog2[6] = {};

int flag = 0;
int WINDOW = 6;

int original1 = 0;
int original2 = 0;
int counter1 = 100;
int counter2 = 200;

void setup() 
{  
  Serial.begin(9600);
}

void loop() 
{

 for (int i = 0; i<WINDOW; i++)
 {
    if (i < WINDOW-1)
    {   
        historyLog1[i] = historyLog1[i+1];
        historyLog2[i] = historyLog2[i+1];
    }
    else
    {
        int temp1 = analogRead(analogInPin1);
        int temp2 = analogRead(analogInPin2);
        
        if (  (temp1 < original1 - 40)||(temp1 > original1 + 40)  )
        {
           historyLog1[WINDOW-1] = original1;
        }
        else
        {
           historyLog1[WINDOW-1] = temp1;
         
        }

        if (  (temp2 < original2 - 40)||(temp2 > original2 + 40)  )
        {
          historyLog2[WINDOW-1] = original2;
        }
        else
        {
          historyLog2[WINDOW-1] = temp2;
        
        }
       
        
        int sum1 = 0;
        int sum2 = 0;
        for (int j = 0; j < WINDOW; j++)
        {
          sum1 += historyLog1[j];
          sum2 += historyLog2[j];
        }
        historyLog1[WINDOW-1] = sum1/WINDOW;
        historyLog2[WINDOW-1] = sum2/WINDOW;
    }
 }

 
  int distance1 = 5*historyLog1[WINDOW-1];
  int distance2 = 5*historyLog2[WINDOW-1];
  
  Serial.print (distance1);
  Serial.print ('+');
  Serial.println (distance2);
  //Serial.println (analogRead(analogInPin2));
  //Serial.print (counter1);
  //Serial.print ('+');
  //Serial.println (counter2);
  //counter1 ++;
  //counter2 ++;

  
  original1 = historyLog1[WINDOW-1];
  original2 = historyLog2[WINDOW-1];
  delay(30);
  flag  = 1;
}
