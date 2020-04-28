from tkinter import *
import time
import datetime
import urllib.request
import pickle
import math
import socket
from win10toast import ToastNotifier

notification_api = ToastNotifier()

window = Tk()

window.title("Internet Connection Status")

window.geometry('220x90')

outage_log = open("outage_log.txt",'a')

def getLastOutageTime():
    f = open('last_outage_time.pkl', 'rb')
    ret = pickle.load(f)
    f.close()
    return ret

def setLastOutageTime(outagetime):
    f = open('last_outage_time.pkl', 'wb')
    pickle.dump(outagetime, f)
    f.close()

def updateTimeSinceLastOutage():
    global LASTOUTAGETIME
    global connectionAlive
    difference = datetime.datetime.now() - LASTOUTAGETIME

    if (connectionAlive):
        txt = "Last outage was "
        if (difference.days != 0):
            txt += str(difference.days)+"d"
        if (math.floor(difference.seconds / 3600) != 0):
            txt += str(math.floor(difference.seconds / 3600))+"h"
        txt += str(math.floor((difference.seconds % 3600) / 60))+"m ago."
    else:
        txt = "Outage time: "
        if (math.floor(difference.seconds / 3600) != 0):
            txt += str(math.floor(difference.seconds / 3600))+"h"

        if (math.floor(difference.seconds / 60) != 0):
            txt += str(math.floor(difference.seconds / 60))+"m"
        txt += str(difference.seconds % 60)+"s."

    lbl3.config(text=txt)

LASTOUTAGETIME = getLastOutageTime()

def updateColor(color):
    window.configure(background=color)
    lbl.configure(background=color)
    lbl2.configure(background=color)
    lbl3.configure(background=color)
    window.update()

def updateStatus(status):
    lbl2.config(text=status)
    window.update()

def reportOutage():
    global LASTOUTAGETIME
    updateColor("#ff0000")
    updateStatus("NOT WORKING")
    setLastOutageTime(datetime.datetime.now())
    LASTOUTAGETIME = datetime.datetime.now()
    notification_api.show_toast("INTERNET CONNECTION FAILED", "Connection to server was unsuccessful.", threaded=True)
    window.attributes("-topmost", True)
    window.attributes("-topmost", False)
    window.iconbitmap(r'status_x.ico')

    outage_log.write("\n\nOUTAGE STARTED\t"+str(datetime.datetime.now()))

def reportOutageEnd():
    updateColor("#41fc03")
    updateStatus("WORKING")
    notification_api.show_toast("INTERNET CONNECTED","Successfully connected to the internet.", threaded=True)
    window.lift()
    window.attributes("-topmost", True)
    window.attributes("-topmost", False)
    window.iconbitmap(r'status_check.ico')

    outage_log.write("\nOUTAGE ENDED\t"+str(datetime.datetime.now()))


lbl = Label(window, text="THE INTERNET IS", font=("Arial",10))

lbl.config(anchor=CENTER)

lbl.pack(pady=2)


lbl2 = Label(window, text="WORKING", font=("Arial",20))

lbl2.config(anchor=CENTER)

lbl2.pack()

lbl3 = Label(window, text="Last outage was XXhXXm ago", font=("Arial", 10))

lbl3.config(anchor=CENTER)

lbl3.pack()

updateColor("#41fc03")

window.iconbitmap(r'status_check.ico')


def onTkClose():
    outage_log.close()
    window.destroy()

window.protocol("WM_DELETE_WINDOW", onTkClose)

def amIOnline(reference):
    try:
        socket.gethostbyname('google.com')
        return True
    except socket.gaierror:
        return False

connectionAlive = True
numTimesFailed = 0

def testConnection():
    global connectionAlive
    global lastOutageTime
    global numTimesFailed
    nextRunDelay = 5000


    onlineStatus = amIOnline("http://www.google.com/")

    if (onlineStatus):
        if (not connectionAlive):
            reportOutageEnd()
            connectionAlive = True
    else:
        if (connectionAlive):
            if (numTimesFailed < 4): #Tries to reconnect for 20s
                reportOutage()
                connectionAlive = False
                numTimesFailed = 0
            else:
                print("Connection failed "+str(numTimesFailed))
                numTimesFailed += 1

        nextRunDelay = 1000

    updateTimeSinceLastOutage()
    window.after(nextRunDelay, testConnection)

window.after(200, testConnection)

window.mainloop()
