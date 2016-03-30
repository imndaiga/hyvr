# import bluetooth
import os
import time
import serial
import webotmessenger
import re
from app import db, app
from app.models import User, Robot
from datetime import datetime
from flask import json, g
from sys import platform as _platform
import sys
from collections import defaultdict

if os.name == 'posix' and sys.version_info[0] < 3:
    import subprocess32 as subprocess
else:
    import subprocess

# Uncomment the following lines to enable BLE search
# if _platform == "linux" or _platform == "linux2":
# 	from bluetooth.ble import DiscoveryService
# 	blescan = True
# else:
# 	blescan = False

# import filepaths from config file
bdir = app.config["BASE"]
sdir = app.config["DATA"]
# search result from bluetooth legacy discovery stored in resp list
resp = []
# webotcommands stores all the blockly python code parsed in from Panya Class
webotcommands = ""

# determine which platform this app package is running on and set the
# required shell/bash script paths. these scripts manage all the
# hosts bluetooth pairing and device tree attaching with the robots.
rfpath = os.path.join(bdir,"app","hostcon.sh")
if _platform == "linux" or _platform == "linux2":
	import bluetooth
	host="linux"
elif _platform == "darwin":
	host="darwin"
else:
	import bluetooth
	host="win"

# Uncomment the following lines to enable BLE search
# def bleinquire():
# 	global resp
# 	global i
# 	service = DiscoveryService()
# 	devices = service.discover(2)
# 	for addr, name in devices.items():
# 		resp.append({'mac*':str(addr),'name*':str(name)})

class Panya(object):

	def __init__(self):
		pass

	def PanyaStop(self):
		packcommands(''.join("function_stop"))

	def PanyaMotors(self, direction, duration):
		self.direction = direction
		self.duration = duration
		# self.speed = speed
		packcommands(','.join(["motor_start",str(self.direction),str(self.duration)]))

	def PanyaDelay(self, pauseduration):
		self.delay = pauseduration
		packcommands(','.join(["function_pause",str(self.delay)]))

	def PanyaPin(self, pin, state=None, pwmvalue=None):
		self.pin = pin
		self.state = state
		self.pwmvalue = pwmvalue
		packcommands(','.join(["pin_set_state",str(self.pin),str(self.state),str(self.pwmvalue)]))

	def PanyaLCD(self, msg=None, rgb=None):
		self.msg = msg
		self.lcdrgb = rgb
		packcommands(','.join(["lcd_print",str(self.msg),str(self.lcdrgb)]))

	def PanyaRepeat(self, iterations):
		self.repeat = iterations
		packcommands(','.join(["repeat",str(self.repeat)]))

