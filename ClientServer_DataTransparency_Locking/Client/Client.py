# Vatsal Dholakiya
# 1001966047
import json
import socket
import sys

port = 8000

arguments = sys.argv

argumentsLength = (sys.argv).__len__()

if (argumentsLength != 1 and argumentsLength != 3) or (argumentsLength==3 and arguments[1]!='-unlock' and arguments[1]!='-lock'):
    print(argumentsLength,arguments[1],type(arguments[2]))
    print("You've passed wrong set of arguments... \nexiting...")
    exit()

    
with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.connect(('127.0.0.1', port))
    if argumentsLength==3 :
        s.send(json.dumps(arguments[-2:]).encode())
    else: 
        s.send('client_invoke'.encode())
    data = s.recv(99999).decode()
s.close()

print("\n*********************************************************************************************************************=\n")

try:
    loadedData = json.loads(data)
    print("{:<10} {:<15} {:<15} {:<30} {:<30} {:<20}\n".format('Index','File','Size','Modified Time','Access Time','Lock Status'))
    iterator = 0
    for file in loadedData:
        file["assignedPermissions"] = '  <locked>' if  file["assignedPermissions"] == '0o100444' else '------------'
        print("{:<10} {:<15} {:<15} {:<30} {:<30} {:<20}".format('['+str(iterator)+']', file["File"],file["Size"],file["modifiedTime"],file["accessTime"],(file["assignedPermissions"])))
        iterator = iterator + 1 
    print("\n\n--------------------------")
    print("\n#File(s) : ",len(loadedData))

except:
    print(data)

print("\n*********************************************************************************************************************=\n")