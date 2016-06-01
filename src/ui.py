#!/usr/bin/env python

from Tkinter import *
import time
import datetime

from hist import History
import themes

from readcycle import Cycle
#from fakecycle import Cycle

class FakeLCD14:
    """fake 14-segment lcd display"""

    def __init__(self, canvas, theme, bgtext, fgtext, x, y):
        """create new display
        
        Args:
            canvas: containing canvas
            theme: theme specifying fonts and colors
            bgtext: default background text, usually a sequence of tildes (all segments on)
            fgtext: initial foreground text
            x: horizontal position on canvas
            y: vertical position on canvas
        """

        self.canvas = canvas
        self.textbg = self.canvas.create_text(x, y, text=bgtext, fill=theme.inactive_color, font=theme.small_font)
        self.textfg = self.canvas.create_text(x, y, text=fgtext, fill=theme.active_color, font=theme.small_font)


    def set_text(self, text):
        self.canvas.itemconfig(self.textfg, text=text)


class FakeLCD7:
    """fake 7-segment lcd display"""

    def __init__(self, canvas, theme, bgtext, fgtext, x, y):
        """create new display
        
        Args:
            canvas: containing canvas
            theme: theme specifying fonts and colors
            bgtext: default background text, usually a sequence of 8's
            fgtext: initial foreground text
            x: horizontal position on canvas
            y: vertical position on canvas
        """
        self.canvas = canvas
        self.textbg = self.canvas.create_text(x, y, text=bgtext, fill=theme.inactive_color, font=theme.large_font)
        self.textfg = self.canvas.create_text(x, y, text=fgtext, fill=theme.active_color, font=theme.large_font)

    def set_text(self, text):
        self.canvas.itemconfig(self.textfg, text=text)


class NumberPanel(Canvas):
    """a panel for displaying numerical data, labeled with some info text"""

    active = True
    orig_width = 70
    orig_height = 40

    def __init__(self, root, info_txt, info_x, info_y, data_fmt, data_x, data_y):
        """creates a new panel

        Args:
            root: tkinter root to attach to
            info_txt: label displayed above the number
            info_x: horizontal position of info text
            info_y: vertical position of info text
            data_fmt: format of the numerical data to be displayed, e.g., 88:88 for times
            data_x: horizontal position of number display
            data_y: vertical position of number display
        """
        Canvas.__init__(self, root, width=self.orig_width, height=self.orig_height, highlightthickness=0, background=root.theme.bg_color)

        # "background" text
        info_fmt = "~" * len(info_txt)

        self.lcd_info = FakeLCD14(self, root.theme, info_fmt, info_txt, info_x, info_y)
        self.lcd_data = FakeLCD7(self, root.theme, data_fmt, "", data_x, data_y)


class Clock (NumberPanel):
    """UI element for displaying time"""

    def __init__(self, root, tformat):
        """creates a new clock

        Args:
            root: tkinter root to attach to
            tformat: datetime time format string, e.g. "%M:%S"
        """
        NumberPanel.__init__(self, root, "TIME", 47, 10, "88:88", 35, 30)
        
        # state
        self.colon = False
        self.time_w_colon = tformat
        self.time_wo_colon = tformat.replace(":", " ");
        
    def update(self, time):
        """updates the time on display and flashes the colon
        
        Args:
            time: datetime object with current time
        """
        self.colon = not self.colon

        if self.colon:
            ts = time.strftime(self.time_w_colon)
        else:
            ts = time.strftime(self.time_wo_colon)

        self.lcd_data.set_text(ts)


class Speed (NumberPanel):
    """UI element for displaying speed"""

    def __init__(self, root):
        NumberPanel.__init__(self, root, "SPEED", 37, 10, "88.8", 40, 30)

    def update(self, speed):
        """updates the speed on display, shown rounded to one decimal

        Args:
            speed: speed as a float
        """

        text = "%2.1f" % speed
        if speed < 10:
            text = "    " + text
        self.lcd_data.set_text(text)


class Rpm (NumberPanel):
    """UI element for displaying revolutions per minute (RPM)"""

    def __init__(self, root):
        NumberPanel.__init__(self, root, "RPM", 38, 10, "888", 30, 30)

    def update(self, rpm):
        """updates RPM on display, shown rounded to the next integer
        
        Args:
            rpm: revolutions per minute, given as a float
        """

        text = "%d" % rpm
        if rpm < 100:  # padding, 4 spaces equal a character
            text = "    " + text 
        if rpm < 10:
            text = "    " + text
        self.lcd_data.set_text(text)

class Revolutions (NumberPanel):
    """UI element for displaying the overall number of revolutions"""

    def __init__(self, root):
        NumberPanel.__init__(self, root, "REVS", 38, 10, "8888", 30, 30)

    def update(self, revs):
        """updates number of revolutions

        Args:
            revs: number of revolutions, given as an integer
        """

        text = "%d" % revs
        if revs < 1000:  # padding
            text = "    " + text
        if revs < 100:
            text = "    " + text
        if revs < 10:
            text = "    " + text
        self.lcd_data.set_text(text)


