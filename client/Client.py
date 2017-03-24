# -*- coding: utf-8 -*-
import socket
import json
from MessageReceiver import MessageReceiver
from MessageParser import MessageParser


class Client:
    """
    This is the chat client class
    """
    def __init__(self, host, server_port):
        """
        This method is run when creating a new Client object
        """

        # Set up the socket connection to the server
        self.connection = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_port = server_port
        self.host = host
        self.run()

    def run(self):
        # Initiate the connection to the server
        self.connection.connect((self.host, self.server_port))

        MessageReceiver(self, self.connection)

        login_username = input("Login username: ")
        self.login(login_username)

        while True:
            message = input("> ")
            msg = message.split()
            self.create_request(msg[0], ' '.join(msg[1:]))

    def disconnect(self):
        self.connection.close()
        exit(0)

    def receive_message(self, message):
        message = message.decode()
        # print("<-- " + message)
        parser = MessageParser()
        result = parser.parse(message)
        if result is False:
            self.disconnect()

    def send_payload(self, data):
        data = json.dumps(data)

        self.connection.send(data.encode())
        # print("--> " + data)

        # More methods may be needed!

    def help(self):
        self.create_request('help')

    def login(self, username):
        self.create_request('login', username)
        self.username = username

    def logout(self):
        self.create_request('logout', self.username)

    def send_message(self, message):
        self.create_request('msg', message)

    def create_request(self, request, content=None):
        if not content:
            content = ''
        payload = {
            'request': request,
            'content': content,
        }
        self.send_payload(payload)


if __name__ == '__main__':
    """
    This is the main method and is executed when you type "python Client.py"
    in your terminal.

    No alterations are necessary
    """
    client = Client('localhost', 9998)
