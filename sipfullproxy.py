#    Copyright 2014 Philippe THIRION
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.

#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.

#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.

#    library source https://github.com/tirfil/PySipFullProxy

import socketserver
import re
import time
import logging

HOST, PORT = '0.0.0.0', 5060
rx_register = re.compile("^REGISTER")
rx_invite = re.compile("^INVITE")  # this
rx_ack = re.compile("^ACK")  # this
rx_prack = re.compile("^PRACK")
rx_cancel = re.compile("^CANCEL")
rx_decline = re.compile("^SIP/2.0 603 ([^ ]*)")
rx_accept = re.compile("^SIP/2.0 200 ([^ ]*)")
rx_bye = re.compile("^BYE")  # this
rx_options = re.compile("^OPTIONS")
rx_subscribe = re.compile("^SUBSCRIBE")
rx_publish = re.compile("^PUBLISH")
rx_notify = re.compile("^NOTIFY")
rx_info = re.compile("^INFO")
rx_message = re.compile("^MESSAGE")
rx_refer = re.compile("^REFER")
rx_update = re.compile("^UPDATE")
rx_from = re.compile("^From:")
rx_cfrom = re.compile("^f:")
rx_to = re.compile("^To:")
rx_cto = re.compile("^t:")
rx_tag = re.compile(";tag")
rx_contact = re.compile("^Contact:")
rx_ccontact = re.compile("^m:")
rx_uri = re.compile("sip:([^@]*)@([^;>$]*)")
rx_addr = re.compile("sip:([^ ;>$]*)")
# rx_addrport = re.compile("([^:]*):(.*)")
rx_code = re.compile("^SIP/2.0 ([^ ]*)")
# rx_cseq = re.compile("^CSeq:")
# rx_callid = re.compile("Call-ID: (.*)$")
# rx_rr = re.compile("^Record-Route:")
rx_request_uri = re.compile("^([^ ]*) sip:([^ ]*) SIP/2.0")
rx_route = re.compile("^Route:")
rx_contentlength = re.compile("^Content-Length:")
rx_ccontentlength = re.compile("^l:")
rx_via = re.compile("^Via:")
rx_cvia = re.compile("^v:")
rx_branch = re.compile(";branch=([^;]*)")
rx_rport = re.compile(";rport$|;rport;")
rx_contact_expires = re.compile("expires=([^;$]*)")
rx_expires = re.compile("^Expires: (.*)$")

# global dictionnary
global recordroute
global topvia
global registrar

recordroute = ""
topvia = ""
registrar = {}
in_call = []


def hexdump(chars, sep, width):
    while chars:
        line = chars[:width]
        chars = chars[width:]
        line = line.ljust(width, '\000')


def quotechars(chars):
    return ''.join(['.', c][c.isalnum()] for c in chars)


def init_logger():
    logging.basicConfig(format='%(asctime)s\t%(message)s', filename='zaznam.log', level=logging.INFO)
    logging.info("Server zapnuty")


