import serial
import time
import datetime
import traceback
import sys
from hist import History


class Cycle:
    """
    Model class for communication with an Arduino connected to a
    stationary bicycle
    """

    # state
    speed = 0
    delta = 0
    ridetime = 0
    revolutions = 0
    rpm = 0

    # serial communication options
    _rate = 9600
    _port = '/dev/ttyACM0'
    

    def __init__(self):
        try:  # connect to arduino
            self.ser = serial.Serial(self._port, self._rate, timeout=0.1) 
            self.ser.setDTR(1)
            print "Serial connection is open:", self.ser.isOpen()
        except:
            print "Arduino not connected"
            sys.exit(1)

        self.speed_hist = History(2)



    def poll(self):
        """reads data from Arduino
        
        Data protocol is lines of key-value pairs:
            .t: active ride time in milliseconds (e.g., t=1231)
             v: overall number of revolutions (e.g., v=10)
             d: duration of most recent revolution in milliseconds (e.g., d=800) 
        """

        data_left = self.ser.inWaiting() 
        if data_left > 0:                        
            try:
                print "trying to read"
                data = self.ser.readlines()
                print "nlines", len(data)
                print "".join(data)
                for line in data:
                    print line,
                    slots = line.strip().split("=")

                    if len(slots) != 2:
                        continue # skip malformed lines
                    key, value = slots
                    #if key == "speed" or key == "s": 
                    #    self.speed = float(value)
                    #    self.speed_hist.add(self.speed)
                    #if key == "rpm" or key == "r":
                    #    self.rpm = float(value)
                    if key == "ridetime" or key == "t":
                        self.ridetime = int(value)
                    elif key == "revolutions" or key == "v":
                        self.revolutions = int(value)
                    elif key == "d": # digispark sends delta instead of speed
                        self.delta = int(value)

            except KeyboardInterrupt:
                # user tried to kill program
                self.ser.close()
                raise
            except:
                # something went wrong, print trace
                # this can also occur on Arduino read errors, so don't fail here
                traceback.print_exc(file=sys.stdout)
                pass
                    
        
    def get_rpm(self):
        """computes rpm from delta"""

        if self.delta == 0:
            self.rpm = 0
        else:
            self.rpm = 60000./self.delta

        return self.rpm

    def get_revolutions(self):
        return self.revolutions

    def get_ride_time(self):
        """parses ride time from millisecond timestamp"""

        return datetime.datetime.fromtimestamp(self.ridetime/1000.)

    def get_speed(self):
        """calculate speed from rpm"""

        # function determined empirically from stock meter
        self.speed = self.get_rpm()/3.5 

        # debug print
        print "speed", self.speed
        return self.speed



if __name__ == "__main__":
    cycle = Cycle()
    while True:
        cycle.poll()
        print cycle.get_speed()
        time.sleep(0.2)
            
        
