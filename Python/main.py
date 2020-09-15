# -*- coding: utf-8 -*-
"""
Created on Fri Dec 21 09:04:48 2018

@author: Mikael
"""

#

import schedule
import datetime as dt
import logging
import time
import mail_handler as mailh

import yaml
import ArduinoConnection as AC
import tempmeasure

from StatusFileHandler import StatusFileHandler
from WifiSockets import WifiSockets

class NoRunningFilter(logging.Filter):
    # class to keep logger from logging unimportant things.
    def filter(self, record):
        return not record.msg.startswith('Running job')

def gts():
    # help function to create string for date and time
    n = dt.datetime.now()
    retstr = '\t' + str(n.year) + '-' + str(n.month)  + '-' + str(n.day)  + ':' + str(n.hour) + ':' + str(n.minute) + ' - ' 
            
    return retstr


def getDataFromLoggfile(file,timespan = 'week'):
    if timespan == 'week':
        wanteddate = dt.datetime.now() - dt.timedelta(days=7)
    elif timespan == 'month':
        wanteddate = dt.datetime.now() - dt.timedelta(days=30)
    elif timespan == 'three_months':
        wanteddate = dt.datetime.now() - dt.timedelta(days=90)
    elif timespan == 'half_year':
        wanteddate = dt.datetime.now() - dt.timedelta(days=180)
    elif timespan == 'year':
        wanteddate = dt.datetime.now() - dt.timedelta(days=365)
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
    def __init__(self,statusfile,logger):
        # get the previous status during startup
        self.status = StatusFileHandler(statusfile)
        self.logger = logger
        self.wifiplug = WifiSockets()
        # start serial connection to arduino
        # self.ardu = AC.ArduConnection()
        self.ardu = tempmeasure.TempMeasurment()
        time.sleep(2)
        
        # set dummy values for 
        self.roomtemp = 0
        self.pipetemp = 0
        self.humid = 0
        print('here')
        # measure the values
        self.getStatus()
        print('hereagain')
        # reset the initial status
        self.startup()
        schedule.every().hour.do(lambda: self.hourlycheck())
        schedule.every(3).seconds.do(lambda: self.checkMail())
        print('should do something now')
        
        # inform that the system has been rebooted
        self.logger.info(gts() + ' The system has been restarted.')
        self.sendEmail('The system has been rebooted', 'users','Update')
        
    def startup(self):
        # resets the previous status of the system

        # reset radiator
        if self.status.data['radiator'] or (self.roomtemp < self.status.data['min_temp']):
            self.turnRadiatorOn()
        else:
            self.turnRadiatorOff()
        # reset heat cord
        if self.status.data['heat_cord']:
            self.turnHeatCordOn()
        else:
            self.turnHeatCordOff()
        # reset the extra plug
        if self.status.data['extra']:
            self.turnExtraOn()
        else:
            self.turnExtraOff()



    def hourlycheck(self):
        # hourly check of the system
        # get status and update logfile
        self.getStatus()
        self.logger.info('HourlyStatus: ' + gts() +'pipe temperature: ' + str(self.pipetemp) + ', room temparature: ' + str(self.roomtemp) + ', humidity: ' + str(self.humid))
        # check if the temperature is low/ high enough to change the radiator settings
        self.radiatorControl()

    def radiatorControl(self):
        # control radiator depending on temperature and send update
        if (self.roomtemp < self.status.data['min_temp']) and not self.status.data['radiator']:
            self.turnRadiatorOn()
            self.sendEmail('The Radiator has been turned on due to low temperature.', 'users','Update')
        elif (self.roomtemp > self.status.data['max_temp']) and self.status.data['radiator']:
            self.turnRadiatorOff()
            self.sendEmail('The Radiator has been turned off due to high temperature.', 'users','Update')

    def turnRadiatorOn(self):
        # turn on radiator
        self.logger.info(gts() + 'Turning on radiator')
        # self.ardu.turnCellarRadiatorOn()
        self.wifiplug.turn_on('plug1')
        self.status.setData('radiator', True)
        
    def turnRadiatorOff(self):
        # turn of radiator
        self.logger.info(gts() + 'Turning off radiator')
        # self.ardu.turnCellarRadiatorOff()
        self.wifiplug.turn_off('plug1')
        self.status.setData('radiator', False)
    
    def turnHeatCordOn(self):
        # turn on heat cord
        self.logger.info(gts() + 'Turning on heat cord')
        # self.ardu.turnHeatCordOn()
        # self.wifiplug.turn_on('plug2')
        self.status.setData('heat_cord', True)
    
    def turnHeatCordOff(self):
        # turn off heat cord
        self.logger.info(gts() + 'Turning on heat cord')
        # self.ardu.turnHeatCordOff()
        # self.wifiplug.turn_off('plug2')
        self.status.setData('heat_cord', False)
        
    def turnExtraOn(self):
        # turn extra plug on
        self.logger.info(gts() + 'Turning on extra plug')
        # self.ardu.turnExtraOn()
        self.wifiplug.turn_on('plug3')
        self.status.setData('extra', True)
    
    def turnExtraOff(self):
        # turn extra plug off
        self.logger.info(gts() + 'Turning off extra plug')
        # self.ardu.turnExtraOff()
        self.wifiplug.turn_off('plug3')
        self.status.setData('extra', False)
        
        
    def sendEmail(self,message,to = 'tarendo',subject = 'GUI'):
        # generic email sender
        mailh.sendEmail(message, 'tarendo', to, subject)

    def sendStatus(self):
        # send status update
        m = ''
        # current status 
        for k in self.status.data.keys():
            m += k + ' ' + str(self.status.data[k]) + '\n'
        # current temperature and humidity
        m += 'room_temp ' + str(self.roomtemp) + '\n'
        m += 'pipe_temp ' + str(self.pipetemp) + '\n'
        m += 'humidity ' + str(self.humid) + '\n'
        # send the email
        self.sendEmail(m)
        
    def sendHistory(self,span='week'):
        # send the history data
        data = getDataFromLoggfile(self.logger.handlers[0].baseFilename,span)
        m = 'History\n'
        for d in data:
            m += str(d[0]) +';'
            m += str(d[1]) +';'
            m += str(d[2]) +';'
            m += str(d[3]) +'\n'
        self.sendEmail(m)
        
    def checkMail(self):
        # check email in case of request from user
        text = mailh.read_email_from_gmail('system')
        # if a responce is found, decode the email
        if text != None:
            commands = mailh.decodeMail(text)
            # if the email contains information, run all commands
            if commands != None:
                self.executeCommands(commands)

            # if the email read didn't fail, send status
            if not any([x in commands for x in ['FAIL', 'getHistory']]):
                print(any([x not in commands for x in ['FAIL', 'getHistory']]))
                self.getStatus()
                self.sendStatus()


    def executeCommands(self,commands):
        
        for k, value in commands.items():
            if k == 'setMinTemp':
                self.status.setData('min_temp',float(value))
            elif k == 'setMaxTemp':
                self.status.setData('max_temp',float(value))
            elif k == 'getTemp':
                # not used atm
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
            elif k == 'getHistory':
                self.sendHistory(value)
            elif k == 'FAIL':
                pass #logger.info(gts() + 'Could not connect to mail')
            else:
                print('unknown command')
    
    def getStatus(self):
        # measure all temperatures and humidity
        self.roomtemp = self.ardu.getRoomTemperature()
        self.humid = self.ardu.getRoomHumidity()
        self.pipetemp = self.ardu.getPipeTemperature()
        
        
    def run(self):
        # run schedule
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
    
    
    main = runner('statusfile.yaml',logger)

    main.run()


        
        
