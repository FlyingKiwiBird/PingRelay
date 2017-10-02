import sys

import websockets
import asyncio
import threading
import json

from Resources.ThreadedService import ThreadStatus
from Resources.ServiceType import ServiceType

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
                self.send(websocket, {"Status": "Error", "error":"not in json format"})
            if "action" not in message:
                self.send(websocket, {"Status": "Error", "error":"action not specified"})
                pass
            action = message["action"].lower()
            if (action == "get status"):
                await self.action_get_status(websocket, message)
            elif (action == "disconnect"):
                await self.action_disconnect(websocket, message)
            elif (action == "reconnect"):
                await self.action_reconnect(websocket, message)
            else:
                self.send(websocket, {"Status": "Error", "error":"action not valid"})

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
            listener_info = self.get_details(listener)
            listener_details.append(listener_info)

        emitter_details = []
        for emitter in self.app.emitters:
            emitter_info = self.get_details(emitter)
            emitter_details.append(emitter_info)

        response = {"Status": "OK", "Response": "Status", "Listeners": listener_details.sort(key=lambda x: x['name']), "Emitters": emitter_details.sort(key=lambda x: x['name'])}
        await self.send(websocket, response)

    async def action_disconnect(self, websocket, message):
        if "id" not in message:
            await self.send(websocket, {"Status": "Error", "error":"id not specified"})
            return
        connection_id = int(message["id"])
        connections = self.app.emitters + self.app.listeners
        match = next((x for x in connections if x.id == connection_id), None)
        if match is None:
            await self.send(websocket, {"Status": "Error", "error":"connection not found"})
            return
        match.stop()
        details = self.get_details(match)
        await self.send(websocket, {"Status": "OK", "connection":details})

    async def action_reconnect(self, websocket, message):
        if "id" not in message:
            await self.send(websocket, {"Status": "Error", "error":"id not specified"})
            return
        connection_id = int(message["id"])
        connections = self.app.emitters + self.app.listeners
        match = next((x for x in connections if x.id == connection_id), None)
        if match is None:
            await self.send(websocket, {"Status": "Error", "error":"connection not found"})
            return
        if match.status() == ThreadStatus.Running:
            match.stop()
        if match.connectionType == ServiceType.LISTENER:
            self.app.reconnect_listener(match)
        elif match.connectionType == ServiceType.EMITTER:
            self.app.reconnect_emitter(match)

        details = self.get_details(match)
        await self.send(websocket, {"Status": "OK", "connection":details})


    def get_details(self, connection):
        connection_info = {}
        connection_info["id"] = connection.id
        connection_info["name"] = connection.name
        connection_info["status"] = str(connection.status().value)
        connection_info["uptime"] = str(connection.uptime())
        return connection_info
