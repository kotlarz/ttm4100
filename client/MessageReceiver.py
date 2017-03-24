# -*- coding: utf-8 -*-
from threading import Thread

BUFFER_SIZE = 1024


class MessageReceiver(Thread):
    """
    This is the message receiver class. The class inherits Thread, something that
    is necessary to make the MessageReceiver start a new thread, and it allows
    the chat client to both send and receive messages at the same time
    """

    def __init__(self, client, connection):
        """
        This method is executed when creating a new MessageReceiver object
        """

        # Flag to run thread as a daemon
        super(MessageReceiver, self).__init__()
        self.daemon = True
        self.client = client
        self.connection = connection
        self.start()

    def run(self):
        while True:
            data = self.connection.recv(BUFFER_SIZE)
            if not data:
                continue
            self.client.receive_message(data)