def messagereturn(cuser,errorkey,stricterror=None,fullcycle=None):
	messresp = defaultdict(list)
	errordict = [{ "error":1, "info":"HCI reset error" },{ "error":2, "info":"HCI reset error"},{ "error":3, "info":"No HCI available"},
					{ "error":4, "info":"HCI switch error"},{ "error":5, "info":"HCI switch error"},{ "error":6, "info":"HCI switch error"},
					{ "error":7, "info":"HCI switch error"},{ "error":8, "info":"No HCI available"},{"error":9, "info":"HCI pull down error"},
					{ "error":10, "info":"HCI pull up error"},{ "error":11, "info":"Device release error"},{ "error":12, "info":"Device assignment error"},
					{ "error":13, "info":"No HCI available"},{ "error":14, "info":"Bluetooth unpair error"},{ "error":15, "info":"Device unpair error"},
					{ "error":16, "info":"Firmware upload error"},{ "error":17, "info":"Bluetooth pairing error"},{ "error":18, "info":"Device binding failed"},
					{ "error":19, "info":"Device binding error"},{"error":20, "info":"Bluetooth pairing error"},{ "error":21, "info":"Device binding failed"},
					{ "error":22, "info":"Device not found"},{ "error":23, "info":"No HCI interfaces up"},{ "error":24, "info":"No HCI available"},{ "error":25, "info": "No HCI available"},
					{ "error":26, "info":"No HCI available"},{ "error":27, "info":"No USB devices found"},{ "error":28, "info":"No Arduinos found"},{ "error":29, "info":"No HCI available"},
					{ "error":30, "info":"Bluetooth setup error"},{ "error":31, "info":"Port is permanently closed"}, { "error":32, "info":"No HCI available"},
					{ "error":33, "info":"Couldn't send data"},{ "error":34, "info":"Firmware does not exist"}
					]
	if (stricterror==None) and (fullcycle==None):
		print 'starting halfcycle error logging'
		errorfile = os.path.join(sdir,g.user.nickname,'error.log')
		json_data=[]
		# remember to include stacktrace error if error not within range
		# print 'CRITICAL ERROR: UNEXPECTED ERROR OCCURRED!'
		# print "STACKTRACE:"
		if os.path.exists(errorfile):
			with open(errorfile,'r') as json_target:
				json_data = json.load(json_target)
				for error in json_data:
					if (int(error["key"]) == int(errorkey)):
						print 'copying error instance: '+str(error)
						for code in error["code"]:
							for refcode in errordict:
								if (int(code)==int(refcode["error"])):
									messresp["info"].append(refcode["info"])
			return json.dumps(messresp)
		else:
			return json.dumps(messresp)
	elif (stricterror==None) and (fullcycle!=None):
		print 'starting fullcycle error logging'
		errorfile = os.path.join(sdir,g.user.nickname,'error.log')
		json_data=[]
		# remember to include stacktrace error if error not within range
		# print 'CRITICAL ERROR: UNEXPECTED ERROR OCCURRED!'
		# print "STACKTRACE:"
		if os.path.exists(errorfile):
			with open(errorfile,'r') as json_target:
				json_data = json.load(json_target)
				for error in json_data:
					if (int(error["key"]) == int(errorkey)):
						print 'copying error instance: '+str(error)
						for code in error["code"]:
							for refcode in errordict:
								if (int(code)==int(refcode["error"])):
									messresp["info"].append(refcode["info"])
			print 'deleting error log file'
			if os.path.exists(errorfile):
				os.remove(errorfile)
			return json.dumps(messresp)
		else:
			print 'deleting error log file'
			if os.path.exists(errorfile):
				os.remove(errorfile)
			return json.dumps(messresp)
	elif (stricterror!=None) and (fullcycle==None):
		print 'starting strict/escalated error logging'
		errfound=False
		for err in errordict:
			if (stricterror==err["error"]):
				print 'error '+str(err["error"])+":"+str(err["info"])
				messresp["info"].append(err["info"])
				errfound=True
				return json.dumps(messresp)

def leginquire():
	# bluetooth legacy discovery api endpoint. This endpoint is used by the
	# registration page when searching for nearby bluetooth devices.
	global resp
	global i
	resp = []
	cuser="admin"
	errorkey=int(time.time())
	if (host=="win"):
		output=subprocess.call([rfpath,'-h',host,'-P', '-e', errorkey,'-c',cuser], shell=True)
		print '********************************************************************'
		print output
		print '********************************************************************'
	else:
		output=subprocess.call(['%s -h %s -P -e %s -c %s' %(rfpath,host,errorkey,cuser)], shell=True)
		print '********************************************************************'
		print output
		print '********************************************************************'
	if (output==0):
		print 'Subprocess call complete with '+str(output)+' errors'
		nearby_devices = bluetooth.discover_devices(duration=8, lookup_names=True, flush_cache=True)
		for addr, name in nearby_devices:
			try:
				resp.append({'mac':str(addr),'name':str(name)})
			except UnicodeEncodeError:
				resp.append({'mac':str(addr),'name':str(name.encode('utf-8', 'replace'))})
		
		# ble discovery endpoint. This trigger is a work in progress due to limitations
		# with the pybluez library.
		# if ((resp == []) & (blescan)):
			# bleinquire()

		# jsonify the bluetooth search results to be consumed by the 
		# registration page ajax pull request.
		response = json.dumps(resp)
		return response
	else:
		print "Error performing bluetooth search"
		print 'ERROR 5: Subprocess call complete with '+str(output)+' errors'
		return messagereturn(None,None,32,None)

