from .BaseListener import Listener
from .ListenerType import ListenerType
from Resources.Message import Message
from Resources.Status import Status
import discord
from discord import User

from datetime import datetime
import asyncio
import threading
import logging
import time

class SlackListener(Listener):

    listenerType = ListenerType.DISCORD

    def __init__(self, config):
        super().__init__(config)
        self.login = config["username"]
