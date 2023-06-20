// demo: CAN-BUS Shield, send data
// loovee@seeed.cc


#include <SPI.h>

#define CAN_2515
// #define CAN_2518FD

// Set SPI CS Pin according to your hardware

// For Arduino MCP2515 Hat:
// the cs pin of the version after v1.1 is default to D9
// v0.9b and v1.0 is default D10
const int SPI_CS_PIN = 10;
const int CAN_INT_PIN = 2;
float servo_setpoint_init = 0;

#include "mcp2515_can.h"
mcp2515_can CAN(SPI_CS_PIN); // Set CS pin

void setup() {
    SERIAL_PORT_MONITOR.begin(115200);
    while(!Serial){};

    while (CAN_OK != CAN.begin(CAN_125KBPS)) {             // init can bus : baudrate = 500k
        SERIAL_PORT_MONITOR.println("CAN init fail, retry...");
        delay(100);
    }
    SERIAL_PORT_MONITOR.println("CAN init ok!");
}

float ramp(float gradient, float servo_setpoint) {

  float throttle_feedback_calc;
  throttle_feedback_calc = gradient*servo_setpoint;

  return throttle_feedback_calc;
}

// Generate benchmark data
float data[][2] = {{1, 5.66}, {2, 9.68}, {3, 12.1}, {4, 15.58}, {5, 18.61}, {6, 21.28}, {7, 24.3}, {8, 27.38}, {9, 30.22}, {10, 33.38}, {11, 36.38}, {12, 39.75}, 
                    {13, 42.4}, {14, 45.44}, {15, 48.68}, {16, 51.7}, {17, 54.65}, {18, 57.9}, {19, 61.05}, {20, 64.25}, {21, 67.7}, {22, 70.75}, {23, 73.77}, {24, 76.52}, 
                    {25, 79.07}, {26, 82.14}, {27, 84.6}, {28, 86.38}, {29, 88.01}, {30, 89.3}, {31, 90.92}, {32, 92.01}, {33, 92.52}, {34, 93.03}, {35, 93.5}, {36, 94.02}, 
                    {37, 94.5}, {38, 94.77}, {39, 95.12}, {40, 95.5}, {41, 95.8}, {42, 96.2}, {43, 96.55}, {44, 96.92}, {45, 97.34}, {46, 97.51}, {47, 97.68}, {48, 97.84}, 
                    {49, 98}, {50, 98.14}, {51, 98.3}, {52, 98.46}, {53, 98.6}, {54, 98.76}, {55, 98.87}, {56, 98.95}, {57, 99.03}, {58, 99.11}, {59, 99.19}, {60, 99.27}, 
                    {61, 99.36}, {62, 99.45}, {63, 99.52}, {64, 99.57}, {65, 99.62}, {66, 99.66}, {67, 99.71}, {68, 99.75}, {69, 99.8}, {70, 99.85}, {71, 99.9}, {72, 99.95}, 
                    {73, 99.96}, {74, 99.96}, {75, 99.97}, {76, 99.98}, {77, 99.98}, {78, 99.99}, {79, 100}, {80, 100}
};

int n = 0;
int l  = sizeof(data)/sizeof(data[0]);
int temp = 0;
int update = 0;
static int servo_setpoint_prev = 1;
unsigned long start_time;
unsigned long timer_end = 4000; // ms
unsigned long curr_time;

void loop() {

    float dummy_data = 34.44;
    unsigned short int scaled_dummy_data = dummy_data * 100;

    // Populating servo setpoint with random dp value but linearly increasing n

    float noise = random(-1000, 1000)/1000.0;
    int servo_setpoint = data[n][0];
    double throttle_feedback = data[n][1] + noise;  

    Serial.print("Servo Setpoint: ");
    Serial.print(servo_setpoint);
    Serial.print("  |  Throttle Feedback: ");
    Serial.print(throttle_feedback, 2);
    Serial.print("  |  Update: ");
    Serial.println(noise, 3);
    
    // Scale the values
    unsigned short int scaled_servo_setpoint = servo_setpoint * 100;
    unsigned short int scaled_throttle_feedback = throttle_feedback * 100;

    byte data[8] = {
      
      // Dummy data
      byte(scaled_dummy_data),
      byte(scaled_dummy_data >> 8),

      // Throttle Feedback data
      byte(scaled_throttle_feedback),
      byte(scaled_throttle_feedback >> 8),

      // Servo setpoint data
      byte(scaled_servo_setpoint),
      byte(scaled_servo_setpoint >> 8),

      // Dummy data
      byte(scaled_dummy_data),
      byte(scaled_dummy_data >> 8)
      };

    CAN.MCP_CAN::sendMsgBuf(0x11, 0, 8, data);
    delay(2);                       // send data per 100ms

  curr_time = millis();
    
  if (curr_time - start_time > timer_end){
      n += 1;
  }

  if (n == l) {
      n = 0;
  } 

}

// END FILE
