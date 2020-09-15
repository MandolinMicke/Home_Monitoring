import pyHS100 as ph
from itertools import chain
from time import sleep

ips = {}
ips['plug1'] = '192.168.8.107'
# ips['plug2'] = '192.168.8.108'
ips['plug3'] = '192.168.8.109'

class WifiSockets():
    """ handles the tp link wifi sockets

    """

    def __init__(self,known_ips = ips):
        sleep(1)
        self.plugs = {}
        for name, ip in known_ips.items():
            new_plug = self.get_plug(name,ip)
            self.plugs[name] = new_plug
            ## TODO:fix when no plug is there
            print(name)
    def get_plug(self,name,know_ip= None):
        """ gets the plug of that name

            Returns ph.SmartPlug
        """
        if know_ip != None:
            try: 
                plug = ph.SmartPlug(know_ip)
                if  plug.alias == name:
                    return plug
            except ph.smartdevice.SmartDeviceException:
                pass
        return self._find_plug(name)

    def _find_plug(self,name,baseip = '192.168.8.'):
        """ will find a plug with a sertain name

        """

        # do a smart search, starts with 100 then go up, then go back
        for i in chain(range(100,256),range(100)):
            
            try: 
                plug = ph.SmartPlug('192.168.8.' + str(i))
                if  plug.alias == name:
                    return plug
            except ph.smartdevice.SmartDeviceException:
                pass
        return None

    def turn_on(self,plug):
        """ sets a plug to be on

        """
#        print(plug)
        if plug in self.plugs:
            self.plugs[plug].turn_on()

    def turn_off(self,plug):
        """ sets a plug to be off

        """
        print(plug)
        if plug in self.plugs:
            self.plugs[plug].turn_off()

    # def get_usage_today(self,plug):
    #     if plug in self.plugs:
    #         data = self.plugs[plug].get_emeter_daily()

if __name__ == '__main__':
    wf = WifiSockets()
    wf.turn_off('plug1')
    