def sdpbrowse(macid=None):
	# this function determines the available service profiles at the specified bluetooth macid.
	target = macid
	print "Determining service profiles at "+str(target)
	if target == "all": target = None

	services = bluetooth.find_service(address=target)

	if len(services) > 0:
	    print("found %d services on %s" % (len(services), target))
	    print()
	else:
	    print("no services found")

	for svc in services:
	    print("Service Name: %s"    % svc["name"])
	    print("    Host:        %s" % svc["host"])
	    print("    Description: %s" % svc["description"])
	    print("    Provided By: %s" % svc["provider"])
	    print("    Protocol:    %s" % svc["protocol"])
	    print("    channel/PSM: %s" % svc["port"])
	    print("    svc classes: %s "% svc["service-classes"])
	    print("    profiles:    %s "% svc["profiles"])
	    print("    service id:  %s "% svc["service-id"])
	    print()

def sketchupl(firmware):
	sketchpath=os.path.join(bdir,"sketches",firmware)
	if os.path.exists(sketchpath):
		errorkey=int(time.time())
		cuser=g.user.nickname
		if (host=="win"):
			output=subprocess.call([rfpath,'-h',host,'-s',sketchpath, '-r', '-e', errorkey,'-c',cuser], shell=True)
			print '********************************************************************'
			print output
			print '********************************************************************'
		else:
			output=subprocess.call(['%s -h %s -s %s -r -e %s -c %s' %(rfpath,host,sketchpath,errorkey,cuser)], shell=True)
			print '********************************************************************'
			print output
			print '********************************************************************'
		if (output==0):
			print 'Subprocess call complete with '+str(output)+' errors'
			return messagereturn(cuser,errorkey,None,"fullcycle")
		else:
			print "Error uploading firmware to devices"
			print 'ERROR 4: Subprocess call complete with '+str(output)+' errors'
			return messagereturn(cuser,errorkey,None,"fullcycle")
	else:
		# Firmware specified does not exist, explicitly handled through messagereturn
		print sketchpath
		return messagereturn(None,None,34,None)

