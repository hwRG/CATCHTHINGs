# -*- coding: utf-8 -*-
from tkinter import *
from tkinter import messagebox
from PIL import Image, ImageTk
import urllib.request
import socket
import threading
import sys

HOST = '127.0.0.1'
PORT = 8080
NAME = ""
app2 = ''
first_check = 1

class myApp:
    global NAME

    def __init__(self, Master):
        self.master = Master
        Master.title("Chat")
        Master.geometry("400x620+820+100")
        self.new_window()

        self.masterFrame = Frame(Master)
        self.masterFrame.pack(fill=X)
        self.frame1 = Frame(self.masterFrame)
        self.frame1.pack(fill=X)
        self.messageLog = Text(self.frame1)
        self.scrollbar = Scrollbar(self.frame1, command=self.messageLog.yview)
        self.messageLog.configure(width=54, height=40, state="disabled", yscrollcommand=self.scrollbar.set)
        self.messageLog.grid()
        self.messageLog.pack(side=LEFT, fill="both", expand=True)
        self.scrollbar.pack(side=RIGHT, fill=Y, expand=False)

        self.frame2 = Frame(self.masterFrame)
        self.frame2.pack(fill=X)
        self.label = Label(self.frame2, text="First input is Your nickname")
        self.label.configure(text="Your Nickname is " + "'" + NAME + "'", width=48)  # nickanme
        self.label.pack(fill=X, side=LEFT)

        self.quitButton = Button(self.frame2, text="quit", width=6, height=1, command=self.quitroot)
        self.quitButton.pack()

        self.frame3 = Frame(self.masterFrame)
        self.frame3.pack(fill=X)
        self.frame3_1 = Frame(self.frame3, padx=2, pady=1)
        self.frame3_1.pack(fill=X)

        self.input = Text(self.frame3_1, width=48, height=4)
        self.input.pack(side=LEFT)

        self.sendButton = Button(self.frame3_1, text="Send", width=6, height=3, command=self.sendMessage)
        self.sendButton.pack()
        self.sendButton.bind("<Return>", self.buttonClicked)
        self.input.bind("<KeyRelease-Return>", self.buttonClicked)

    def logRefresh(self, data):
        self.messageLog.configure(state="normal")
        self.messageLog.insert(END, "\n" + data)
        self.messageLog.see(END)
        self.messageLog.configure(state="disabled")

    def buttonClicked(self, event):
        self.sendMessage()

    def sendMessage(self):
        message = self.input.get(1.0, END)
        sock.send(message.encode().strip())
        # self.logRefresh(message)
        self.input.delete(1.0, END)

    def quitroot(self):
        if messagebox.askokcancel("Qut", "Do you want to quit?"):
            self.master.quit()
            self.master.destroy()
            sys.exit()

    def new_window(self):
        global app2
        self.newWindow = Toplevel(self.master)
        app2 = myApp2(self.newWindow)


class myApp2(Frame):
    def __init__(self, master2):
        self.master2 = master2
        Frame.__init__(self, master2)
        master2.title('Image')
        master2.geometry("700x400+100+100")

    def imshow(self):
        self.grid(row=0)
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)
        self.original = Image.open('Chat_image.jpg')
        resized = self.original.resize((700, 400), Image.ANTIALIAS)
        self.image = ImageTk.PhotoImage(resized)  # Keep a reference, prevent GC
        self.display = Label(self, image=self.image)
        self.display.grid(row=0)


class subApp:
    def __init__(self, Master):
        self.master = Master
        Master.title("Connect")
        Master.geometry("220x87")

        self.mainFrame = Frame(self.master)
        self.mainFrame.pack(fill=X)

        self.frame1 = Frame(self.mainFrame)
        self.frame1.pack(fill=X)
        self.ipLabel = Label(self.frame1)
        self.ipLabel.configure(text="Server IP", width=10)
        self.ipLabel.pack(side=LEFT)
        self.entry1 = Entry(self.frame1)
        self.entry1.pack(side=LEFT)

        self.frame2 = Frame(self.mainFrame)
        self.frame2.pack(fill=X)
        self.portLabel = Label(self.frame2)
        self.portLabel.configure(text="Port", width=10)
        self.portLabel.pack(side=LEFT)
        self.entry2 = Entry(self.frame2)
        self.entry2.pack(side=LEFT)

        self.frame3 = Frame(self.mainFrame)
        self.frame3.pack(fill=X)
        self.nameLabel = Label(self.frame3)
        self.nameLabel.configure(text="Nickname", width=10)
        self.nameLabel.pack(side=LEFT)
        self.entry3 = Entry(self.frame3)
        self.entry3.pack(side=LEFT)

        self.frame4 = Frame(self.mainFrame)
        self.frame4.pack(fill=X)
        self.button = Button(self.frame4)
        self.button.configure(text="OK", command=self.submit)
        self.button.pack(fill=X)

    def submit(self):
        global HOST, PORT, NAME
        HOST = self.entry1.get()
        PORT = int(self.entry2.get())
        NAME = self.entry3.get()
        self.master.quit()
        self.master.destroy()

    def quitroot(self):
        if messagebox.askokcancel("Quit", "Do you want to quit?"):
            self.master.quit()
            self.master.destroy()
            sys.exit()


def data_recv(sock):
    global first_check
    while True:
        try:
            get_data = sock.recv(1024)
            if not get_data:
                break
            g_data = get_data.decode('utf-8')
            if first_check:
                app2.imshow()
                first_check = 0
            if g_data.find('transmit_picture') != -1:
                urllib.request.urlretrieve('http://222.110.147.53/gyeongje/0.jpg', 'Chat_image.jpg')
                app2.imshow()
            print(g_data)
            app.logRefresh(g_data)
        except:
            pass


urllib.request.urlretrieve('http://222.110.147.53/gyeongje/waitwait.jpg', 'Chat_image.jpg')
root2 = Tk()
app_2 = subApp(root2)
root2.protocol("WM_DELETE_WINDOW", app_2.quitroot)
root2.mainloop()

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.connect((HOST, PORT))
sock.send(NAME.encode())

root = Tk()
app = myApp(root)

t3 = threading.Thread(target=data_recv, args=(sock,))
t3.daemon = True
t3.start()

root.protocol("WM_DELETE_WINDOW", app.quitroot)
root.mainloop()
