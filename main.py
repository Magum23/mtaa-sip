#! /usr/bin/python3
import sys
import sipfullproxy
import socket
import socketserver


HOST, PORT = '0.0.0.0', 5060
ipaddress = ""


def start():
    if len(sys.argv) > 1:
        ipaddress = sys.argv[1]
    else:
        ipaddress = input("Enter your IP address")
    sipfullproxy.init_logger()
    sipfullproxy.recordroute = "Record-Route: <sip:%s:%d;lr>" % (ipaddress, PORT)
    sipfullproxy.topvia = "Via: SIP/2.0/UDP %s:%d" % (ipaddress, PORT)
    server = socketserver.UDPServer((HOST, PORT), sipfullproxy.UDPHandler)
    print("Server started")
    server.serve_forever()


if __name__ == "__main__":
    start()
