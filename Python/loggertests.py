# -*- coding: utf-8 -*-
"""
Created on Sun Dec 30 10:37:13 2018

@author: andmika
"""
import logging

class NoRunningFilter(logging.Filter):
    def filter(self, record):
        return not record.msg.startswith('Running job')
    
my_filter = NoRunningFilter()
logger = logging.getLogger('testlog')
logger.setLevel(logging.DEBUG)

logger.addFilter(my_filter)

fh = logging.FileHandler('D:/Tärendö/Home_Monitoring/testlog.log')
fh.setLevel(logging.DEBUG)
logger.addHandler(fh)

logger.debug('debug')

logger.info('Running job: something')
logger.info('info')




