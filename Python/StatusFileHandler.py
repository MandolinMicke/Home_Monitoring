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
            mailh.sendEmail('Hej \n Systemet har startats om och statusen från innan var korrupt. \n Logga in och kolla så allt är som du vill.', 'tarendo', 'user', 'Tillsyn krävs i Tärendö')
            
    
    def SaveStatus(self):       
        with open(self.statusfile,'w+') as file:
            yaml.dump(self.data,file,allow_unicode = True,encoding = 'utf-8',default_flow_style = False)
        
    def setData(self, keyword, value):
        self.data[keyword] = value
        self.SaveStatus()


        


if __name__ == '__main__':
    sf = StatusFileHandler('statusfile.yaml')
    