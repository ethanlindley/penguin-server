import os
import binascii
from base.ServerBase import ServerBase


class LoginServer(ServerBase):

    """ main login module for login server base """

    def __init__(self):
        ServerBase.__init__(self)

        self.key = ""
        self.s = None

        self.startServer()

    def startServer(self):
        host = "localhost"
        port = 6112
        buffer_size = 4096
        self.startLoginServer(host, port, buffer_size)

    def handlePacket(self, packet):
        if packet == "<policy-file-request/>\0":
            self.sendPacket("<cross-domain-policy><allow-access-from domain='*' "
                            "to-ports='*' /></cross-domain-policy>\0")
        elif "<msg t='sys'><body action='verChk'" in packet:
            version = self.getXMLString(packet, "<ver v='", "'", 8)
            self.checkVersion(version)
        elif packet == "<msg t='sys'><body action='rndK' r='-1'></body></msg>\0":
            self.key = self.generateKey()
            self.sendPacket("<msg t='sys'><body action='rndK' r='-1'><k>" + self.key + "</k></body></msg>\0")
        elif "<msg t='sys'><body action='login' r='0'>" in packet:
            username = self.getXMLString(packet, "<nick><![CDATA[", "]]", 1)
            password = self.getXMLString(packet, "<pword><![CDATA[", "]]", 2)
            print "got new user: %s" % username
            # self.sendPacket("%xt%gs%-1%127.0.0.1:CPPL:3|127.0.0.1:6114:Moderator:2% 3;\0")
            self.sendPacket("%xt%gs%-1%127.0.0.1:6113:CPPL:3% 3;\0")
            self.sendPacket("%xt%l%-1%" + username + "%" + self.key + "%0%\0")
            # self.sendPacket("%xt%e%-1%603%\0")
        else:
            print "rogue packet: %s" % packet

    def checkVersion(self, ver):
        # TODO: don't hard set the version
        if ver == "153":
            self.sendPacket("<msg t='sys'><body action='apiOK' r='0'></body></msg>\0")
        else:
            self.sendPacket("<msg t='sys'><body action='apiKO' r='0'></body></msg>\0")

    def generateKey(self):
        key = binascii.b2a_hex(os.urandom(5))
        return key

    def getXMLString(self, _input, left, right, occurrence):
        stringL = _input.index(left) + len(left)
        stringR = self.getNthString(_input, right, occurrence) + stringL
        return _input[stringL] + _input[stringR - stringL]

    def getNthString(self, string, substring, index):
        return len(string.split(substring, index).join(substring))

    def sendPacket(self, packet):
        print "sending packet: %s" % packet  # debug
        self.s.send(packet)


gang = LoginServer()
