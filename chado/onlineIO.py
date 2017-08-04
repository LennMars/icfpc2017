import sys
import socket
import requests
import json
import time

class OnlineIO():
    def __init__(self):
        pass



if __name__ == '__main__':
    hostname = "punter.inf.ed.ac.uk"
    hostaddress = socket.gethostbyname(hostname)
    port = 9001

    shakehand = {"me":"CubeClub"}
    shakehand_json = json.dumps(shakehand)
    print(shakehand_json)
    print(len(shakehand_json))
    shakehand_json = str(len(shakehand_json))+":"+shakehand_json
    print(shakehand_json)

    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect((hostaddress,port))
    #I guess connetion is succeeded

    client.send(shakehand_json)
    response = client.recv(1024)

    print(response)