class UDPHandler(socketserver.BaseRequestHandler):

    def changeRequestUri(self):
        # change request uri
        md = rx_request_uri.search(self.data[0])
        if md:
            method = md.group(1)
            uri = md.group(2)
            if uri in registrar:
                uri = "sip:%s" % registrar[uri][0]
                self.data[0] = "%s %s SIP/2.0" % (method, uri)

    def removeRouteHeader(self):
        # delete Route
        data = []
        for line in self.data:
            if not rx_route.search(line):
                data.append(line)
        return data

    def addTopVia(self):
        branch = ""
        data = []
        for line in self.data:
            if rx_via.search(line) or rx_cvia.search(line):
                md = rx_branch.search(line)
                if md:
                    branch = md.group(1)
                    via = "%s;branch=%sm" % (topvia, branch)
                    data.append(via)
                # rport processing
                if rx_rport.search(line):
                    text = "received=%s;rport=%d" % self.client_address
                    via = line.replace("rport", text)
                else:
                    text = "received=%s" % self.client_address[0]
                    via = "%s;%s" % (line, text)
                data.append(via)
            else:
                data.append(line)
        return data

    def removeTopVia(self):
        data = []
        for line in self.data:
            if rx_via.search(line) or rx_cvia.search(line):
                if not line.startswith(topvia):
                    data.append(line)
            else:
                data.append(line)
        return data

    def checkValidity(self, uri):
        addrport, socket, client_addr, validity = registrar[uri]
        now = int(time.time())
        if validity > now:
            return True
        else:
            del registrar[uri]
            return False

    def getSocketInfo(self, uri):
        addrport, socket, client_addr, validity = registrar[uri]
        return (socket, client_addr)

    def getDestination(self):
        destination = ""
        for line in self.data:
            if rx_to.search(line) or rx_cto.search(line):
                md = rx_uri.search(line)
                if md:
                    destination = "%s@%s" % (md.group(1), md.group(2))
                break
        return destination

    def getOrigin(self):
        origin = ""
        for line in self.data:
            if rx_from.search(line) or rx_cfrom.search(line):
                md = rx_uri.search(line)
                if md:
                    origin = "%s@%s" % (md.group(1), md.group(2))
                break
        return origin

    def sendResponse(self, code):
        request_uri = "SIP/2.0 " + code
        self.data[0] = request_uri
        index = 0
        data = []
        for line in self.data:
            data.append(line)
            if rx_to.search(line) or rx_cto.search(line):
                if not rx_tag.search(line):
                    data[index] = "%s%s" % (line, ";tag=123456")
            if rx_via.search(line) or rx_cvia.search(line):
                # rport processing
                if rx_rport.search(line):
                    text = "received=%s;rport=%d" % self.client_address
                    data[index] = line.replace("rport", text)
                else:
                    text = "received=%s" % self.client_address[0]
                    data[index] = "%s;%s" % (line, text)
            if rx_contentlength.search(line):
                data[index] = "Content-Length: 0"
            if rx_ccontentlength.search(line):
                data[index] = "l: 0"
            index += 1
            if line == "":
                break
        data.append("")
        text = "\r\n".join(data).encode('utf-8')
        self.socket.sendto(text, self.client_address)

    def processRegister(self):
        fromm = ""
        contact = ""
        contact_expires = ""
        header_expires = ""
        expires = 0
        validity = 0
        authorization = ""
        index = 0
        auth_index = 0
        data = []
        size = len(self.data)
        for line in self.data:
            if rx_to.search(line) or rx_cto.search(line):
                md = rx_uri.search(line)
                if md:
                    fromm = "%s@%s" % (md.group(1), md.group(2))
            if rx_contact.search(line) or rx_ccontact.search(line):
                md = rx_uri.search(line)
                if md:
                    contact = md.group(2)
                else:
                    md = rx_addr.search(line)
                    if md:
                        contact = md.group(1)
                md = rx_contact_expires.search(line)
                if md:
                    contact_expires = md.group(1)
            md = rx_expires.search(line)
            if md:
                header_expires = md.group(1)

        if len(contact_expires) > 0:
            expires = int(contact_expires)
        elif len(header_expires) > 0:
            expires = int(header_expires)

        if expires == 0:
            if fromm in registrar:
                del registrar[fromm]
                self.sendResponse("200 SUPER")
                return
        else:
            now = int(time.time())
            validity = now + expires

        registrar[fromm] = [contact, self.socket, self.client_address, validity]
        self.sendResponse("200 SUPER")

    def getCallId(self):
        if len(self.data) > 5:
            return self.data[5]
        return "unknown call id"

    def processInvite(self):
        origin = self.getOrigin()
        if len(origin) == 0 or not origin in registrar:
            self.sendResponse("400 ZLA POZIADAVKA")
            return
        destination = self.getDestination()
        if len(destination) > 0:
            logging.info("HOVOR {} >>> {} ({})".format(self.getOrigin(), destination, self.getCallId()))
            in_call.append(self.getDestination())
            in_call.append(self.getOrigin())
            if destination in registrar and self.checkValidity(destination):
                socket, claddr = self.getSocketInfo(destination)
                # self.changeRequestUri()
                self.data = self.addTopVia()
                data = self.removeRouteHeader()
                # insert Record-Route
                data.insert(1, recordroute)
                text = "\r\n".join(data).encode('utf-8')
                socket.sendto(text, claddr)
            else:
                logging.info("NEDOSTUPNY {} ( VOLAL >>> {} )".format(destination, self.getOrigin()))
                self.sendResponse("480 NEDOSTUPNY")
        else:
            self.sendResponse("500 CHYBA SERVERU")

    def processAck(self):
        destination = self.getDestination()
        if len(destination) > 0:
            # logging.info("HOVOR PRIJATY ({} >>> {})".format(destination, self.getOrigin()))
            if destination in registrar:
                socket, claddr = self.getSocketInfo(destination)
                # self.changeRequestUri()
                self.data = self.addTopVia()
                data = self.removeRouteHeader()
                # insert Record-Route
                data.insert(1, recordroute)
                text = "\r\n".join(data).encode('utf-8')
                socket.sendto(text, claddr)

    def processNonInvite(self):
        origin = self.getOrigin()
        if len(origin) == 0 or not origin in registrar:
            self.sendResponse("400 ZLA POZIADAVKA")
            return
        destination = self.getDestination()
        if len(destination) > 0:
            if destination in registrar and self.checkValidity(destination):
                socket, claddr = self.getSocketInfo(destination)
                # self.changeRequestUri()
                self.data = self.addTopVia()
                data = self.removeRouteHeader()
                # insert Record-Route
                data.insert(1, recordroute)
                text = "\r\n".join(data).encode('utf-8')
                if rx_bye.search(self.data[0]):
                    in_call.remove(self.getDestination())
                    in_call.remove(self.getOrigin())
                    logging.info("KONIEC HOVORU ( {} - {} )".format(destination, self.getOrigin()))
                if rx_cancel.search(self.data[0]):
                    in_call.remove(self.getDestination())
                    in_call.remove(self.getOrigin())
                    logging.info("HOVOR ZRUSENY ( {} - {} )".format(destination, self.getOrigin()))

                socket.sendto(text, claddr)
            else:
                self.sendResponse("406 NEPRIJATELNE")
        else:
            self.sendResponse("500 CHYBA SERVERU")

    def processCode(self):
        origin = self.getOrigin()
        if len(origin) > 0:
            if origin in registrar:
                socket, claddr = self.getSocketInfo(origin)
                self.data = self.removeRouteHeader()
                data = self.removeTopVia()
                text = "\r\n".join(data).encode('utf-8')
                socket.sendto(text, claddr)
                if rx_decline.search(self.data[0]):
                    in_call.remove(self.getDestination())
                    in_call.remove(self.getOrigin())
                    logging.info("HOVOR ODMIETNUTY ( {} - {} )".format(self.getDestination(), self.getOrigin()))
                if rx_accept.search(self.data[0]) and self.getOrigin() in in_call and self.getDestination() in in_call:
                    logging.info("HOVOR PRIJATY ({} >>> {})".format(self.getOrigin(), self.getDestination()))


    def processRequest(self):
        if len(self.data) > 0:
            request_uri = self.data[0]
            if rx_register.search(request_uri):
                self.processRegister()
            elif rx_invite.search(request_uri):
                self.processInvite()
            elif rx_ack.search(request_uri):
                self.processAck()
            elif rx_bye.search(request_uri):
                self.processNonInvite()
            elif rx_cancel.search(request_uri):
                self.processNonInvite()
            elif rx_options.search(request_uri):
                self.processNonInvite()
            elif rx_info.search(request_uri):
                self.processNonInvite()
            elif rx_message.search(request_uri):
                self.processNonInvite()
            elif rx_refer.search(request_uri):
                self.processNonInvite()
            elif rx_prack.search(request_uri):
                self.processNonInvite()
            elif rx_update.search(request_uri):
                self.processNonInvite()
            elif rx_subscribe.search(request_uri):
                self.sendResponse("200 SUPER")
            elif rx_publish.search(request_uri):
                self.sendResponse("200 SUPER")
            elif rx_notify.search(request_uri):
                self.sendResponse("200 SUPER")
            elif rx_code.search(request_uri):
                self.processCode()
            else:
                print(request_uri)
            # elif rx_decline(request_uri):
            #     self.processNonInvite()

    def handle(self):
        data = self.request[0].decode('utf-8')
        self.data = data.split("\r\n")
        self.socket = self.request[1]
        request_uri = self.data[0]
        if rx_request_uri.search(request_uri) or rx_code.search(request_uri):
            self.processRequest()
        else:
            if len(data) > 4:
                hexdump(data, ' ', 16)

