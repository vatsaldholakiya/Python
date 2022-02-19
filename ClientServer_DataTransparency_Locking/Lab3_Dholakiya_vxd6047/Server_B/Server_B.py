# Vatsal Dholakiya
# 1001966047
import os
import os.path
import time
import socket
import json
import subprocess
import diff_match_patch as dmp_module

dmp = dmp_module.diff_match_patch()

absPathToDirectoryA = "\\".join(os.getcwd().split('\\')[:-1]+["Server_A", "parentDirectoryServer_A"])
absPathToDirectoryB = "\\".join(os.getcwd().split('\\')[:-1]+["Server_B", "parentDirectoryServer_B"])

port = 8000

sleepSeconds = 2

def filesInServerA():
    return os.listdir(absPathToDirectoryA)

def filesInServerB():
    return os.listdir(absPathToDirectoryB)

getAbsoloutePathB = lambda file: os.path.join(absPathToDirectoryB, file)
doesPathExists = lambda path: os.path.exists(path)

# function to read file
def readFile(fileName):
    f=open(fileName,'r')
    data = f.read()
    f.close()
    return data

# function to keep track of deleted/added/modified files.
def createdirectoryChange_B( initialFileData, initialFileModifiedTimeStore):
    currentList = filesInServerB()
    initialList = list(initialFileModifiedTimeStore.keys())
    
    modifiedFiles = []
    for file in [item for item in currentList if item in initialList]:
        # reference : https://www.geeksforgeeks.org/python-intersection-two-lists/
        if os.path.getmtime(getAbsoloutePathB(file)) > initialFileModifiedTimeStore[file]:
            modifiedFiles.append(file)

    modifiedFilesData = {}
    for file in modifiedFiles:
        currentData = readFile(getAbsoloutePathB(file))
        modifiedFilesData[file] = dmp.patch_toText(dmp.patch_make(initialFileData[file], currentData))

    return {
        "modifiedFilesData": modifiedFilesData,
        "addedFiles": [item for item in currentList if item not in initialList],
        "deletedFiles": [item for item in initialList if item not in currentList],
    }

def sendDirectoryChange(directoryChange_B):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as soc:
        soc.connect(('127.0.0.1', port))
        soc.send(json.dumps(directoryChange_B).encode())
        data = soc.recv(1024).decode()
    soc.close()

def getDirectoryChange_A():
    soc = socket.socket()
    soc.bind(('127.0.0.1', port))
    soc.listen(5)
    conn, address = soc.accept()
    data = json.loads(conn.recv(1024).decode())
    
    conn.close()
    soc.close()

    return data

# sync servers
def syncWithServerA(directoryChange_A, directoryChange_B):
    for fileName in directoryChange_A["deletedFiles"]:
        filePath = getAbsoloutePathB(fileName)
        print("File to be deleted : ", fileName, "\nIs filepath accurate?",doesPathExists(filePath), '\n\n\n')
        if doesPathExists(filePath):
            os.remove(filePath)

    print("directoryChange_B : ",directoryChange_B)
    
    addedOrModifiedList = directoryChange_B["addedFiles"] + list(directoryChange_B["modifiedFilesData"].keys())
    
    if len(addedOrModifiedList) > 0:
        for fileName in addedOrModifiedList:
            sourceDirectory_B = getAbsoloutePathB(fileName)
            try:
                subprocess.run(['scp', sourceDirectory_B, absPathToDirectoryA], shell=True, check=True)       
            except Exception as e:
                print(e)
    
while (1):    
    # setting modified time for files
    initialFileModifiedTimeStore = {}
    for file in filesInServerB():
        initialFileModifiedTimeStore[file] = (os.path.getmtime(getAbsoloutePathB(file)))

    initialFileData = {}
    for file in filesInServerB():
        fileData = readFile(getAbsoloutePathB(file))
        initialFileData[file] = fileData

    time.sleep(sleepSeconds)

    print("Time : ",time.strftime("%H:%M:%S", time.localtime()))

    directoryChange_B = createdirectoryChange_B(initialFileData, initialFileModifiedTimeStore)
    print("\nFile changes at Server B : \n",directoryChange_B,)
    
    sendDirectoryChange(directoryChange_B)

    directoryChange_A = getDirectoryChange_A()
    print("\nFile changes at Server A : \n",directoryChange_A,"\n\n\n")
    
    syncWithServerA(directoryChange_A, directoryChange_B)