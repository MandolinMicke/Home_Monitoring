import Adafruit_DHT as ada


class TempMeasurment:
    def __init__(self):
        self.pipepin = 2
        self.roompin = 27
        self.sensor = ada.DHT11

    def getPipeTemperature(self):
        _, t = ada.read_retry(self.sensor,self.pipepin)
        if t == None:
            t = -99
        return t

    def getRoomTemperature(self):
        _, t = ada.read_retry(self.sensor,self.roompin)
        if t == None:
            t = -99
        return float(t)

    def getRoomHumidity(self):
        h, _ = ada.read_retry(self.sensor,self.roompin)
        if h == None:
            h = -99
        return float(h)

if __name__ == '__main__':
    tm = TempMeasurment()
    print(tm.getRoomTemperature())
    print(tm.getPipeTemperature())
    print(tm.getRoomHumidity())