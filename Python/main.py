# -*- coding: utf-8 -*-
"""
Created on Fri Dec 21 09:04:48 2018

@author: Mikael
"""

#from serial import Serial

import schedule
from datetime import datetime as dt
import logging
import time
import mail_handler as mailh

import yaml


class NoRunningFilter(logging.Filter):
    def filter(self, record):
        return not record.msg.startswith('Running job')

def gts():
    n = dt.now()
    retstr = '\t' + str(n.year) + '-' + str(n.month)  + '-' + str(n.day)  + ':' + str(n.hour) + ':' + str(n.minute) + ' - ' 
            
    return retstr


class ArduConnection:
    def __init__(self,inpport = 'COM5'):
        # self.ser = Serial(port=inpport)
        logger.info(gts() + ' connected made to arduino.')
        
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
        logger.info('radiator turned on')
    
    def turnCellarRadiatorOff(self):
        logger.info('radiator turned off')
    
    def turnHeatCordOn(self):
        logger.info('heat cord turned on')

    def turnHeatCordOff(self):
        logger.info('heat cord turned off')

    def turnExtraOn(self):
        logger.info('heat extra on')

    def turnExtraOff(self):
        logger.info('heat extra off')
        
        
        
        
class StatusFileHandler:
    def __init__(self, statusfile):
        self.statusfile = statusfile
        with open(statusfile) as f:
            self.data = yaml.load(f)
    
    def SaveStatus(self):       
        with open(self.statusfile,'w+') as file:
            yaml.dump(self.data,file,allow_unicode = True,encoding = 'utf-8',default_flow_style = False)
        
    def setData(self, keyword, value):
        self.data[keyword] = value
        self.SaveStatus()

class runner:
    def __init__(self,statusfile):
        self.status = StatusFileHandler(statusfile)
        
        # self.ardu = ArduConnection()
        time.sleep(2)


        self.roomtemp = 20
        self.pipetemp = 23
        self.humid = 100
        self.fejk = False
        
#        self.getStatus()
        self.getfejkstatus()
        
        self.startup()
        schedule.every(5).seconds.do(lambda: self.hourlycheck())
        schedule.every(3).seconds.do(lambda: self.checkMail())

        
        
        logger.info(gts() + ' The system has been restarted.')
#        self.sendEmail('Systemet har startats', 'user','Uppdatering Från Tärendö')
        
    def startup(self):
        if self.status.data['radiator'] or (self.roomtemp < self.status.data['min_temp']):
            self.turnOnRadiator()
        else:
            self.turnOffRadiator()
        
        if self.status.data['heat_cord']:
            self.turnOnHeatCord()
        else:
            self.turnOffHeatCord()
            
        if self.status.data['extra']:
            self.turnOnExtra()
        else:
            self.turnOffExtra()

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
        logger.info(gts() +'pipe temperature: ' + str(self.pipetemp) + ', room temparature: ' + str(self.roomtemp) + ', humidity: ' + str(self.humid))
        self.radiatorControl()

    def radiatorControl(self):
#        print(self.roomtemp)
#        print(self.status.data['radiator'])

        if (self.roomtemp < self.status.data['min_temp']) and not self.status.data['radiator']:
            self.turnOnRadiator()
        elif (self.roomtemp > self.status.data['max_temp']) and self.status.data['radiator']:
            self.turnOffRadiator()

    def turnOnRadiator(self):
        logger.info(gts() + 'Turning on radiator')
        # self.ardu.turnCellarRadiatorOn()
#        self.sendEmail('Turning on Radiator')
        self.status.setData('radiator', True)
        
    def turnOffRadiator(self):
        logger.info('Turning off radiator')
        # self.ardu.turnCellarRadiatorOff()
#        self.sendEmail('Turning off Radiator')
        self.status.setData('radiator', False)
    
    def turnOnHeatCord(self):
        logger.info('Turning on heat cord')
        # self.ardu.turnHeatCordOn()
#        self.sendEmail('Turning off Heat Cord')
        self.status.setData('head_cord', True)
    
    def turnOffHeatCord(self):
        logger.info('Turning on heat cord')
        # self.ardu.turnHeatCordOn()
#        self.sendEmail('Turning off Heat Cord')
        self.status.setData('head_cord', False)
        
    def turnOnExtra(self):
        logger.info('Turning on heat cord')
        # self.ardu.turnExtraOn()
#        self.sendEmail('Turning off Extra')
        self.status.setData('extra', True)
    
    def turnOffExtra(self):
        logger.info('Turning on heat cord')
        # self.ardu.turnExtraOff()
#        self.sendEmail('Turning off Extra')
        self.status.setData('extra', False)
        
        
    def sendEmail(self,message,to = 'tarendo',subject = 'GUI'):
        
        mailh.sendEmail(message, 'tarendo', to, subject)

    def sendStatus(self):
        m = ''
        for k in self.status.data.keys():
            m += k + ' ' + str(self.status.data[k]) + '\n'
        m += 'room_temp ' + str(self.roomtemp) + '\n'
        m += 'pipe_temp ' + str(self.pipetemp) + '\n'
        m += 'humidity ' + str(self.humid) + '\n'
        self.sendEmail(m)
        
    def checkMail(self):
        text = mailh.read_email_from_gmail('tarendo','GUI')
        if text != None:
            commands = mailh.decodeMail(text)
            if commands != None:
                self.executeCommands(commands)
            self.sendStatus()

    def executeCommands(self,commands):
        for k, value in commands.items():
            if k == 'setMinTemp':
                self.status.setData('min_temp',float(value))
            elif k == 'setMaxTemp':
                self.status.setData('max_temp',float(value))
            elif k == 'getStatus':
#                self.getStatus()
                self.sendStatus()
                
            elif k == 'getTemp':
                # self.getStatus()
                self.sendEmail('somestuffs')
            elif k == 'turnRadiatorOn':
                self.turnRadiatorOn()
            elif k == 'turnRadiatorOff':
                self.turnRadiatorOff()
            elif k == 'getLastWeeksData':
                pass
            elif k == 'getLastMonthData':
                pass
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
    # setup logger

    my_filter = NoRunningFilter()
    logger = logging.getLogger('testlog')
    logger.setLevel(logging.DEBUG)
    
    logger.addFilter(my_filter)
    
    fh = logging.FileHandler('D:/Tärendö/Home_Monitoring/logfile.log')
    fh.setLevel(logging.DEBUG)
    logger.addHandler(fh)
    
    
    main = runner('statusfile.yaml')
#    main.checktemp()
#    main.run()
    main.sendStatus()
    
    # while True:
    #     schedule.run_pending()
    #     time.sleep(1)
    
    
    # f.close()
    # main.ardu.close()
    
#ardu = ArduConnection()
#time.sleep(2)
#print(ardu.getTemperature())
        
        
#ardu = ArduConnection()
#ardu.close()        
        
        
