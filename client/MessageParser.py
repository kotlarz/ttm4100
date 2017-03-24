import json


class MessageParser:
    def __init__(self):
        self.possible_responses = {
            'error': self.parse_error,
            'info': self.parse_info,
            'message': self.parse_message,
            'history': self.parse_history,
            'logout': self.parse_logout
        }

    def parse(self, payload):
        payload = json.loads(payload)
        # decodes the JSON object to a dictionary
        if payload['response'] in self.possible_responses:
            return self.possible_responses[payload['response']](payload)
        else:
            print("The server did not respond correctly, please try again.")
            # Response not valid

    def parse_logout(self, payload):
        print(payload['timestamp'] + ' Logged out')

    def parse_error(self, payload):
        print(payload['timestamp'] + ' Error: ' + payload['content'])
        return None

    def parse_info(self, payload):
        print(payload['timestamp'] + ' ' + payload['sender'] + ':' + "\t" + payload['content'])
        return None

    def parse_message(self, payload):
        print(payload['timestamp'] + ' ' + payload['sender'] + ':' + "\t" + payload['content'])
        return None

    def parse_history(self, payload):
        for payload_item_json in payload['content']:
            payload_item = json.loads(payload_item_json)
            if payload_item['response'] in self.possible_responses:
                self.possible_responses[payload_item['response']](payload_item)
        return None
