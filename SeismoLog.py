import gtk, serial, time, gobject, threading, sys , os, datetime
from matplotlib.dates import date2num
from matplotlib.dates import num2date
from serial.tools import list_ports



class serial_thread(threading.Thread):
    stopthread = threading.Event()



    def run(self):
        #Initialize some variables
        self.stopthread.clear()
        self.period_state = False
        self.stop_state = False
        self.log_state = False
        self.reading_num = 0

        #Start a new thread for the serial communication
        gtk.threads_enter()
        textview1.get_buffer().set_text("Starting a New Serial Thread...\n\r")
        gtk.threads_leave()
        time.sleep(1)

        #Set the comport to the chosen port from the combobox
        #This gets the comport name as a string
        my_port = combobox.get_active_text()
        #This strips off the COM part of the string and leaves just the number - 1
        my_port = int(my_port[3:])-1
        gtk.threads_enter()
        textview1.get_buffer().set_text("Connecting to serial port...")
        gtk.threads_leave()
        time.sleep(1)
        try:
            self.ser = serial.Serial()
            self.ser.baudrate = 57600
            self.ser.port = my_port
            self.ser.timeout = 2
            self.ser.open()

            #restart the AD7745 chip
            gtk.threads_enter()
            textview1.get_buffer().set_text("Resetting AD7745...")
            gtk.threads_leave()
            self.ser.write("r\n\r")
            time.sleep(3)

            #print "Connected!"
            gtk.threads_enter()
            textview1.get_buffer().set_text("Connected!")
            gtk.threads_leave()

            #Start streaming back CDC counts
            self.ser.write("m\n\r")
            time.sleep(1)



            #Start Collecting the Data
            self.collect_data()

        except:
            #print "Failed to connect on", my_port
            pass

    def collect_data(self):
            #Do this loop as long as stopthread is clear#First flush all the input data
            self.ser.flushInput()       #First flush all the input data
            while not self.stopthread.isSet():
                raw=str(self.ser.readline())
                #print raw
                raw=raw.replace("\n","").replace("\r","")
                raw=raw.split(",")
                try:
                    point=(int(raw[0]))
                    #print point

                except:
                    gtk.threads_enter()
                    textview1.get_buffer().set_text("No CDC counts - Press stop and choose another port")
                    gtk.threads_leave()
                    break

                if self.log_state == 0:
                    #Print Out to the textview window
                    try:
                        if not self.period_state:
                            gtk.threads_enter()
                            textview1.get_buffer().insert(textview1.get_buffer().get_end_iter(),  "\n" + str(point))
                            textview1.scroll_to_iter(textview1.get_buffer().get_end_iter(),0)
                            gtk.threads_leave()
                            line_count = textview1.get_buffer().get_line_count()
                            print line_count
                            if line_count > 1000:
                                gtk.threads_enter()
                                textview1.get_buffer().set_text("")
                                gtk.threads_leave()

                    except:
                        pass



                #Process the Period
                try:
                    if self.period_state:
                        gtk.threads_enter()
                        textview1.get_buffer().set_text("We will be printing out the period here")
                        gtk.threads_leave()

                except:
                    pass

                #Process the Log
                #If a new day then start saving in a new file



                '''
                print datetime.date.today()


                if self.today != datetime.date.today():
                    self.file.close()
                    self.log()
                '''
                try:

                    if self.log_state:
                        self.reading_num += 1
                        self.save_data(self.reading_num,point)

                except:
                    pass


    def save_data(self,reading_num,reading):

        value_1 = "%.11f" % date2num(datetime.datetime.now())
        value = (reading_num,reading,value_1)
        file_line = str(value)
        self.file.write (file_line)
        self.file.write ("\n")


    #------------------------
    #Process incoming buttons
    #------------------------
    def stop(self):
        #Try to close the Log File
        try:
            self.file.close()
        except:
            pass

        self.stopthread.set()


    def period(self):
        self.period_state = not self.period_state

    def log(self):
        self.log_state = True
        self.reading_num = 0

        #clear the log file
        self.today = str(datetime.date.today())


        self.logname = '%s.txt' % self.today
        open(self.logname, 'w').close()
        #Now open the log file for writing

        self.file = open(self.logname, 'a')

class Handler:
    def __init__(self):
        self.period = False
    def on_delete_window(self, *args):
        print "shut HER down"
        gtk.main_quit(*args)

        #If there is a serial thread started stop it so we can shutdown cleanly
        try:
            self.st.stop()
        except:
            pass

    def stop_pressed(self, connect):
        #If there is a serial thread started stop it so we can shutdown cleanly

        try:
            self.st.stop()
        except:
            textview1.get_buffer().set_text("You have to Connect")
            pass


    def connect_pressed(self, connect):
        self.st = serial_thread()
        self.st.start()

    def log_pressed(self, connect):

        try:
            self.st.log()
            textview1.get_buffer().set_text("Logging to file log.txt")
        except:
            textview1.get_buffer().set_text("You have to Connect")
            pass

    def period_pressed(self, connect):
        try:
            self.st.period()
        except:
            textview1.get_buffer().set_text("You have to Connect")
            pass

    def PortChanged(self, connect):
        print combobox.get_active_text()


builder = gtk.Builder()
builder.add_from_file("Kater.glade")
builder.connect_signals(Handler())

stop = builder.get_object("Stop")
textview1 =  builder.get_object("textview1")


#Build the SerialPort ComboBox
#First Build the Box
combobox = builder.get_object("SerialPort")
cell = gtk.CellRendererText()
combobox.pack_start(cell)
combobox.add_attribute(cell, 'text', 0)

#Find the ports
#list_ports.comports()
comports = serial.tools.list_ports.comports()

for port in comports:
    print port[0]
    #Now append the ports to the cells in the combobox
    combobox.append_text(port[0])

#Go ahead and choose the item in the list so that the box is not blank
combobox.set_active(0)

window = builder.get_object("window1")
window.show_all()

gobject.threads_init()
gtk.threads_init()
gtk.main()