class SpeedGraph (Canvas):
    """UI element for graphing the speed history"""

    def __init__(self, root):
        Canvas.__init__(self, root, width=102, height=40, highlightthickness=0, background=root.theme.bg_color)
        self.theme = root.theme
        self.history = History(100)
        self.height = 40

    def add(self, speed):
        """adds a new data point to the history

        Args:
            speed: current speed, given as a float
        """
        y =  self.height - speed/30. * self.height
        self.history.add(y)
        self.plot()

    def plot(self):
        """displays the current speed history as a line graph

        Note: Currently, this method deletes all previous line objects
        and creates new ones. This is rather slow and could be improved.
        """

        self.delete("all")

        for x,y in enumerate(self.history):
            prev_x = max(x-1, 0)
            if x == 0: prev_y = y

            self.create_line(prev_x,prev_y,x,y, width=2, fill=self.theme.active_color)
            prev_y = y
    

class UI(Tk):
    """ Controller class connecting the UI with the bicycle"""

    # update intervals for UI components
    update_interval_poll = 1000  # poll more frequently to
    update_interval_time = 1000
    update_interval_speed = 1000
    update_interval_speed_graph = 1000
    update_interval_rpm = 1000
    update_interval_revolutions = 1000

    # state
    speed = 0.

    def __init__(self, cycle, theme):
        """
        Args:
            cycle: a cycle model object
            theme: a theme class
        """

        self.theme = theme
        Tk.__init__(self)

        # store cycle
        self.cycle = cycle

        # set up ui properties
        self.wait_visibility(self)
        self.wm_attributes('-alpha',0.8)
        self.resizable(width=FALSE, height=FALSE)
        self.wm_attributes("-topmost", 1)
        self.geometry('400x45+950+0')
        self.configure(background=self.theme.bg_color)

        # key stuff
        self.bind_all('<Key>', self.key)

        # set up window
        self.l_time = Clock(self, "%M:%S")
        self.l_speed = Speed(self)
        self.l_rpm = Rpm(self)
        self.l_speedgraph = SpeedGraph(self)
        self.l_revs = Revolutions(self)
        
        # placement
        self.l_time.pack(side=LEFT)
        self.l_speed.pack(side=LEFT)
        self.l_rpm.pack(side=LEFT)
        self.l_revs.pack(side=LEFT)
        self.l_speedgraph.pack(side=LEFT)

        # run loop
        self.poll()
        self.update_ride_time()
        self.update_speed()
        self.update_rpm()
        self.update_revolutions()
        self.update_speed_graph()
        self.mainloop()

    def key(self, event):
        """keyboard event processing"""

        if event.char == 't':
            element =  self.l_time
        elif event.char == 's':
            element =  self.l_speed
        elif event.char == 'r':
            element =  self.l_rpm
        elif event.char == 'v':
            element =  self.l_revs
        else:
            return
            
        if element.active:
            element.config(width=0)
        else:
            element.config(width=element.orig_width)
        element.active = not element.active 

    def update_time(self):
        """update the time UI element with current wall clock time"""

        t = datetime.datetime.now()
        self.l_time.update(t)

        # re-schedule
        self.after(self.update_interval_time, self.update_time)

    def update_ride_time(self):
        """update the time UI element with current ride time from model"""

        ridetime = self.cycle.get_ride_time()
        self.l_time.update(ridetime)

        # re-schedule
        self.after(self.update_interval_time, self.update_ride_time)

    def update_speed(self): 
        """update the speed UI element with current speed from model"""

        speed = self.cycle.get_speed()       
        self.l_speed.update(speed)

        # re-schedule
        self.after(self.update_interval_speed, self.update_speed)

    def update_speed_graph(self):
        """update the speed graph with current speed from model"""

        self.l_speedgraph.add(self.cycle.get_speed())

        # re-schedule
        self.after(self.update_interval_speed_graph, self.update_speed_graph)


    def update_rpm(self): 
        """update the RPM display with current RPM from model"""
       
        self.l_rpm.update(self.cycle.get_rpm())

        # re-schedule
        self.after(self.update_interval_rpm, self.update_rpm)

    def update_revolutions(self): 
        """update the revolution counter with current count from model"""
       
        self.l_revs.update(self.cycle.get_revolutions())

        # re-schedule
        self.after(self.update_interval_revolutions, self.update_revolutions)


    def poll(self):
        """update the cycle model with new data from controller"""
        self.cycle.poll()
        
        self.after(self.update_interval_poll, self.poll)


# launch UI
if __name__ == "__main__":   
    cycle = Cycle()
    ui = UI(cycle, themes.WhiteOnBlack)

