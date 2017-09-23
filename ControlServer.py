import sys

import websockets
import asyncio
import json

import logging
_log = logging.getLogger("PingRelay")

class ControlServer(object):
    def __init__(self, application, config):
        self.app = application

    def start(self):
        _log.debug("Starting control server")
        self.sever_runner = websockets.serve(self.server, 'localhost', 8765)
        asyncio.get_event_loop().run_until_complete(self.sever_runner)
        asyncio.get_event_loop().run_forever()
        _log.debug("Control server up")

    async def send(self, websocket, response):
        json = json.dumps(response)
        _log.debug("Sending message: {0}".format(json))
        await websocket.send(json)

    async def action_disconnect(self, websocket, message):
        if not all(key in message for key in ["type", "name"]):
            self.send(websocket, {"error":"action not specified"})
            return
        connection_type = message["type"]
        connection_name = message["name"]

    async def server(self, websocket, path):
        while True:
            message_json = await websocket.recv()
            try:
                message = json.loads(message_json)
            except Exception as err:
                self.send(websocket, {"error":"not in json format"})
            if "action" not in message:
                self.send(websocket, {"error":"action not specified"})
                pass
            action = message["action"]
            if (action == "disconnect"):
                self.action_disconnect(websocket, message)
