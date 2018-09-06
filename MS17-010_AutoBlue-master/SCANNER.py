

import socket
import time



def checkHost(host, port, timeout):

    sock=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    sock.settimeout(timeout)
    try:
        sock.connect((host,port))
        sock.shutdown(1)
        return 0
    except:
        return 1


liveh=[]

for x in range(1,255):
    if checkHost("192.168.1."+str(x),445,0.01)==0:
        liveh.append("192.168.1."+str(x))








