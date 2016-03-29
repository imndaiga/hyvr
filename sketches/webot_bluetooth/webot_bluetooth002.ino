// *** Webo_LCDPrint ***

// This expands Webo_Identify. The Webot can now receive and process
// the following commands:
// - Return multiple types status; It can return an Acknowlegde and Error command
// - Receive multiple parameters,
// - Send multiple parameters
// - Call a function periodically
// - Change pin number parameter to specified state parameter
// - Print LCD string parameter onto Groove-LCD RGB Backlight v2.0
// - Create a software serial object to send data over bluetooth
//Note: functions beginning with "on" are reserved by CmdMessenger
//Note: bluetooth serial connections take longer to set up, so acknowledgement
//to requesting device is now attached to a callback function.

#include <SoftwareSerial.h> // SoftwareSerial
#include <CmdMessenger.h>  // CmdMessenger
#include <Wire.h>          // I2C library
#include "rgb_lcd.h"       // Groove LCD library

// Blinking led variables 
unsigned long previousToggleLed = 0;   // Last time the led was toggled
bool ledState                   = 0;   // Current state of Led
const int kBlinkLed             = 13;  // Pin of internal Led

// Instantiate an rgb_lcd object
rgb_lcd lcd;
// Instantiate an Serial object with TX, RX arguments
SoftwareSerial serBluetooth(9, 8); // RX, TX
// Attach a new CmdMessenger object to the default Serial port
CmdMessenger cmdMessenger = CmdMessenger(serBluetooth);
// This is the list of recognized commands. These can be commands that can either be sent or received. 
// In order to receive, attach a callback function to these events
enum
{
  // Commands
  kAcknowledge         , // Command to acknowledge that cmd was received
  kError               , // Command to report errors
  kPinSetState       , // Command to request Pin Number and Set State
  kCommandResult     , // Command to report successful command execution
  kLcdPrint          , // Command to request strings to be written to LCD
  kIdentify          , // Command to both identify exact device and for watchdog to differentiate multiple serial
  kMotorStart        , // Command to move attached motors for a specified duration
  
};

// ------------------  C A L L B A C K S -----------------------

// Called when a received command has no attached function
void OnUnknownCommand()
{
  cmdMessenger.sendCmd(kError,"Command without attached callback");
}

void onIdentifyRequest()
{
  cmdMessenger.sendCmd(kIdentify, F("BFAF4176-766E-436A-ADF2-96133C02B03C"));
}

// Callback function that responds that Arduino is ready (has booted up)
void BluetoothAck()
{
  cmdMessenger.sendCmd(kAcknowledge,"Edubot ready");
}

// Callback function that toggles a specified Pin state
void PinSetState()
{
  int setPin = cmdMessenger.readInt16Arg();
  bool setState = cmdMessenger.readBoolArg();
  // set pin for toggle switching
  pinMode(setPin, OUTPUT);
  digitalWrite(setPin, setState?HIGH:LOW);
  cmdMessenger.sendCmdStart(kCommandResult);
  cmdMessenger.sendCmdArg(setPin);
  cmdMessenger.sendCmdArg(setState);
  cmdMessenger.sendCmdEnd();
}

// Callback function that sets Motor Directions and Speed
void LcdPrint()
{
  String lcdString = cmdMessenger.readStringArg();
  int r = cmdMessenger.readInt16Arg();
  int g = cmdMessenger.readInt16Arg();
  int b = cmdMessenger.readInt16Arg();

  if ( r || b || g ){
    if (lcdString != "None") {
      lcd.clear();
      //  lcd.print does some string preprocessing before outputting
      //  to the lcd unlike lcd.write which would error out with
      //  the lcdString object.
      lcd.print(lcdString);
      lcd.setRGB(r, g, b);
      cmdMessenger.sendCmdStart(kCommandResult);
      cmdMessenger.sendCmdArg(lcdString);
      cmdMessenger.sendCmdArg(r);
      cmdMessenger.sendCmdArg(g);
      cmdMessenger.sendCmdArg(b);
      cmdMessenger.sendCmdEnd();
    }
    else {
      lcd.setRGB(r, g, b);
      cmdMessenger.sendCmdStart(kCommandResult);
      cmdMessenger.sendCmdArg(r);
      cmdMessenger.sendCmdArg(g);
      cmdMessenger.sendCmdArg(b);
      cmdMessenger.sendCmdEnd();
    }
  }
  else {
    if (lcdString != "None") {
      lcd.clear();
      //  lcd.print does some string preprocessing before outputting
      //  to the lcd unlike lcd.write which would error out with
      //  the lcdString object.
      lcd.print(lcdString);
      cmdMessenger.sendCmdStart(kCommandResult);
      cmdMessenger.sendCmdArg(lcdString);
      cmdMessenger.sendCmdEnd();
    }
    else {
      lcd.clear();
      cmdMessenger.sendCmdStart(kCommandResult);
      cmdMessenger.sendCmdArg("No arguments found");
      cmdMessenger.sendCmdEnd();
    }
  }
}

// Commands we send from the PC and want to receive on the Arduino.
// We must define a callback function in our Arduino program for each entry in the list below.

void attachCommandCallbacks()
{
  // Attach callback methods
  cmdMessenger.attach(OnUnknownCommand);
  cmdMessenger.attach(kPinSetState, PinSetState);
  cmdMessenger.attach(kLcdPrint, LcdPrint);
  cmdMessenger.attach(kAcknowledge, BluetoothAck);
  cmdMessenger.attach(kIdentify, onIdentifyRequest);
}

// ------------------ M A I N  ----------------------

// Setup function
void setup() 
{
  // Listen on serial connection for messages from the pc
  serBluetooth.begin(9600);

  // Adds newline to every command
  cmdMessenger.printLfCr();   

  // Attach my application's user-defined callback methods
  attachCommandCallbacks();

  // Send the status to the PC over USB that says the Arduino has booted
  //  cmdMessenger.sendCmd(kAcknowledge,"Edubot has started!");
  
  // set pin for blink LED
  pinMode(kBlinkLed, OUTPUT);

  // set up the LCD's number of columns and rows:
  lcd.begin(16, 2);
}

// Returns if it has been more than interval (in ms) ago. Used for periodic actions
bool hasExpired(unsigned long &prevTime, unsigned long interval) {
  if (  millis() - prevTime > interval ) {
    prevTime = millis();
    return true;
  } else     
    return false;
}

// Toggle led state 
void toggleLed()
{  
  ledState = !ledState;
  digitalWrite(kBlinkLed, ledState?HIGH:LOW);
}  

// Loop function
void loop() 
{
  // Process incoming serial data, and perform callbacks
  cmdMessenger.feedinSerialData();

  // Toggle LED periodically. If the LED does not toggle every 2000 ms, 
  // this means that cmdMessenger are taking a longer time than this  
  if (hasExpired(previousToggleLed,2000)) // Toggle every 2 secs
  {
    toggleLed();  
  } 
}
