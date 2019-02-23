# -*- coding: utf-8 -*-
"""
Created on Fri Dec 21 09:04:48 2018

@author: Mikael
"""

#

import schedule
from datetime import datetime as dt
import logging
import time
import mail_handler as mailh

import yaml
import ArduinoConnection as AC

class NoRunningFilter(logging.Filter):
    def filter(self, record):
        return not record.msg.startswith('Running job')

def gts():
    n = dt.now()
    retstr = '\t' + str(n.year) + '-' + str(n.month)  + '-' + str(n.day)  + ':' + str(n.hour) + ':' + str(n.minute) + ' - ' 
            
    return retstr
                
class StatusFileHandler:
    def __init__(self, statusfile):
        self.statusfile = statusfile
        with open(self.statusfile) as f:
            self.data = yaml.load(f)
    
    def SaveStatus(self):       
        with open(self.statusfile,'w+') as file:
            yaml.dump(self.data,file,allow_unicode = True,encoding = 'utf-8',default_flow_style = False)
        
    def setData(self, keyword, value):
        self.data[keyword] = value
        self.SaveStatus()

def getDataFromLoggfile(file,timespan = 'week'):
    if timespan == 'week':
        wanteddate = dt.datetime.now() - dt.timedelta(days=7)
    elif timespan == 'month':
        wanteddate = dt.datetime.now() - dt.timedelta(days=30)
    elif timespan == 'threemonts':
        wanteddate = dt.datetime.now() - dt.timedelta(days=90)
    elif timespan == 'halfyear':
        wanteddate = dt.datetime.now() - dt.timedelta(days=180)
    elif timespan == 'year':
        wanteddate = dt.datetime.now() - dt.timedelta(days=180)
    else:
        wanteddate = dt.datetime.now() - dt.timedelta(days=7)
    with open(file,'r') as f:
        retlist =[]
        for line in f.readlines():
            if 'HourlyStatus' in line:
                linedata = line.split(' ')
                date = linedata[1].split('-')
                curtime = dt.datetime(int(date[0]),int(date[1]),int(date[2].split(':')[0]),int(date[2].split(':')[1]),int(date[2].split(':')[2]))
                tmpdata = []
                if (curtime > wanteddate):
                    tmpdata.append(curtime)
                    tmpdata.append(float(linedata[5].strip(',')))
                    tmpdata.append(float(linedata[8].strip(',')))
                    tmpdata.append(float(linedata[10].strip('\n')))
                    retlist.append(tmpdata)
                    
    return retlist

class runner:
    def __init__(self,statusfile):
        self.status = StatusFileHandler(statusfile)
        
        self.ardu = AC.ArduConnection()
        time.sleep(2)

        self.roomtemp = 20
        self.pipetemp = 23
        self.humid = 100
        self.fejk = False
        
        self.getStatus()
#        self.getfejkstatus()
        
        self.startup()
        
        schedule.every().hour.do(lambda: self.hourlycheck())
        schedule.every(3).seconds.do(lambda: self.checkMail())

        
        
        logger.info(gts() + ' The system has been restarted.')
#        self.sendEmail('Systemet har startats', 'user','Uppdatering Från Tärendö')
        
    def startup(self):
        if self.status.data['radiator'] or (self.roomtemp < self.status.data['min_temp']):
            self.turnRadiatorOn()
        else:
            self.turnRadiatorOff()
        
        if self.status.data['heat_cord']:
            self.turnHeatCordOn()
        else:
            self.turnHeatCordOff()
            
        if self.status.data['extra']:
            self.turnExtraOn()
        else:
            self.turnExtraOff()

    def getfejkstatus(self):
        if self.roomtemp <4 or self.fejk:
            self.roomtemp += 1
            self.fejk = True
            if self.roomtemp >20:
                self.fejk = False
        else:
            self.roomtemp -= 1        
            

    def hourlycheck(self):
        self.getStatus()
#        self.getfejkstatus()
        logger.info('HourlyStatus: ' + gts() +'pipe temperature: ' + str(self.pipetemp) + ', room temparature: ' + str(self.roomtemp) + ', humidity: ' + str(self.humid))
        self.radiatorControl()

    def radiatorControl(self):

        if (self.roomtemp < self.status.data['min_temp']) and not self.status.data['radiator']:
            self.turnRadiatorOn()
        elif (self.roomtemp > self.status.data['max_temp']) and self.status.data['radiator']:
            self.turnRadiatorOff()

    def turnRadiatorOn(self):
        logger.info(gts() + 'Turning on radiator')
        self.ardu.turnCellarRadiatorOn()
        self.status.setData('radiator', True)
        
    def turnRadiatorOff(self):
        logger.info(gts() + 'Turning off radiator')
        self.ardu.turnCellarRadiatorOff()
        self.status.setData('radiator', False)
    
    def turnHeatCordOn(self):
        logger.info(gts() + 'Turning on heat cord')
        self.ardu.turnHeatCordOn()
        self.status.setData('heat_cord', True)
    
    def turnHeatCordOff(self):
        logger.info(gts() + 'Turning on heat cord')
        self.ardu.turnHeatCordOff()
        self.status.setData('heat_cord', False)
        
    def turnExtraOn(self):
        logger.info(gts() + 'Turning on heat cord')
        self.ardu.turnExtraOn()
        self.status.setData('extra', True)
    
    def turnExtraOff(self):
        logger.info(gts() + 'Turning on heat cord')
        self.ardu.turnExtraOff()
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
        
    def sendHistory(self,span='week'):
        data = getDataFromLoggfile(logger.handlers[0].baseFilename,span)
        m = 'History\n'
        for d in data:
            m += str(d[0]) +';'
            m += str(d[1]) +';'
            m += str(d[2]) +';'
            m += str(d[3]) +'\n'
        self.sendEmail(m)
        
    def checkMail(self):
        text = mailh.read_email_from_gmail('system')
        if text != None:
            commands = mailh.decodeMail(text)
            print(commands)
            if commands != None:
                self.executeCommands(commands)

            # always send status after an email is recived???
            
#            self.getfejkstatus()
            if 'FAIL' not in commands:
                self.getStatus()
                self.sendStatus()


    def executeCommands(self,commands):
        for k, value in commands.items():
            if k == 'setMinTemp':
                self.status.setData('min_temp',float(value))
            elif k == 'setMaxTemp':
                self.status.setData('max_temp',float(value))
            elif k == 'getTemp':
                self.getStatus()
                self.sendEmail('somestuffs')
            elif k == 'radiatorControl':
                if value == 'True':
                    self.turnRadiatorOn()
                else:
                    self.turnRadiatorOff()
            elif k == 'heatCordControl':
                if value == 'True':
                    self.turnHeatCordOn()
                else:
                    self.turnHeatCordOff()    
            elif k == 'extraControl':
                if value == 'True':
                    self.turnExtraOn()
                else:
                    self.turnExtraOff()    
            elif k == 'getLastWeeksData':
                pass
            elif k == 'getLastMonthData':
                pass
            elif k == 'FAIL':
                logger.info(gts() + 'Could not connect to mail')
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
    logfile = '/home/pi/local/Home_Monitoring/logfile.log'
#    logfile = 'D:/Tärendö/Home_Monitoring/logfile.log'
    fh = logging.FileHandler(logfile)
    
    fh.setLevel(logging.DEBUG)
    logger.addHandler(fh)
    
    
    main = runner('statusfile.yaml')

    main.run()


        
        
