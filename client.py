import threading
import socket
import argparse
import os
import sys
import tkinter as tk


class Send(threading.Thread):
    # Listens for user input from command line

    # sock the connected sock object
    # name (str) : The username provided by the user

    def __init__(self, sock, name):
        super().__init__()
        self.sock = sock
        self.name = name

    def run(self):
        # Listen for the user input from the command line and send it to the server
        # Type "QUIT" to exit the app

        while True:
            print("""{}: """.format(self.name), end='')
            sys.stdout.flush()
            message = sys.stdin.readline()[:-1]

            # type "QUIT" to leave the app

            if message == "QUIT":
                self.sock.sendall("""Server: {} has left.""".format(self.name).encode('ascii'))
                break

            # send messageto server for broadcasting
            else:
                self.sock.sendall("""{} : {} """.format(self.name, message).encode('ascii'))

        print('\nQuitting...')
        self.sock.close()
        os._exit(0)


class Receive(threading.Thread):
    # Listens for incoming messages from the server
    
    def __init__(self, sock, name):
        super().__init__()
        self.sock = sock
        self.name = name
        self.messages = None

    def run(self):

        # Receives data from the server and displays it in the gui

        while True:
            try:
                message = self.sock.recv(1024).decode('ascii')
            except:
                message = None

            if message:
                if self.messages:
                    self.messages.insert(tk.END, message)
                    print('\r{}\n{}: '.format(message, self.name), end='')
                else:
                    print('\r{}\n{}: '.format(message, self.name), end='')
            else:
                print('\n Lost connection to the server!')
                print('\nQuitting...')
                self.sock.close()
                os._exit(0)


class Client:
    # management of client-server connection and integration of GUI
    
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.sock = socket.socket(
            socket.AF_INET, 
            socket.SOCK_STREAM
        )
        self.name = None
        self.messages = None

    def start(self):
        print('Trying to connect to {}:{}....'.format(self.host, self.port))

        self.sock.connect((self.host, self.port))

        print('Succesfully connected to {}:{}'.format(self.host, self.port))
        print('')

        self.name = input('Your Name: ')
        print('')

        print('Welcome, {}! Getting ready to send and receive messages...'.format(self.name))

        # Create send and receive threads

        send = Send(self.sock, self.name)
        receive = Receive(self.sock, self.name)

        # start send and receive thread
        send.start()
        receive.start()

        self.sock.sendall('Server: {} has join the chat'.format(self.name).encode('ascii'))
        print("""\rReady! Type 'QUIT' to cabskuy""")
        print('{}: '.format(self.name), end= '')

        return receive

    def send(self, textInput):
        # Sends textInput data from the GUI
        message = textInput.get()
        textInput.delete(0, tk.END)
        self.messages.insert(tk.END, '{}: {}'.format(self.name, message))

        # Type 'QUIT' to leave the chat
        if message == "QUIT":
            self.quit()

        # SEND message to the server for broadcasting
        else:
            self.sock.sendall('{}: {}'.format(self.name, message).encode('ascii'))

    def quit(self):
        self.sock.sendall('Server: {} has left the chat'.format(self.name).encode('ascii'))
        print('\nQuitting...')
        self.sock.close()
        os._exit(0)


def main(host, port):
    # initialize and run GUI app

    client = Client(host, port)
    receive = client.start()

    window = tk.Tk()
    window.title("Megalitikum Robotikum (versi lite)")

    fromMessage = tk.Frame(master=window)
    scrollBar = tk.Scrollbar(master=fromMessage)
    messages = tk.Listbox(master=fromMessage, yscrollcommand=scrollBar.set)
    scrollBar.pack(side=tk.RIGHT, fill=tk.Y, expand=False)
    messages.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

    client.messages = messages
    receive.messages = messages

    fromMessage.grid(row=0, column=0, columnspan=3, sticky="nsew")
    fromEntry = tk.Frame(master=window)
    textInput = tk.Entry(master=fromEntry)

    textInput.pack(fill=tk.BOTH, expand=True)
    textInput.bind("<Return>", lambda x: client.send(textInput))
    textInput.insert(0, "Write your message here.")

    btnSend = tk.Button(
        master=window,
        text="Send",
        command=lambda: client.send(textInput)
    )
    btnGdocs = tk.Button(
        master=window,
        text="GDocs",
        command=lambda: openGDocs(window, btnGdocs)
    )

    fromEntry.grid(row=1, column=0, padx=10, sticky="ew")
    btnSend.grid(row=1, column=1, pady=10, sticky="ew")
    btnGdocs.grid(row=1, column=2, pady=10, sticky="ew")

    window.rowconfigure(0, minsize=500, weight=1)
    window.rowconfigure(1, minsize=50, weight=0)
    window.columnconfigure(0, minsize=500, weight=1)
    window.columnconfigure(1, minsize=100, weight=0)
    window.columnconfigure(2, minsize=100, weight=0)

    window.mainloop()

    client.quit()


def changeButtonState(button, window=None):
    if button['state'] == "normal":
        button['state'] = "disable"
    else:
        button['state'] = "normal"
        if window:
            window.destroy()


def openGDocs(parent, button):
    window = tk.Toplevel(parent)
    window.title("The Jidoks (versi lite)")

    fromMessage = tk.Frame(master=window)
    scrollBar = tk.Scrollbar(master=fromMessage)
    questions = tk.Listbox(master=fromMessage, yscrollcommand=scrollBar.set)
    answers = tk.Listbox(master=fromMessage, yscrollcommand=scrollBar.set)
    scrollBar.pack(side=tk.RIGHT, fill=tk.Y, expand=False)
    questions.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
    answers.pack(side=tk.LEFT, fill=tk.BOTH, expand=False)
    
    fromMessage.grid(row=0, column=0, columnspan=2, sticky="nsew")
    fromEntry = tk.Frame(master=window)
    textInput = tk.Entry(master=fromEntry)

    textInput.pack(fill=tk.BOTH, expand=True)
    textInput.bind("<Return>", lambda x: print("send question"))
    textInput.insert(0, "Write your message here.")

    btnSend = tk.Button(
        master=window,
        text="Send",
        command=lambda: print("send question")
    )

    fromEntry.grid(row=1, column=0, padx=10, sticky="ew")
    btnSend.grid(row=1, column=1, pady=10, sticky="ew")
    
    window.rowconfigure(0, minsize=500, weight=1)
    window.rowconfigure(1, minsize=50, weight=0)
    window.columnconfigure(0, minsize=500, weight=1)
    window.columnconfigure(1, minsize=100, weight=0)


    changeButtonState(button)

    window.protocol('WM_DELETE_WINDOW', lambda: changeButtonState(button, window))


if __name__ == "__main__":
    host = input('Host: ')
    port = int(input('Port (default 1060): ') or "1060")

    main(host, port)