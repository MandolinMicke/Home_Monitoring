# -*- coding: utf-8 -*-
"""
Created on Mon Jan  7 17:26:39 2019

@author: andmika
"""

from tkinter import Frame, Label, LabelFrame, Entry, END, StringVar, Radiobutton, Button, Toplevel, Listbox, Scrollbar, VERTICAL, Tk, IntVar

import mail_handler as mailh


class MainWindow(Frame):
    def __init__(self,master):
        Frame.__init__(self, master)
        self.master = master


        
        ## TEMPERATURE FRAME
        tempwin = LabelFrame(self.master, text="Temperatur", padx=5, pady=3)
        tempwin.pack(padx=10, pady=10)   

        self.basement_temp = StringVar()
        self.basement_temp.set("Källare: ?? ")
        
        lab = Label(tempwin, textvariable = self.basement_temp ,width=20,height=2)
        lab.grid(row=0,column=0)        

        self.pipe_temp = StringVar()
        self.pipe_temp.set("Rör: ?? ")
     
        lab = Label(tempwin, textvariable = self.pipe_temp ,width=20,height=2)
        lab.grid(row=0,column=1)    
        
        self.basement_humidity = StringVar()
        self.basement_humidity.set("Fuktighet: ?? ")
        
        lab = Label(tempwin, textvariable = self.basement_humidity ,width=20,height=2)
        lab.grid(row=0,column=2)    
        
        Button(tempwin, text="Kolla historik", width=15,height = 2, command = self.check_history).grid(row=1,column=1)
        
        ## TEMPERATURE AUTOMATION FRAME
        automationwin = LabelFrame(self.master, text = "Automation", padx=5, pady=3)
        automationwin.pack(padx=10,pady=10)
        
        lab = Label(automationwin, text = "Min temperatur" ,width=20,height=2)
        lab.grid(row=0,column=0)
        
        self.min_temp = Entry(automationwin,width = 10)
        self.min_temp.delete(0, END)
        self.min_temp.insert(0, "min")
        self.min_temp.grid(row=1,column=0)
        self.min_temp.focus_set()

        lab = Label(automationwin, text = "Max temperatur" ,width=20,height=2)
        lab.grid(row=0,column=1)
                
        self.max_temp = Entry(automationwin,width = 10)
        self.max_temp.delete(0, END)
        self.max_temp.insert(0, "max")
        self.max_temp.grid(row=1,column=1)        
        self.max_temp.focus_set()
        
        ## PLUG CONTROL
        controlnwin = LabelFrame(self.master, text = "Plug Control", padx=5, pady=3)
        controlnwin.pack(padx=10,pady=10)
        
        lab = Label(controlnwin, text = "Källar Element" ,width=20,height=2)
        lab.grid(row=0,column=0)
        
        
        self.radiator = IntVar()
        r = Radiobutton(controlnwin, text="På", variable=self.radiator, value=1,  command=self.radiator)
        r.grid(row=1,column=0)
        r = Radiobutton(controlnwin, text="Av", variable=self.radiator, value=0,  command=self.radiator)
        r.grid(row=2,column=0)
        
        
        lab = Label(controlnwin, text = "Värmeslinga" ,width=20,height=2)
        lab.grid(row=0,column=1)
        
        
        self.heatcord = IntVar()
        r = Radiobutton(controlnwin, text="På", variable=self.heatcord, value=1,  command=self.radiator)
        r.grid(row=1,column=1)
        r = Radiobutton(controlnwin, text="Av", variable=self.heatcord, value=0,  command=self.radiator)
        r.grid(row=2,column=1)

        lab = Label(controlnwin, text = "Extra" ,width=20,height=2)
        lab.grid(row=0,column=2)
        
        self.extra = IntVar()
        r = Radiobutton(controlnwin, text="På", variable=self.extra, value=1,  command=self.radiator)
        r.grid(row=1,column=2)
        r = Radiobutton(controlnwin, text="Av", variable=self.extra, value=0,  command=self.radiator)
        r.grid(row=2,column=2)
        
        
        ## STATUS WINDOW
        statuswin = LabelFrame(self.master, text="Status", padx=1, pady=3)
        statuswin.pack(padx=10, pady=10)
        
        self.status_string = StringVar()
        self.status_string.set("Hämtar data, detta kan ta några sekunder, var god vänta...")
        
        lab = Label(statuswin, textvariable = self.status_string ,width=60,height=2)
        lab.grid(row=0,column=0)    
        
        
        ## OPTION BUTTONS
        optionwin = LabelFrame(self.master, text="Options", padx=1, pady=3)
        optionwin.pack(padx=10, pady=10)
        
        Button(optionwin, text="Uppdatera", width=18,height = 2, command = self.getStatus).grid(row=0,column=0)
        Button(optionwin, text="Skicka och uppdatera", width=18,height = 2, command = self.sendUpdate).grid(row=0,column=1)
#        Button(searchwindow, text="Välj från låtlista", width=15,height = 2, command = self.from_list).grid(row=0,column=2)
        Button(optionwin, text="Stäng", width = 18, height = 2, command=self.quit).grid(row=0, column=3)
        
        
        
    def updateStatus(self,commands):       
        for k, value in commands.items():
            if k == 'extra':
                if value == 'True':
                    self.extra.set(1)
                else:
                    self.extra.set(0)
            elif k == 'radiator':
                if value == 'True':
                    self.radiator.set(1)
                else:
                    self.radiator.set(0)
            elif k == 'heat_cord':
                if value == 'True':
                    self.heatcord.set(1)
                else:
                    self.heatcord.set(0)
            elif k == 'room_temp':
                self.basement_temp.set("Källare: " + value)
            elif k == 'pipe_temp':
                self.pipe_temp.set("Rör: " + value)
            elif k == 'humidity':
                self.basement_humidity.set("Fuktighet: " + value)  
            elif k == 'min_temp':
                self.min_temp.delete(0, END)
                self.min_temp.insert(0, value)
            elif k == 'max_temp':
                self.max_temp.delete(0, END)
                self.max_temp.insert(0, value)
            
                    
    

    
    def sendUpdate(self):
        pass
    
    def getStatus(self):
        self.status_string.set("Hämtar data, var god vänta...")
        mailh.sendEmail('getStatus True\n','tarendo','tarendo','system')
        self.after(1000,self.checkUpdates)
        
        
    def checkUpdates(self):
        text = None
#        while text == None:
        text = mailh.read_email_from_gmail('GUI')
        if text != None:
            commands = mailh.decodeMail(text)
            self.updateStatus(commands)
            self.status_string.set("Data uppdaterad")
        else:
            self.after(100,self.checkUpdates)
            
    def check_history(self):
        pass
    
    def radiator(self):
        pass
    
    
if __name__ == '__main__':


    master = Tk()
    mw = MainWindow(master)
    master.after(100,mw.getStatus)
    
    master.mainloop()
    
    master.destroy()