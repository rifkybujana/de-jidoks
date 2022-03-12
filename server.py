import threading
import socket
import argparse
import os
import json


class Server (threading.Thread):
    def __init__(self, host, port):
        super().__init__()
        self.connections = []
        self.host = host
        self.port = port

    def run(self):
        sock = socket.socket(
            socket.AF_INET, 
            socket.SOCK_STREAM
        )
        sock.setsockopt(
            socket.SOL_SOCKET, 
            socket.SO_REUSEADDR,
            1
        )
        sock.bind((self.host, self.port))
        sock.listen(1)

        print("Listening at", sock.getsockname())

        while True:
            # Accept new connection
            sc, sockname = sock.accept()
            print(f"{sc.getpeername()} connecting to {sc.getsockname()}")

            # Create new thread
            server_socket = ServerSocket(sc, sockname, self)

            # start new thread
            server_socket.start()

            self.connections.append(server_socket)
            print(f"{sc.getpeername()} connected!")

    def broadcast(self, message, source):
        for connection in self.connections:
            # send to all connected client accept the source client
            if connection.sockname != source:
                connection.send(message)

    def sendTo(self, message, destination):
        for connection in self.connections:
            # send to specific client
            if connection.sockname == destination:
                connection.send(message)

    def remove_connection(self, connection):
        self.connections.remove(connection)


class ServerSocket(threading.Thread):
    def __init__(self, sc, sockname, server):
        super().__init__()
        self.sc = sc
        self.sockname = sockname
        self.server = server

    def run(self):

        while True:
            with open('questions.json') as f:
                data = json.load(f)

            try:
                message = self.sc.recv(1024).decode('ascii')
            except:
                message = None

            if message:
                if message == '[request]':
                    self.server.sendTo("[response];" + json.dumps(data), self.sockname)
                elif message.split(';')[0] == "[q]":
                    question = message.split(';')
                    if int(question[1]) > len(data) - 1:
                        data.append({
                            "question" : question[2],
                            "answer" : ""
                        })
                    else:
                        data[int(question[1])]['question'] = question[2]

                    with open('questions.json', 'w') as f:
                        f.write(json.dumps(data))
                        f.close()
                        
                    self.server.broadcast(message, self.sockname)

                elif message.split(';')[0] == "[a]":
                    answer = message.split(';')
                    if int(answer[1]) > len(data) - 1:
                        data.append({
                            "question" : "",
                            "answer" : answer[2]
                        })
                    else:
                        data[int(answer[1])]['answer'] = answer[2]

                    with open('questions.json', 'w') as f:
                        f.write(json.dumps(data))
                        f.close()
                        
                    self.server.broadcast(message, self.sockname)
                else:
                    print(f"""{self.sockname} says {message}""")
                    self.server.broadcast(message, self.sockname)

            else:
                print(f"""{self.sockname} has closed the connection""")
                self.sc.close()
                self.server.remove_connection(self)
                return

    def send(self, message):
        self.sc.sendall(message.encode('ascii'))


def exit(server):
    while True:
        ipt = input("")
        if ipt == "q":
            print("Closing all connections...")
            for connection in server.connections:
                connection.sc.close()

            print("Shutting down the server...")
            os._exit(0)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Chatroom Server")
    parser.add_argument('host', help='Interface the server lintens at')
    parser.add_argument('-p', metavar='PORT', type=int, default=1060, help='TCP port(default 1060)')

    args = parser.parse_args()

    # Create and start server thread
    server = Server(args.host, args.p)
    server.start()

    exit = threading.Thread(target=exit, args=(server,))
    exit.start()