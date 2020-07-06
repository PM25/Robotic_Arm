from adafruit_servokit import ServoKit
from time import sleep
from evdev import InputDevice, categorize, ecodes
import threading
import numpy as np
import cv2
from pathlib import Path

kit = ServoKit(channels=8)

for ename in Path('/dev/input').glob('event*'):
	print(InputDevice(str(ename)))

print()
print('-' * 10)
ename = input('Select Event: ')
gamepad = InputDevice('/dev/input/event' + ename)
print(gamepad)

init_deg = [70, 40, 150, 30, 95, 95]
deg = [70, 40, 150, 30, 95, 95]
rot = [0, 0, 0, 0, 0, 0]
bound = [[0, 150], [0, 179], [0, 179], [0, 179], [0, 179], [95, 180]]

class ResetThread(threading.Thread):
	def __init__(self):
		super().__init__()
		
	def run(self):
		global deg
		print('Reset Thread is Running')
		while(deg[0] > init_deg[0]):
			deg[0] -= 1
			deg[1] -= 1
			sleep(.02)
		while(deg[0] < init_deg[0]):
			deg[0] += 1
			deg[1] += 1
			sleep(.02)
			
		while(deg[1] > init_deg[1]):
			deg[1] -= 1
			sleep(.02)
		while(deg[1] < init_deg[1]):
			deg[1] += 1
			sleep(.02)
		
		deg[4] = init_deg[4]
		deg[5] = init_deg[5]
		sleep(.2)
		while(deg[3] > init_deg[3]):
			deg[3] -= 1
			sleep(.02)
		while(deg[3] < init_deg[3]):
			deg[3] += 1
			sleep(.02)
			
		while(deg[2] > init_deg[2]):
			deg[2] -= 1
			sleep(.02)
		while(deg[2] < init_deg[2]):
			deg[2] += 1
			sleep(.02)
		print('RESET!')


class ServoThread(threading.Thread):
	def __init__(self):
		super().__init__()
		
	def run(self):
		global rot, deg
		print('Servo Thread is Running')
		while True:
			# print(deg, rot)
			for i in range(len(deg)):
				deg[i] += rot[i]
				if(deg[i] > bound[i][1]):
					deg[i] = bound[i][1]
				elif(deg[i] < bound[i][0]):
					deg[i] = bound[i][0]
				kit.servo[i].angle = deg[i]
			sleep(.035)

class CamThread(threading.Thread):
	def __init__(self):
		super().__init__()
		self.cap = cv2.VideoCapture(0)
		self.cap.set(cv2.CAP_PROP_FPS, 20)
		
	def run(self):
		while(True):
			ret, frame = self.cap.read()
			cv2.imshow('frame', frame)
			if cv2.waitKey(1) & 0xFF == ord('q'):
				break
		self.cap.release()
		cv2.destroyAllWindows()

ServoThread().start()
ResetThread().start()
CamThread().start()

aBtn = 304
bBtn = 305
xBtn = 307
yBtn = 308

for event in gamepad.read_loop():
	if event.type == ecodes.EV_KEY:
		print(event)
		if(event.value == 1):
			if event.code == 317:
				ResetThread().start()
			elif event.code == 310:
				rot[5] = -15
			elif event.code == 311:
				rot[5] = 5
			elif event.code == aBtn:
				if(deg[5] >= 175):
					deg[5] = 95
				else:
					deg[5] = 179
		elif(event.value == 0):
			if event.code == 310 or event.code == 311:
				rot[5] = 0

	elif event.type == ecodes.EV_ABS:
		absevent = categorize(event)
		# print(ecodes.bytype[absevent.event.type][absevent.event.code], absevent.event.value)
		
		if ecodes.bytype[absevent.event.type][absevent.event.code] == 'ABS_X':
			rot[0] = -int(absevent.event.value / 32767 * 3)
		
		elif ecodes.bytype[absevent.event.type][absevent.event.code] == 'ABS_RY':
			rot[3] = -int(absevent.event.value / 32767 * 3)
			
		elif ecodes.bytype[absevent.event.type][absevent.event.code] == 'ABS_Y':
			rot[1] = -int(absevent.event.value / 32767 * 2)
			rot[2] = -int(absevent.event.value / 32767 * 2)
				
		elif ecodes.bytype[absevent.event.type][absevent.event.code] == 'ABS_RZ':
			if absevent.event.value > 0:
				deg[4] = 179
			else:
				deg[4] = 95
		elif ecodes.bytype[absevent.event.type][absevent.event.code] == 'ABS_Z':
			if absevent.event.value > 0:
				deg[4] = 0
			else:
				deg[4] = 95

