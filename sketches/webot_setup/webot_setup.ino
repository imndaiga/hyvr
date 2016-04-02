#include <SoftwareSerial.h>

SoftwareSerial mySerial(9, 8); // RX, TX

//1----1200bps
//2----2400bps
//3----4800bps
//4----9600bps
//5----19200bps
//6----38400bps
//7----57600bps
//8----115200bps
//9----230400bps
//A----460800bps
//B----921600bps
//C----1382400bps


//some MAX 232 chips cannot work reliably for 
//Baudrates faster than 115200bps, therefore, 
//don't set the Bluetooth to a Baudrate that 
//is faster than 115200bps.

void setup() {
   mySerial.begin(9600);
   delay(2000);
   mySerial.print("AT+NAMEKenshin");
   delay(2000);
   mySerial.print("AT+PIN4321");
   delay(2000);
   mySerial.print("AT+BAUD7");
}

void loop() {
}