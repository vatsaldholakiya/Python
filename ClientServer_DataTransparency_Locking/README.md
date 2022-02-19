# Client Server Architecture demonstrating Data Transparency as well as Locking mechanism

## Problem Description
   - A try on achieving Data transparency and locking mechanism while accepting the updates.
   - To achieve data transparency, data replication among servers has been implemented at certain Interval of time (5 sec) as the size of data is not large.
   - User on server side can alter(add/modify/delete) file on Server A or Server B.
   - When a file on any server is altered(add/modify/delete) while it is unlocked, the change should be reflected on the other server.
   - When a file on any server B is altered(modify/delete) while it is locked on server A, the update should be put in a queue maintained at server A.
   - User on client side can fetch list of files present on Server A and it cannot directly connect to server B.
   - User on client side can lock/unlock file on server A by passing the index of file.
   - For the locked files at server A, a queue will be used on server A to keep a track of all the concerning updates that arise on Server B.
   - On unlocking a file on server A, all the queued updates should be executed making file on both the server just the same. 

## Memo
   - Folder and Files at server A and B are exactly the same, if not, will be made the same.
   
## Execution details

* Download the whole folder with following 3 subfolders:
   * Client
   * Server_A
   * Server_B


* Run Server_A.py file from the terminal
* Run Server_B.py file from the terminal
* Run Client file in the following way:
    * To fetch the list of files: __`python3 Client.py`__   
    * Result : ![Screenshot 2022-02-18 193252](https://user-images.githubusercontent.com/25501934/154781509-8dfe6bc6-ba5a-4856-805a-d18bff137f53.png)
    * To fetch the list of files: __`python3 Client.py -lock 2`__ replace 2 with the index of the file from the list.
    * Result: ![Screenshot 2022-02-18 195528](https://user-images.githubusercontent.com/25501934/154781606-73479032-33f5-4457-b8f9-37d87899bb79.png)
    * To fetch the list of files: __`python3 Client.py -unlock 2`__ replace 2 with the index of the file from the list
    * Results : ![Screenshot 2022-02-18 195847](https://user-images.githubusercontent.com/25501934/154781758-f547e058-d7de-4e18-a18d-4a54962c6763.png)



