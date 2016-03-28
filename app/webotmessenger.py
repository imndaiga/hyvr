#!/usr/bin/python
# sendandreceivearguments.py
# Author: Adrien Emery
# Make sure the you have the SendAndReceiveArguments example loaded onto the Arduino
import sys
import serial
import time

from cmdmessenger import CmdMessenger
from serial.tools import list_ports


class SendAndReceiveArguments(object):

    def __init__(self,port=None):
        # make sure this baudrate matches the baudrate on the Arduino
        self.running = False
        # this method list is matched with the enumerator type on the Arduino sketch
        # always make sure to have them in the same order.
        self.commands = ['acknowledge',
                         'error',
                         'pin_set_state',
                         'command_result',
                         'lcd_print',
                         'identify',
                         'motor_start',
                         ]

        try:
            if (port is None):
                print 'Ensure that the right firmware is loaded to the webot'
                print 'Select Serial Interface (USB=1,BLUETOOTH=2) >',
                selinterface=raw_input()
                if (selinterface == "1"):
                    print 'Set Baud=115200, readtimeout=0.1'
                    self.baud = 115200
                    self.readtimeout = 0.1
                    print 'USB interface selected'
                    # try to open the first available usb port
                    self.port_name = self.list_usb_ports()[0][0]
                elif (selinterface == "2"):
                    print 'Set Baud=9600, readtimeout=0.5'
                    self.baud = 9600
                    self.readtimeout = 0.5
                    print 'Bluetooth interface selected (/dev/rfcomm0)'
                    self.port_name = "/dev/rfcomm0"
                else:
                    print 'Defaulting to USB interface'
                    # try to open the first available usb port
                    self.port_name = self.list_usb_ports()[0][0]
            else:
                print 'Setting up bluetooth courier configuration'
                self.baud = 9600
                self.readtimeout = 0.5
                self.port_name = port
            self.serial_port = serial.Serial(self.port_name, self.baud, timeout=0)
        except (serial.SerialException, IndexError):
            raise SystemExit('Could not open serial port.')
        else:
            print 'Serial port sucessfully opened.'
            self.messenger = CmdMessenger(self.serial_port)
            # attach callbacks
            self.messenger.attach(func=self.on_error, msgid=self.commands.index('error'))
            self.messenger.attach(func=self.on_command_result,
                                  msgid=self.commands.index('command_result'))
            self.messenger.attach(func=self.on_identify, msgid=self.commands.index('identify'))

            # send a command that the arduino will acknowledge
            self.messenger.send_cmd(self.commands.index('acknowledge'))
            # Wait until the arduino sends an acknowledgement back
            self.messenger.wait_for_ack(ackid=self.commands.index('acknowledge'))
            print 'Edubot Ready'

    def on_identify(self, received_command, *args, **kwargs):
        print 'Identity:', args[0][0]

    def list_usb_ports(self):
        """ Use the grep generator to get a list of all USB ports.
        """
        ports =  [port for port in list_ports.grep('usb')]
        return ports

    def on_error(self, received_command, *args, **kwargs):
        """Callback function to handle errors
        """
        print 'Error:', args[0][0]

    def on_command_result(self, received_command, *args, **kwargs):
        """Callback to handle the Pin State Change success state
        """
        print 'Echo Received:', args[0]
        print

    def stop(self):
        self.running = False

    def run(self):
        """Main loop to send and receive data from the Arduino        
        """
        print 'Determining device identity'
        self.messenger.send_cmd(self.commands.index('identify'))
        time.sleep(self.readtimeout)
        self.messenger.feed_in_data()
        self.running = True
        while self.running:
            print 'Which command would you like to test? (1-Pin Set, 2-LCD Print) ',
            userchoice = raw_input()
            if (userchoice == "1"):
                print 'Enter Pin Number > ',
                a = raw_input()
                print 'Enter State > ',
                b = raw_input()
                print 'Sending: {}, {}'.format(a, b)
                self.messenger.send_cmd(self.commands.index('pin_set_state'), a, b)
            if (userchoice == "2"):
                print 'Enter LCD String > ',
                c = raw_input()
                print 'Sending: {}'.format(c)
                self.messenger.send_cmd(self.commands.index('lcd_print'), c)

            # Check to see if any data has been received
            time.sleep(self.readtimeout)
            self.messenger.feed_in_data()

    def relay(self,blocklycommands):
        commandlist = []
        commandlist = blocklycommands.split(';')
        self.messenger.send_cmd(self.commands.index('identify'))
        time.sleep(self.readtimeout)
        self.messenger.feed_in_data()
        commax=len(commandlist)
        # for some reason the last element is an empty string, the following
        # statements clean that out
        validcommandlist = [validcommand for validcommand in commandlist[0:commax-1]]
        # print validcommandlist
        for commandset in validcommandlist:
            command = []
            command = commandset.split(',')
            print command[0]
            # argnumber=len(command[1:])
            self.messenger.send_cmd(self.commands.index(command[0]),*command[1:])
            time.sleep(self.readtimeout)
            self.messenger.feed_in_data()

def courier(devport,blocklycommands):
    print 'Webot Courier Service Started: ', devport, blocklycommands
    send_and_receive_args = SendAndReceiveArguments(port=devport)
    send_and_receive_args.relay(blocklycommands)

if __name__ == '__main__':
    send_and_receive_args = SendAndReceiveArguments()

    try:
        print 'Press Ctrl+C to exit...'
        print
        send_and_receive_args.run()
    except KeyboardInterrupt:
        send_and_receive_args.stop()
        print 'Exiting...'
