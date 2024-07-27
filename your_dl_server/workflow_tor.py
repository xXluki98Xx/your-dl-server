import os

import requests
from stem import Signal
from stem.control import Controller

from your_dl_server.dto import dto
import your_dl_server.workflow_proxy as workflow_proxy


checkUrl = "https://check.torproject.org/api/ip"


# signal TOR for a new connection 
def renewConnection():
    session = getTorSession()
    dto().publishLoggerDebug('tor : renewConnection 1 | ' + session.get(checkUrl).text)

    with Controller.from_port(port = 9051) as controller:
        torPassword = os.getenv('SECRET', "")
        dto().publishLoggerDebug('tor : renewConnection 2 | ' + torPassword)
        controller.authenticate(password=torPassword)
        controller.signal(Signal.NEWNYM)

    session = getTorSession()
    dto().publishLoggerDebug('tor : renewConnection 3 | ' + session.get(checkUrl).text)


def getTorSession():
    session = requests.session()
    # Tor uses the 9050 port as the default socks port
    session.proxies = {'http':  dto().getProxy(),
                       'https': dto().getProxy()}
    return session


def checkSessionChange():
    # Following prints your normal public IP
    dto().publishLoggerDebug("real IP: " + requests.get(checkUrl).text)

    session = getTorSession()
    dto().publishLoggerDebug("Proxy IP: " + session.get(checkUrl).text)


def startTor():
    # if dto().getProxyRaw() == "":
    #     workflow_proxy.start_background_task()
    
    os.system('tor')
