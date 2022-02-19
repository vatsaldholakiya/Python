# Vatsal Dholakiya
# 1001966047
import socket
import time
import json
import os
import subprocess
from datetime import datetime
import sys
import diff_match_patch as dmp_module

port = 8000

dmp = dmp_module.diff_match_patch()
Queue = {}

absPathToDirectoryA = "\\".join(os.getcwd().split('\\')[:-1] +
                                ["Server_A", "parentDirectoryServer_A"])
absPathToDirectoryB = "\\".join(os.getcwd().split('\\')[:-1] +
                                ["Server_B", "parentDirectoryServer_B"])


def filesInServerA():
    return os.listdir(absPathToDirectoryA)


def filesInServerB():
    return os.listdir(absPathToDirectoryB)


# lambda function to get absoloute path for a particular file in server A
def getAbsoloutePathA(file):
    return os.path.join(absPathToDirectoryA, file)


# lambda function to get absoloute path for a particular file in server B
def getAbsoloutePathB(file):
    return os.path.join(absPathToDirectoryB, file)


# lambda function to check if the path exists
def doesPathExists(path):
    return os.path.exists(path)


# lambda function to get modified time
def modifiedTime(path):
    return os.path.getmtime(path)


def readFile(fileName):
    f = open(fileName, 'r')
    data = f.read()
    f.close()
    return data


# https://stackoverflow.com/questions/5194057/better-way-to-convert-file-sizes-in-python
def convert_bytes(bytes_number):
    tags = ["B", "KB", "MB", "GB", "TB"]
    i = 0
    double_bytes = bytes_number
    while (i < len(tags) and bytes_number >= 1024):
        double_bytes = bytes_number / 1024.0
        i = i + 1
        bytes_number = bytes_number / 1024
    return str(round(double_bytes, 2)) + " " + tags[i]


def syncServers():
    print("\n\nSyncing when starting server A...\n")

    # change modes in order to scp
    print('unlocking/changing permissions(777) of all files at A\n')
    for file in filesInServerA():
        os.chmod(getAbsoloutePathA(file), 0o777)

    filesOnlyInA = [
        item for item in filesInServerA() if item not in filesInServerB()
    ]
    print("fileList of A not B : \n\t\t", filesOnlyInA, '\n')
    # https://www.geeksforgeeks.org/python-intersection-two-lists/

    filesOnlyInB = [
        item for item in filesInServerB() if item not in filesInServerA()
    ]
    print("fileList of B not A : \n\t\t", filesOnlyInB, '\n')
    # https://www.geeksforgeeks.org/python-intersection-two-lists/

    fileInAandB = [
        item for item in filesInServerA() if item in filesInServerB()
    ]
    print("fileList of A and B : \n\t\t", fileInAandB, '\n')
    # https://www.geeksforgeeks.org/python-intersection-two-lists/

    # send files only in A to B
    for file in filesOnlyInA:
        filePathA = getAbsoloutePathA(file)
        subprocess.run(['scp', filePathA, absPathToDirectoryB],
                       shell=True,
                       check=True)

    # send files only in B to A
    for file in filesOnlyInB:
        filePathB = getAbsoloutePathB(file)
        subprocess.run(['scp', filePathB, absPathToDirectoryA],
                       shell=True,
                       check=True)

    for file in fileInAandB:
        fileModifiedTime_A = (modifiedTime(getAbsoloutePathA(file)))
        fileModifiedTime_B = (modifiedTime(getAbsoloutePathB(file)))

        if fileModifiedTime_A > fileModifiedTime_B:
            print("\nFile : ", file, "\nmodifiedTime at A : ",
                  time.ctime(fileModifiedTime_A), "\nmodifiedTime at B : ",
                  time.ctime(fileModifiedTime_B))
            subprocess.run(
                ['scp', getAbsoloutePathA(file), absPathToDirectoryB],
                shell=True,
                check=True)
        elif fileModifiedTime_A < fileModifiedTime_B:
            print("\nFile : ", file, "\nmodifiedTime at A : ",
                  time.ctime(fileModifiedTime_A), "\nmodifiedTime at B : ",
                  time.ctime(fileModifiedTime_B))
            subprocess.run(
                ['scp', getAbsoloutePathB(file), absPathToDirectoryA],
                shell=True,
                check=True)
        else:
            None

    print("\n")


def getDirectoryChange_A(initialListModifiedTime):
    # creting the dictionary that contains info about deletion/addition/modification of files in server B.

    initialList = list(initialListModifiedTime.keys())
    # list before connection recieved
    currentList = filesInServerA()
    # list after connection recieved

    preExistingFiles = [item for item in currentList if item in initialList]
    # https://www.geeksforgeeks.org/python-intersection-two-lists/

    modifiedFiles = []
    # if the last modified time of new file is more than that of old file with same name. Add it to the list.
    for file in preExistingFiles:
        if modifiedTime(
                getAbsoloutePathA(file)) > initialListModifiedTime[file]:
            modifiedFiles.append(file)

    return {
        "modifiedFiles": modifiedFiles,
        # list ofthe files that are in new list and not in old list.
        "addedFiles":
        [item for item in currentList if item not in initialList],
        # list ofthe files that are not in new list and are in old list.
        "deletedFiles":
        [item for item in initialList if item not in currentList],
    }


