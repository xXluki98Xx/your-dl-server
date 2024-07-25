import os

import requests
from stem import Signal
from stem.control import Controller

from your_dl_server.dto import dto


# signal TOR for a new connection 
def renewConnection():
    session = getTorSession()
    dto().publishLoggerDebug('tor : renewConnection 1 | ' + session.get("https://check.torproject.org/api/ip").text)

    with Controller.from_port(port = 9051) as controller:
        torPassword = os.getenv('SECRET', "")
        dto().publishLoggerDebug('tor : renewConnection 2 | ' + torPassword)
        controller.authenticate(password=torPassword)
        controller.signal(Signal.NEWNYM)

    session = getTorSession()
    dto().publishLoggerDebug('tor : renewConnection 3 | ' + session.get("https://check.torproject.org/api/ip").text)


def getTorSession():
    session = requests.session()
    # Tor uses the 9050 port as the default socks port
    session.proxies = {'http':  dto().getProxy(),
                       'https': dto().getProxy()}
    return session


def checkSessionChange():
    # Following prints your normal public IP
    dto().publishLoggerDebug("real IP: " + requests.get("https://check.torproject.org/api/ip").text)

    session = getTorSession()
    dto().publishLoggerDebug("Proxy IP: " + session.get("https://check.torproject.org/api/ip").text)


def startTor():
    os.system('tor')
