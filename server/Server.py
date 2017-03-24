# -*- coding: utf-8 -*-
import socketserver
import time
import json
import datetime
import re

"""
Variables and functions that must be used by all the ClientHandler objects
must be written here (e.g. a dictionary for connected clients)
"""

# Dictionary of connected clients [keys] = connection, [values] = name
connectedClients = {}
users = []

# List of chat history
history = []

# Regular expression allowed characters for users
viableCharacters = re.compile("^[a-zA-Z0-9]+$")


class ClientHandler(socketserver.BaseRequestHandler):
    """
    This is the ClientHandler class. Everytime a new client connects to the
    server, a new ClientHandler object will be created. This class represents
    only connected clients, and not the server itself. If you want to write
    logic for the server, you must write it outside this class
    """

    def handle(self):
        """
        This method handles the connection between a client and the server.
        """
        self.ip = self.client_address[0]
        self.port = self.client_address[1]
        self.connection = self.request
        self.client = ''
        self.login_flag = False

        # Loop that listens for messages from the client
        while True:
            received_string = self.connection.recv(4096)
            if not received_string:
                continue
            received_string = received_string.decode()
            print("<-- [", self.ip, "]:", received_string)
            received_string = json.loads(received_string)
            request = received_string['request']
            content = received_string['content']

            # Handling login request
            if request == 'login' and content is not None:
                if not viableCharacters.match(content):
                    self.respond('error', 'Invalid name!')
                elif content in users:
                    self.respond('error', 'Already logged in!')
                else:
                    self.client = content
                    if self.client not in connectedClients:
                        connectedClients[self.connection] = self.client
                        users.append(self.client)
                        self.respond('info', "Login successful!")
                        message = self.generate_message('info', content + " has logged in!")
                        self.send_to_clients_except_name(message, content)
                        history.append(message)
                        self.login_flag = True
                        if len(history) > 0:
                            self.respond('history', history)
                    else:
                        self.respond('error', 'Already logged in!')
            # Handling help request
            elif request == 'help':
                if self.login_flag:
                    self.respond('info', 'Supported requests is: logout, history, msg/message')
                else:
                    self.respond('info', 'Supported request is: login!')
            # Ensures that only logged in clients can access the server's main functionality
            elif self.login_flag:
                # Handling logout request
                if request == 'logout':
                    if self.client in users:
                        del connectedClients[self.connection]
                        users.remove(self.client)
                        message = self.generate_message('info', self.client + " has logged out!")
                        self.send_to_clients_except_name(message, self.client)
                        history.append(message)
                        self.login_flag = False
                    else:
                        self.respond('error', 'You are not logged in!')

                # Handling msg request
                elif request == 'msg' or request == "message":
                    message = self.generate_message('message', content)
                    self.send_to_clients(message)
                    history.append(message)

                # Handling history request
                elif request == 'history':
                    self.respond('history', history)

                else:
                    self.respond('error', 'Invalid command. Supported requests is: logout, history, msg/message')
            else:
                self.respond('error', 'Invalid command. Supported requests is: login!')

    def respond(self, response, content):
        response = json.dumps(
            {
                'timestamp': datetime.datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S'),
                'sender': self.client,
                'response': response,
                'content': content,
            }
        )
        if response == 'message':
            history.append(response)
        self.send_to_connection(self.connection, response)

    def send_to_clients(self, message):
        for connection in list(connectedClients):
            self.send_to_connection(connection, message)

    def send_to_clients_except_name(self, message, expect_name):
        for connection in list(connectedClients):
            if connectedClients[connection] == expect_name:
                continue
            self.send_to_connection(connection, message)

    def send_to_connection(self, connection, response):
        try:
            connection.send(response.encode())
            print("--> [", connection.getpeername(), "]:", response)
        except OSError as e:
            # Client is no longer connected or has an error, dirty workaround
            print("OS ERROR! " + e)
            del connectedClients[connection]
            users.remove(self.client)

    def generate_message(self, response, content):
        message = json.dumps(
            {
                'timestamp': datetime.datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S'),
                'sender': self.client,
                'response': response,
                'content': content,
            }
        )
        return message


class ThreadedTCPServer(socketserver.ThreadingMixIn, socketserver.TCPServer):
    """
    This class is present so that each client connected will be ran as a own
    thread. In that way, all clients will be served by the server.

    No alterations are necessary
    """
    allow_reuse_address = True

if __name__ == "__main__":
    """
    This is the main method and is executed when you type "python Server.py"
    in your terminal.

    No alterations are necessary
    """
    HOST, PORT = 'localhost', 9998
    print('Server running...')

    # Set up and initiate the TCP server
    server = ThreadedTCPServer((HOST, PORT), ClientHandler)
    server.serve_forever()