def sendDirectoryChange(directoryChange_A):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as soc:
        soc.connect(('127.0.0.1', port))
        soc.send(json.dumps(directoryChange_A).encode())
        data = soc.recv(1024).decode()
    soc.close()


def syncWithServerB(directoryChange_A, directoryChange_B):
    if len(directoryChange_A["addedFiles"]) + len(
            directoryChange_A["modifiedFiles"]) > 0:
        for fileName in directoryChange_A["addedFiles"] + directoryChange_A[
                "modifiedFiles"]:
            subprocess.run(
                ['scp',
                 getAbsoloutePathA(fileName), absPathToDirectoryB],
                shell=True,
                check=True)

    modifiedFilesAtB = list(directoryChange_B["modifiedFilesData"].keys())

    for file in modifiedFilesAtB:
        if oct(os.stat(getAbsoloutePathA(file)).st_mode & 0o777)[-3:] == '444':
            print(file, ' is Locked\n')
            if file not in Queue.keys():
                Queue[file] = directoryChange_B["modifiedFilesData"][file]
            else:
                Queue[file] = Queue[file] + directoryChange_B[
                    "modifiedFilesData"][file]

    for file in directoryChange_B['deletedFiles']:
        if oct(os.stat(getAbsoloutePathA(file)).st_mode & 0o777)[-3:] == '444':
            # remove if queue exists for that file
            Queue[file] = '@@delete@@'
        else:
            os.remove(getAbsoloutePathA(file))


def getSortedFileListWithAttributes(fileList):
    attributedFileList = []
    for item in fileList:
        attributedFileList.append({
            # reference : https://www.w3resource.com/python-exercises/python-basic-exercise-107.php(object and value getting reference)
            "File":
            item,
            "Size":
            convert_bytes(os.path.getsize(getAbsoloutePathA(item))),
            "accessTime":
            time.ctime(os.path.getatime(getAbsoloutePathA(item))),
            "modifiedTime":
            time.ctime(modifiedTime(getAbsoloutePathA(item))),
            "assignedPermissions":
            oct(os.stat(getAbsoloutePathA(item)).st_mode)
        })

    attributedFileList.sort(key=lambda x: x["File"])

    return attributedFileList


def deployQueuedOperations(file):
    print(Queue)
    if file in Queue.keys():
        dataInQueue = Queue[file]
        fileData = readFile(getAbsoloutePathA(file))
        if dataInQueue == "@@delete@@":
            os.remove(getAbsoloutePathA(file))
        else:
            queuedPatches = dmp.patch_fromText(dataInQueue)
            print(dmp.patch_apply(queuedPatches, fileData))
            f = open(getAbsoloutePathA(file), 'w')
            f.write(dmp.patch_apply(queuedPatches, fileData)[0])
            f.close()

        del Queue[file]


syncServers()

while (1):
    # storing up last modified time of each file in server A
    initialListModifiedTime = {}
    for file in filesInServerA():
        initialListModifiedTime[file] = (modifiedTime(getAbsoloutePathA(file)))

    soc = socket.socket()
    soc.bind(('127.0.0.1', port))
    soc.listen(5)
    conn, address = soc.accept()
    print("\nServer A listening...\n\n")

    data = conn.recv(1000000).decode()

    print("Time : ", time.strftime("%H:%M:%S", time.localtime()), '\n')
    print("\nQueue : ", Queue)
    print("\nRecieved Data : \t", data, '\n')

    # architecture is designed in such a way that when we recieve a JSON object we know it's B trying to communicate
    # if we recieve a string or JSON list it's client
    try:
        # trying to load json from data
        loadedData = json.loads(data)
        if type(loadedData) == list:
            raise Exception(
                '\n\nRecieved request from client for locking/unlocking file.')

        # closing socket because A will be sending data now and B will be listening
        conn.close()
        soc.close()

        directoryChange_B = loadedData
        print("File changes at Server B : ", directoryChange_B)

        directoryChange_A = getDirectoryChange_A(initialListModifiedTime)
        print("File changes at Server A : ", directoryChange_A)

        # sending the directory change at A to server B
        sendDirectoryChange(directoryChange_A)

        # putting A in sync with respect to the changes in server B
        syncWithServerB(directoryChange_A, directoryChange_B)
        print(
            "\n\n**********************************************************************#-"
        )

    except Exception as ex:

        sortedExtendedFileListServerA = getSortedFileListWithAttributes(
            filesInServerA())

        if str(
                ex
        ) == '\n\nRecieved request from client for locking/unlocking file.':
            args = json.loads(data)[-2:]
            file = getAbsoloutePathA(sortedExtendedFileListServerA[int(
                args[1])]['File'])
            if args[0] == '-lock':
                print('locking file : ', file)
                os.chmod(file, 0o444)
                print(oct(os.stat(file).st_mode))
                conn.send(("locked file : " + file).encode())

            if args[0] == '-unlock':
                print('unlocking file : ', file)
                os.chmod(file, 0o666)
                print(oct(os.stat(file).st_mode))
                conn.send(("unlocked file : " + file).encode())

                deployQueuedOperations(sortedExtendedFileListServerA[int(
                    args[1])]['File'])

        # sending JSON data of sorted fileList from both server to client
        conn.send(json.dumps(sortedExtendedFileListServerA).encode())

        # closing the socket and go into listening state again.
        print(
            "\n\n**********************************************************************#-"
        )
        conn.close()
        soc.close()
