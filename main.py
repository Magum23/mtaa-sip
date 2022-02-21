import sys
import sipfullproxy
import logging
import time
import socket
import socketserver


HOST, PORT = '0.0.0.0', 5060
ipaddress = ""


def start():
    logging.basicConfig(format='%(asctime)s:%(levelname)s:%(message)s', filename='proxy.log', level=logging.INFO,
                        datefmt='%H:%M:%S')
    logging.info(time.strftime("%a, %d %b %Y %H:%M:%S ", time.localtime()))
    if len(sys.argv) > 1:
        ipaddress = sys.argv[1]
    else:
        ipaddress = input("Enter your IP address")
    hostname = socket.gethostname()
    logging.info(hostname)
    logging.info(ipaddress)
    sipfullproxy.recordroute = "Record-Route: <sip:%s:%d;lr>" % (ipaddress, PORT)
    sipfullproxy.topvia = "Via: SIP/2.0/UDP %s:%d" % (ipaddress, PORT)
    server = socketserver.UDPServer((HOST, PORT), sipfullproxy.UDPHandler)
    server.serve_forever()


start()
