# -*- coding: utf-8 -*-
"""
Created on Fri Dec 21 09:04:48 2018

@author: Mikael
"""

from serial import Serial

import schedule
from datetime import datetime as dt
import logging
import time
import mail_handler as mailh

logging.basicConfig(filename ='C:/Users/Mikael/Documents/Python Scripts/Tärendö/logfile.log',level=logging.DEBUG)

def gts():
    n = dt.now()
    retstr = '\t' + str(n.year) + '-' + str(n.month)  + '-' + str(n.day)  + ':' + str(n.hour) + ':' + str(n.minute) + ' - ' 
			
    return retstr


class ArduConnection:
	def __init__(self,inpport = 'COM5'):
		# self.ser = Serial(port=inpport)
		logging.info(gts() + ' connected made to arduino.')
		
	def sendAndRecive(self,message):
		self.send(message)
		return self.read()

	def read(self):
		retstr = ''
		while retstr == '':
			retstr = self.ser.readline().decode().strip()
		return retstr

	def send(self,msg):
		self.ser.write(msg.encode())

	def close(self):
		self.ser.close()

	def getPipeTemperature(self):
		return float(self.sendAndRecive('pipetemperature'))

	def getRoomTemperature(self):
		return float(self.sendAndRecive('roomtemperature'))

	def getRoomHumidity(self):
		return float(self.sendAndRecive('humidity'))

	def turnCellarRadiatorOn(self):
		logging.info('radiator turned on')
	
	def turnCellarRadiatorOff(self):
		print.info('radiator turned off')

class runner:
	def __init__(self,maxtemp=None,mintemp=None):		
		
		if maxtemp == None:
			#read from defaultvalues.txt!!
			self.maxroomtemp = 15
			self.minroomtemp = 6
		
		
		# self.ardu = ArduConnection()
		time.sleep(2)

		schedule.every(5).seconds.do(lambda: self.hourlycheck())
		schedule.every(1).seconds.do(lambda: self.checkMail())
		self.radiatorstatus = False
		self.heaterstatus = True
		self.roomtemp = 20
		self.pipetemp = 23
		self.humid = 100
		
		self.fejk = False
	def getfejkstatus(self):
		if self.roomtemp <4 or self.fejk:
			self.roomtemp += 1
			self.fejk = True
			if self.roomtemp >20:
				self.fejk = False
		else:
			self.roomtemp -= 1		
			

	def hourlycheck(self):
		# self.getStatus()
		self.getfejkstatus()
		logging.info(gts() +'pipe temperature: ' + str(self.pipetemp) + ', room temparature: ' + str(self.roomtemp) + ', humidity: ' + str(self.humid))
		self.radiatorControl()

	def radiatorControl(self):
		print(self.roomtemp)
		print(self.radiatorstatus)

		if (self.roomtemp < self.minroomtemp) and not self.radiatorstatus:
			self.turnOnRadiator()
		elif (self.roomtemp > self.maxroomtemp) and self.radiatorstatus:
			self.turnOffRadiator()

	def turnOnRadiator(self):
		logging.info(gts() + 'Turning on radiator')
		# self.ardu.turnCellarRadiatorOn()
		self.sendEmail('Turning on Radiator')
		self.radiatorstatus = True
	def turnOffRadiator(self):
		logging.info('Turning off radiator')
		# self.ardu.turnCellarRadiatorOff()
		self.sendEmail('Turning off Radiator')
		self.radiatorstatus = False
	def sendEmail(self,message):
		print(message)


	def checkMail(self):
		
		text = mailh.read_email_from_gmail('tarendo')
		if text != None:
			commands = mailh.decodeMail(text)
			if commands != None:
				self.executeCommands(commands)

	def executeCommands(self,commands):

		for k, value in commands.items():
			if k == 'setMinTemp':
				self.minroomtemp = float(value)
			elif k == 'setMaxTemp':
				self.maxroomtemp = float(value)
			elif k == 'getStatus':
				self.sendEmail('here all things should be printed')
			elif k == 'getTemp':
				# self.getStatus()
				self.sendEmail('somestuffs')
			elif k == 'turnRadiatorOn':
				self.turnRadiatorOn()
			elif k == 'turnRadiatorOff':
				self.turnRadiatorOff()
			elif k == 'getLastWeeksData':
				print('hej')
			elif k == 'getLastMonthData':
				print('hej')
			else:
				print('unknown command')
	def getStatus(self):
		self.roomtemp = self.ardu.getRoomTemperature()
		self.humid = self.ardu.getRoomHumidity()
		self.pipetemp = self.ardu.getPipeTemperature()		
		
		
	def run(self):
		while True:
		    schedule.run_pending()
		    time.sleep(1)
		
if __name__ == '__main__':
	main = runner()
#	main.checktemp()
	main.run()

	
	# while True:
	# 	schedule.run_pending()
	# 	time.sleep(1)
	
	
	# f.close()
	# main.ardu.close()
	
#ardu = ArduConnection()
#time.sleep(2)
#print(ardu.getTemperature())
		
		
#ardu = ArduConnection()
#ardu.close()		
		
		
