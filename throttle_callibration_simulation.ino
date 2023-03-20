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
int n = 0;

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
void loop() {
   
    float dummy_data = 34.44;
    unsigned short int scaled_dummy_data = dummy_data * 100;

    // Populating servo setpoint with random dp value but linearly increasing n
    float servo_setpoint = n + random(100)/100;
    float throttle_feedback = ramp(1.0, servo_setpoint);

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
    delay(100);                       // send data per 100ms
    SERIAL_PORT_MONITOR.println("CAN BUS sendMsgBuf ok!");
    n += 1;
}

// END FILE
