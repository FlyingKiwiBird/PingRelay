from Listeners.jabberListener import JabberListener
from pprint import pprint

def main():
    jab = JabberListener("made you", "look", "conference.goonfleet.com", "5222")
    jab.onMessage(message)
    jab.connect();

def message(msg):
    pprint(msg)


if __name__== "__main__":
    main()
