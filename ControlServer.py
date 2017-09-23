import sys

import websockets
import asyncio
import threading
import json

import logging
_log = logging.getLogger("PingRelay")

class ControlServer(threading.Thread):
    def __init__(self, application, config):
        threading.Thread.__init__(self)
        self.running = False
        self.app = application


    def run(self):
        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.loop)
        try:
            self.sever_runner = websockets.serve(self.server, 'localhost', 8765)
            self.loop.run_until_complete(self.sever_runner)
            self.running = True
        except Exception as err:
            _log.error("Error while starting server: {0}".format(err))
            return
        _log.info("Control server started")
        self.loop.run_forever()


    def stop(self):
        self.running = False

    async def server(self, websocket, path):
        while self.running:
            try:
                message_json = await websocket.recv()
            except Exception as err:
                _log.debug("A connection was closed: {0}".format(err))
            _log.debug("Got message: {0}".format(message_json))
            try:
                message = json.loads(message_json)
            except Exception as err:
                self.send(websocket, {"error":"not in json format"})
            if "action" not in message:
                self.send(websocket, {"error":"action not specified"})
                pass
            action = message["action"]
            if (action == "get listeners"):
                await self.action_get_listeners(websocket, message)
            elif (action == "disconnect"):
                await self.action_disconnect(websocket, message)

    async def send(self, websocket, response):
        reaponse_json = json.dumps(response)
        _log.debug("Sending message: {0}".format(reaponse_json))
        try:
            await websocket.send(reaponse_json)
        except Exception as err:
            _log.debug("A connection was closed: {0}".format(err))

    async def action_get_listeners(self, websocket, message):
        listener_names = [l.name for l in self.app.listeners]
        response = {"Status": "OK", "Listeners": listener_names}
        await self.send(websocket, response)

    async def action_disconnect(self, websocket, message):
        if not all(key in message for key in ["type", "name"]):
            await self.send(websocket, {"error":"action not specified"})
            return
        connection_type = message["type"]
        connection_name = message["name"]