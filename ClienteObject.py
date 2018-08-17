# --*-- coding: utf-8 --*--
import socket

class client:

    def __init__(self, name, address, channel):
        self.name = name
        self.address = address
        self.channel = channel

        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.settimeout(2)

    def getName(self):
        return self.name

    def getAddress(self):
        return self.address

    def getChannel(self):
        return self.channel

    def setName(self, name):
        self.name = name

    def setAddress(self, address):
        self.address = address

    def setChannel(self, channel):
        self.channel = channel

    def getSocket(self):
        return self.socket

    def setSockete(self, socket):
        self.socket = socket
