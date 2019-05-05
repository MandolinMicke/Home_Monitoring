# -*- coding: utf-8 -*-
"""
Created on Fri Dec 21 09:04:48 2018

@author: Mikael
"""

import mail_handler as mailh


standardyaml = dict()
standardyaml['extra'] = False
standardyaml['heat_cord'] = True
standardyaml['max_temp'] = 10
standardyaml['min_temp'] = 6
standardyaml['radiator'] = False


import yaml


class StatusFileHandler:
    def __init__(self, statusfile):
        self.statusfile = statusfile
        with open(self.statusfile) as f:
            self.data = yaml.load(f)
            
        if not all([x in self.data for x in list(standardyaml.keys())]):
            self.data = standardyaml
            mailh.sendEmail('Hello. During reboot something went wrong with the previous status, please check that everything checks out.', 'tarendo', 'users', 'Survailance is needed.')
            
    
    def SaveStatus(self):       
        with open(self.statusfile,'w+') as file:
            yaml.dump(self.data,file,allow_unicode = True,encoding = 'utf-8',default_flow_style = False)
        
    def setData(self, keyword, value):
        self.data[keyword] = value
        self.SaveStatus()


        


if __name__ == '__main__':
    sf = StatusFileHandler('statusfile.yaml')
    