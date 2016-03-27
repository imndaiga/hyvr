
commands = []

class Panya(object):
	def __init__(self):
		pass

	def PanyaStop(self):
		storecomms("function_stop;")

	def PanyaMotors(self, direction, duration):
		self.direction = direction
		self.duration = duration
		# self.speed = speed
		storecomms("motor_start",self.direction,self.direction,";")

	def PanyaDelay(self, pauseduration):
		self.delay = pauseduration
		storecomms("function_pause",self.delay,";")

	def PanyaPin(self, pin, state):
		self.pin = pin
		self.state = state
		storecomms("pin_set_state",self.pin,self.state,";")

	def PanyaLCD(self, msg=None, rgb=None):
		self.msg = msg
		self.lcdrgb = rgb
		storecomms("lcd_print",self.msg,self.lcdrgb,";")

	def PanyaRepeat(self, iterations):
		self.repeat = iterations
		storecomms("repeat",self.repeat,";")

def storecomms(*args):
	for arg in args:
		commands.append(arg)

def main():
	pass

if __name__ == '__main__':
	main()