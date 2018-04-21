from datetime import datetime
import discord

class Message:

    def __init__(self, listener, message, sender, channel, server, time = None):
        self.listener = listener
        self.message = message
        self.sender = sender
        self.channel = channel
        self.server = server
        self.time = time or datetime.utcnow()        

        self.has_alert = False
        self.alerts = []

    def __str__(self):
        time_str = self.time.strftime("%Y-%m-%d %H:%M:%S")
        return "[{0}] {1}>{2}>{3}: {4}".format(time_str, self.server, self.channel, self.sender, self.message)

    @property
    def search_text(self):
        return "CHANNEL: {0}\nSENDER: {1}\nMESSAGE: {2}".format(self.channel, self.sender, self.message)

    def add_alert(self, alert):
        self.has_alert = True
        self.alerts.append(alert)

    def get_alert_str(self):
        return ", ".join(self.alerts)

    def embed(self, time_fmt="%Y-%m-%d %H:%M:%S"):
        embed = discord.Embed(description=self.message)
        if self.has_alert:
            embed.add_field(name="Alerts", value=self.get_alert_str(), inline=False)
            embed.color=0xff0000
        embed.add_field(name="Server", value=self.server, inline=True)
        embed.add_field(name="Channel", value=self.channel, inline=True)
        embed.add_field(name="Author", value=self.sender, inline=True)
        embed.set_footer(text=self.time.strftime(time_fmt))
        return embed