def rfcommbind(rfcset,macid,alias=None,unick=None,commands=None,uid=None,flush=None,errorkey=None,cuser=None,returnerror=None):
	# this function takes the supplied macid passing it to the bash/shell script to
	# pair to using the simple-bluez-agent tool and attach said macid to a 
	# /dev/rfcomm port. If the reset flag is passed, the associated robot macid is 
	# flushed i.e. released from rfcomm and the pairing entry deleted from 
	# /var/lib/bluetooth/{local host macid}/linkkeys. This flushing might be overkill
	# but it ensures that all host-robot sessions are handled robustly.
	if flush is None:
		errorkey=int(time.time())
		cuser=g.user.nickname
		if (host=="win"):
			output=subprocess.call([rfpath,'-u',macid,'-d',rfcset,'-h',host, '-p','-e',errorkey,'-c',cuser], shell=True)
		else:
			output=subprocess.call(['%s -u %s -d %s -h %s -p -e %s -c %s' %(rfpath,macid,rfcset,host,errorkey,cuser)], shell=True)
		print '********************************************************************'
		print output
		print '********************************************************************'
		if (output==0):
			print 'Subprocess call complete with '+str(output)+' errors'
			print 'Starting command upload procedure'
			# errorkey and cuser values passed to datasend to ensure bash script
			# can match errorkeys to place errors in appropriate dictionary.
			# feature has not been implemented fully, hostcon cannot perform
			# the matching yet. Why I'm doing this is to have a static log of
			# all errors users may run into with the program. Currently, the
			# error.log file is deleted after every fullcycle run.
			datasend(macid,alias,unick,commands,rfcset,uid,errorkey,cuser)
		else:
			print "Error Binding and pairing bluetooth Device"
			print 'ERROR 1: Subprocess call complete with '+str(output)+' errors'
			print 'Cleaning robot status key-value'
			robot = Robot.query.filter_by(user_id=uid).first()
			robots = Robot.query.all()
			robot.status="inactive"
			db.session.commit()
			for rob in robots:
				print "%s:%s" %(robot.alias,robot.status)
			return messagereturn(cuser,errorkey,None,"fullcycle")
	else:
		if (host=="win"):
			output=subprocess.call([rfpath,'-u',macid,'-d',rfcset,'-h',host, '-f','-e',errorkey,'-c',cuser], shell=True)
		else:
			output=subprocess.call(['%s -u %s -d %s -h %s -f -e %s -c %s' %(rfpath,macid,rfcset,host,errorkey,cuser)], shell=True)
		print '********************************************************************'
		print output
		print '********************************************************************'
		if (output==0):
			print 'Subprocess call complete with '+str(output)+' errors'
			print 'Cleaning robot status key-value'
			robot = Robot.query.filter_by(user_id=uid).first()
			robots = Robot.query.all()
			robot.status="inactive"
			db.session.commit()
			for rob in robots:
				print "%s:%s" %(robot.alias,robot.status)
			return messagereturn(cuser,errorkey,returnerror,"fullcycle")
		else:
			print "Error releasing and unpairing bluetooth Device"
			print 'ERROR 6: Subprocess call complete with '+str(output)+' errors'
			print 'Cleaning robot status key-value'
			robot = Robot.query.filter_by(user_id=uid).first()
			robots = Robot.query.all()
			robot.status="inactive"
			db.session.commit()
			for rob in robots:
				print "%s:%s" %(robot.alias,robot.status)
			return messagereturn(cuser,errorkey,returnerror,"fullcycle")

def datasend(macid,alias,unick,commands,rfcset,uid,errorkey,cuser):
	# this is the command transport mechanism. A serial port is opened at the rfcset
	# declared devport and commands transmitted using the pyserial library.
	# currently in testing, default preset values are sent to the attached robot that
	# must be running the arduino panyabot sketch.
	# future feature to use the standard firmata library to have bidirectional
	# transmission of data (commands and sensor values).
	try:
		baud = 9600
		tbuffer = 1
		devport = "/dev/"+str(rfcset)
		print devport
		webotmessenger.courier(devport,commands)
		# ser = serial.Serial(devport, baud)
		# print ser
		# print 'Sending %s\'s commands to %s, alias:%s' % (unick,macid,alias)
		# # send and print the stored commands to the robot and terminal window respectively
		# for i in range(0,len(commands)):
		# 	time.sleep(tbuffer)
		# 	print commands[i]
		# 	ser.write(str(commands[i]))
		# ser.close()
		# after downstream data transmission is completed, the attached robot is flushed.
		rfcommbind(rfcset,macid,None,None,None,uid,"flush",errorkey,cuser,None)
		flush = ""
	except serial.SerialException, e:
		print 'Port %s not available.' %(devport)
		print 'Will release and unpair from %s' % (uid)
		print str(e)
		rfcommbind(rfcset,macid,None,None,None,uid,"flush",errorkey,cuser,33)

