# Ping Relay
Gather all your modern-ish ping apps into one place?  This tool is for you!

## Supports
### Incoming
* Jabber (XMPP)
* Slack
* Discord

### Outgoing
* Discord

## Install
1. Install python 3.4+
2. clone this repo
3. Run `pip install -r requirements.txt`
### Recommended but optional: use Supervisor
4. [Install supervisor](http://supervisord.org)
5. Open PingRelay.supervisor.conf and replace all instances of `/replace/me/` with the directory you downloaded PingRelay to
6. Put the conf file in your supervisor directory `/etc/supervisor/conf.d/`

## Config
A sample config is included at `Config.example.toml` the config file uses the [TOML](https://github.com/toml-lang/toml) syntax.  It is split into 4 sections

This file must be called `Config.toml`

### General

**log_level**

Sets the logging level of the main application, can be DEBUG, INFO, WARNING, or ERROR
Defaults to INFO

**module_log_level**

Sets the logging level of 3rd party modules, can be: DEBUG, INFO, WARNING, or ERROR
Defaults to WARNING

**only_relay_alerts**

Only send messages that match alerts (more on those later)
Defaults to False

### Alerts
Alerts are a way to highlight important messages
As show in the example these are under a heading of `[[alerts]]`

**name**

The name of the alert
Required

**filter**

A regular expression which is run against the message body.  If there is a match it sends the alert.
Required

### Listeners
Listeners, well listen.  These monitor services for new messages and pass them along.
As show in the example these are under a heading of `[[listeners]]`

**type**

The type of the listener can be: Jabber, Slack, or Discord
Required

**name**

The name of the listener - not used much except for in the logs to identify issues
Required

**channel_list**

A list of channel names to monitor (Note: for discord use channel ID instead)

**pm_list**

A list of users to listen to private/direct messages from (Note: for discord use user ID instead)

#### Jabber Specific

**jid**

Jabber full username (this will have @ then a url at the end, like an email)
Required

**password**

Jabber password
Required

**host**

The URL to the "conference" server
Required

**port**

The port Jabber is running on, probably 5222
Required

#### Slack Specific

**token**

A legacy token for the user, should start with "xoxp"
Required

#### Discord specific
Discord uses IDs rather than names for channel_list and pm_list, change your client to "Dev Mode" and you can right click to copy these IDs

**email**

User's email
Required

**password**

User's password
Required

### Emitters
Emitters send the messages acquired by the listeners to the correct place
As show in the example these are under a heading of `[[emitters]]`

**type**

The type of the emitter can be: Discord (more soon)
Required

**name**

The name of the emitter - not used much except for in the logs to identify issues
Required

**default_channel**

The default channel (name) to send the messages to
Note: Discord uses channel ID instead
Required

**alert_channel**

If specified all messages with alerts will be directed to the channel with this name instead
Note: Discord uses channel ID instead

#### Formatting

**format**

The format a message is displayed in
The following placeholders can be used:

* `%{server}` - The server the message came from
* `%{channel}` - The channel the message came from
* `%{from}` - The user the message came from
* `%{time}` - The time the message arrived
* `%{message}` - The body of the message

**time_format**

The format which the `%{time}` placeholder is displayed as
See [strftime.org](http://strftime.org/) for the format
Defaults to `%Y-%m-%d %I:%M:%S %p` (e.g. `2017-09-26 10:11:12 PM`)

#### Channel directors
This is a way to direct messages that come from a server on the listener side to a channel on the emitter side
As show in the example these are under a heading of `[[emitters.channels]]`

**from_server_list**

A list of server names that the message is coming from
Note: The server name is determined depending on the listener type:
* Jabber = host
* Slack & Discord = The server name which can be found by hovering over the server icon in the apps
Required

**to_channel_list**

A list of channel names to broadcast the message to if it matches the from_server_list
Note: Discord uses channel ID instead
Required

#### Discord Specific

**token**

A token for the discord bot being used to send the messages

## Running
If not running via supervisor method simply run with:
`python PingRelay.py`

# Future / To Do

* Web interface for managing listeners/emitters
* More Emitters
