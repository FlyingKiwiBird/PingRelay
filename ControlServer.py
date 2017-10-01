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
        if "web_server_port" in config:
            self.port = config["web_server_port"]
        else:
            self.port = 8080

    def run(self):
        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.loop)
        try:
            self.sever_runner = websockets.serve(self.server, 'localhost', self.port)
            self.loop.run_until_complete(self.sever_runner)
            self.running = True
        except Exception as err:
            _log.error("Error while starting server: {0}".format(err))
            return
        _log.info("Control server started")
        self.loop.run_forever()


    def stop(self):
        self.sever_runner.close()
        self.running = False

    async def server(self, websocket, path):
        while self.running and websocket.open:
            try:
                message_json = await websocket.recv()
            except Exception as err:
                _log.debug("A connection was closed: {0}".format(err))
                break
            _log.debug("Got message: {0}".format(message_json))
            try:
                message = json.loads(message_json)
            except Exception as err:
                self.send(websocket, {"error":"not in json format"})
            if "action" not in message:
                self.send(websocket, {"error":"action not specified"})
                pass
            action = message["action"]
            if (action == "get status"):
                await self.action_get_status(websocket, message)
            elif (action == "disconnect"):
                await self.action_disconnect(websocket, message)

    async def send(self, websocket, response):
        reaponse_json = json.dumps(response)
        _log.debug("Sending message: {0}".format(reaponse_json))
        try:
            await websocket.send(reaponse_json)
        except Exception as err:
            _log.debug("A connection was closed: {0}".format(err))

    async def action_get_status(self, websocket, message):
        listener_details = []
        for listener in self.app.listeners:
            listener_info = {}
            listener_info["name"] = listener.name
            listener_info["status"] = str(listener.status())
            listener_info["uptime"] = str(listener.uptime())
            listener_details.append(listener_info)

        emitter_details = []
        for emitter in self.app.emitters:
            emitter_info = {}
            emitter_info["name"] = emitter.name
            emitter_info["status"] = str(emitter.status())
            emitter_info["uptime"] = str(emitter.uptime())
            emitter_details.append(emitter_info)

        response = {"Status": "OK", "Response": "Status", "Listeners": listener_details, "Emitters": emitter_details}
        await self.send(websocket, response)

    async def action_disconnect(self, websocket, message):
        if not all(key in message for key in ["type", "name"]):
            await self.send(websocket, {"error":"action not specified"})
            return
        connection_type = message["type"]
        connection_name = message["name"]