def rfcommset(robots):
	# this function manages the allocation of rfcomm port numbers to each incoming request.
	# prstlist stores the previously allocated dev numbers that haven't been declared inactive.
	# prstflag indicates that the function must iterate to the lowest unused port number.
	prstlist = {}
	prstflag = False
	user = User.query.filter_by(nickname=g.user.nickname).first()
	robot = Robot.query.filter_by(user_id=user.id).first()
	robots = Robot.query.all()
	for robot in robots:
		if (robot.status!="inactive"):
			prstcomm=re.search("rfcomm.",robot.status)
			print 'Found %s registered to %s' %(prstcomm.group(),robot.alias)
			devno=prstcomm.group().strip("rfcomm")
			prstlist['robot.alias']=devno
			prstflag = True

	if prstflag:
		# this conditional and nested loop interate over the values stored
		# in the prstlist to determine what port value to assign for the current
		# request.
		print 'Iterating to lowest available rfcomm index'
		setval = 0
		for key, value in prstlist.iteritems():
			if (setval<int(value)):
				setval=int(value)+1
	else:
		# if prstflag is not true, default to assign at port 0 (i.e. /dev/rfcomm0)
		print 'No devices found to be in active use. Setting setcomm to rfcomm'
		setval = 0

	setcomm="rfcomm"+str(setval)
	return setcomm

def portsetup(commands):
	# this function checks if any current robots are attached and in process
	# if there are, the current request is queued until such a time that all
	# prior tranmissions are completed.
	Qflag = False
	Tout = False
	Qout = False
	user = User.query.filter_by(nickname=g.user.nickname).first()
	robot = Robot.query.filter_by(user_id=user.id).first()
	robots = Robot.query.all()
	for rob in robots:
		print "%s:%s" %(robot.alias,robot.status)
		if (rob.status != "inactive") and (robot.alias != rob.alias):
			# Wait for 5 seconds and check again if a host-client bluetooth connection is up
			# If elapsed_time is greater than 10 seconds then timeout the process and prompt
			# for database check for any errors found
			print "Queuing bluetooth upload"
			Qflag = True
			queue_start = time.time()
			elapsed_time = 0
			while (elapsed_time < 5) and not (Qout):
				if (rob.status == "inactive"):
					print 'Slot in queue found'
					Qout = True
				elapsed_time = time.time() - queue_start
			if (elapsed_time > 5) and not Qout:
				print 'Port setup timeout'
				Tout = True
		elif (rob.status != "inactive") and (robot.alias == rob.alias):
				Qout=True
				print 'Robot key-value pair found in error state'
				print 'Cleaning robot status key-value'
				robot.status="inactive"
				db.session.commit()
				for rob in robots:
					print "%s:%s" %(robot.alias,robot.status)
		else:
			Qout = True

		if Qout and not Tout:
			Qflag = False
		else:
			print "Please check database value for the key %s:%s" %(rob.alias,rob.status)
	if not Qflag:
		rfcset=rfcommset(robots)
		robot.status=rfcset
		db.session.commit()
		return rfcommbind(str(rfcset),str(robot.macid),str(robot.alias),str(user.nickname),str(commands),str(user.id))
	# sdpbrowse(robot.macid) # HC06 and HC05 bluetooth modules don't advertise an SDP interface. Uncomment if
	# using a module that does. Bug number will be attached to this issue.

def packcommands(*args):
	global webotcommands
	for arg in args:
		webotcommands += arg+";"

def parseblocks(blocklycode):
	# this is where blockly code is parsed into a python file with the command list
	# saved in memory for transimission.
	global webotcommands
	panya=Panya()
	t = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
	savedir = os.path.join(sdir, g.user.nickname, 'sketches')
	if not os.path.exists(savedir):
		os.mkdir(savedir)
	filename = os.path.join(savedir, t+'.py')
	print 'Saving python code to ',filename
	target = open(filename,'w')
	target.write(blocklycode)
	target.close()
	# We now compile the generated python strings in the blocklycode
	# into bytecode and execute the resultant .pyc through the exec function
	# in our current namespace (I can't figure out a better way to have the
	# panya class instance variables accessible)
	# Read about caveats here - http://lucumr.pocoo.org/2011/2/1/exec-in-python/
	compiledcode = compile(blocklycode,'<string>','exec')
	exec compiledcode
	print webotcommands
	sessionresponse = portsetup(webotcommands)
	webotcommands = ""
	return sessionresponse

if __name__ == '__main__':
	# print "OS: %s" % (str(_platform))
	print leginquire()
