# -*- coding: utf-8 -*-
"""
Created on Sun Jan 13 07:53:41 2019

@author: andmika
"""
from serial import Serial, SerialException
import sys
import glob

def serial_ports():
    """ Lists serial port names

        :raises EnvironmentError:
            On unsupported or unknown platforms
        :returns:
            A list of the serial ports available on the system
    """
    if sys.platform.startswith('win'):
        ports = ['COM%s' % (i + 1) for i in range(256)]
    elif sys.platform.startswith('linux') or sys.platform.startswith('cygwin'):
        # this excludes your current terminal "/dev/tty"
        ports = glob.glob('/dev/tty[A-Za-z]*')
    elif sys.platform.startswith('darwin'):
        ports = glob.glob('/dev/tty.*')
    else:
        raise EnvironmentError('Unsupported platform')

    result = []
    for port in ports:
        try:
            s = Serial(port)
            s.close()
            result.append(port)
        except (OSError, SerialException):
            pass
    return result



class ArduConnection:
    def __init__(self,inpport = None):
        if inpport == None:
            ports = serial_ports()
            inpport = ports[0]
        self.ser = Serial(port=inpport)

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
        return self.sendAndRecive('radiator_on')

    def turnCellarRadiatorOff(self):
        return self.sendAndRecive('radiator_off')

    def turnHeatCordOn(self):
        return self.sendAndRecive('heatcord_on')

    def turnHeatCordOff(self):
        return self.sendAndRecive('heatcord_off')

    def turnExtraOn(self):
        return self.sendAndRecive('extra_on')

    def turnExtraOff(self):
        return self.sendAndRecive('extra_off')
        

if __name__ == '__main__':
    pass