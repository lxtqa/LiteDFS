import grpc
import os
import sys
import random
# 添加路径
ROOT_PATH = '/Users/yuhaonan/Desktop/cpps/LiteDFS'
sys.path.append(ROOT_PATH)
sys.path.append(ROOT_PATH + '/managementServer')
sys.path.append(ROOT_PATH + '/storageServer')
# 数据服务器rpc
import storageServer_pb2 as st_pb2
import storageServer_pb2_grpc as st_pb2_grpc
# 管理服务器rpc
import managementServer_pb2 as ma_pb2
import managementServer_pb2_grpc as ma_pb2_grpc
# 参数文件
import parameter

class Client():
    def __init__(self, id):
        self.id = id
        self.stStub = None
        self.root_path = parameter._ROOT_PATH+'/DATASTORE/client_%d/'%(id)
        self.cur_path = ''
        self.openFile = list() # 已打开文件列表
        # 创建数据的主文件夹作为用户的缓存
        if not os.path.exists(self.root_path):  
            os.mkdir(self.root_path)
        # 连接到管理服务器
        print('Connect with the Management Server ...')
        maChannel = grpc.insecure_channel(parameter._MANAGEMENT_IP+':'+parameter._MANAGEMENT_PORT)
        self.maStub = ma_pb2_grpc.managementServerStub(maChannel)

    def initStServer(self,path):
        response = self.maStub.getServer(ma_pb2.filepath(path = path))
        if response.ip != -1:
            stChannel = grpc.insecure_channel(response.ip+':'+str(response.port))
            self.stStub = st_pb2_grpc.storageServerStub(stChannel)
    
    # def selectStorageServer(self):
    #     try:
    #         response = self.maStub.getServerList(ma_pb2.empty(e = 1))
    #         print('Please choose a storage server:')
    #         print('***********************************')
    #         for info in response.list:
    #             print('Server %d   ip:'%info.id+info.ip+'   port:%d'%info.port)
    #         print('***********************************')
    #         while True:
    #             success = False
    #             if len(response.list) == 0:
    #                 print('No server online. Client startup failed.')
    #                 exit(0)
    #             try:
    #                 chooseString = input('The id of server to connect:')
    #             except KeyboardInterrupt:
    #                 self.quit()
    #                 print("Client {} is offline".format(self.id))
    #                 break
                
    #             if chooseString == "":
    #                 choose = response.list[random.randint(0,len(response.list)-1)].id
    #             else:
    #                 choose = int(chooseString)
    #             for info in response.list:
    #                 if info.id == choose:
    #                     serverIp = info.ip
    #                     serverPort = info.port
    #                     success = True
    #                     break
    #             if success:
    #                 break
    #             print('The idx of server is not online.')
    #         print(serverIp+':'+str(serverPort))
    #         stChannel = grpc.insecure_channel(serverIp+':'+str(serverPort))
    #         self.stStub = st_pb2_grpc.storageServerStub(stChannel)
    #         self.server_root_path = ROOT_PATH+'/DATASTORE/storage_%d/'%(choose)
    #         print('Client %d'%self.id + ' successfully startup and connect with server %d'%choose)
    #     except Exception as e:
    #         print(e.args)
    #         print('Client startup failed.')
    
    def ls(self):
        response = self.maStub.ls(ma_pb2.filepath(path = self.cur_path))
        print(response.list)

    def tree(self):
        response = self.maStub.tree(ma_pb2.filepath(path = self.cur_path))
        print(response.list)

    def mkdir(self, fileName):
        self.initStServer(self.cur_path)
        response = self.stStub.mkdir(st_pb2.file_path(path = self.cur_path+fileName))
        response = self.maStub.mkdir(ma_pb2.file(path = self.cur_path,name = fileName))
        if response.done:
            print('Successfully create dir:%s.'%fileName)
        else:
            print('Create failed.')
    
    def rm(self, fileName):
        self.initStServer(self.cur_path+fileName)
        self.stStub.synDelete(st_pb2.file_path(path = self.cur_path+fileName))
        response = self.maStub.delete(ma_pb2.filepath(path = self.cur_path+fileName))
        if response.done:
            path = self.root_path+self.cur_path+fileName
            if os.path.exists(path):
                os.remove(path)
            print('Successfully delete dir:%s.'%fileName)
        else:
            print('Delete failed.')
    
    def download(self, fileName):
        self.initStServer(self.cur_path+fileName)
        response = self.maStub.getServer(ma_pb2.filepath(path = self.cur_path+fileName))
        stChannel = grpc.insecure_channel(response.ip+':'+str(response.port))
        self.stStub = st_pb2_grpc.storageServerStub(stChannel)
        # self.server_root_path = ROOT_PATH+'/DATASTORE/storage_%d/'%(response.info.id)
        try:
            response = self.stStub.download(st_pb2.file_path(path = self.cur_path+fileName))
            # 二进制打开文件用于写入
            path = self.root_path + self.cur_path
            # 本地文件不存在就创建
            if not os.path.exists(path):
                os.mkdir(path)
            with open(path+fileName, 'wb') as f:
                for i in response:
                    f.write(i.buffer)
            print('Successfully download the file.')
        except Exception as e:
            print(e.args)
            print('Download failed.')
    
    def create(self, fileName):
        path = self.root_path + self.cur_path
        # 本地文件不存在就创建
        if not os.path.exists(path):
            os.mkdir(path)
        with open(path+fileName, 'w') as f:
            try:
                msg = input("Enter your file content: use ctrl+c to end input\n")
                f.write(msg+"\n")
                while True:
                    msg = input()
                    f.write(msg+"\n")
            except KeyboardInterrupt:
                # 结束写入
                f.close()
        print('Successfully create file:'+fileName)
        self.initStServer(self.cur_path)
        self.maStub.create(ma_pb2.file(path = self.cur_path,name = fileName))
        self.upload(fileName)

    def getBuffer(self, rPath, path):
        # 根据文件相对路径和本地绝对路径返回流式数据
        with open(path, 'rb') as f:
            buf = f.read(parameter._BUFFER_SIZE)
            yield st_pb2.upload_file(path = rPath, buffer = buf)

    def upload(self, fileName):
        try:
            path = self.root_path + self.cur_path + fileName # 本地绝对路径
            rPath = self.cur_path + fileName # 相对路径
            self.initStServer(self.cur_path)
            if os.path.exists(path):
                response = self.stStub.synUpload(self.getBuffer(rPath, path))
                print('Successfully upload the file.')
            else:
                print('Can\'t find this file.')
        except Exception as e:
            print(e.args)
            print('Upload failed.')
    
    def cd(self, fold):
        ## TODO
        if fold == "..":
            self.cdBack()
            return
        response = self.maStub.ls(st_pb2.file_path(path = self.cur_path))
        #path = self.server_root_path + self.cur_path+fold
        if fold in response.list:# and os.path.isdir(path):
            # 成功进入文件夹
            self.cur_path += fold + '/'
        else:
            print('Can\'t enter this fold.')


    def cdBack(self):
        if (self.cur_path != ''):
            self.cur_path = os.path.dirname(self.cur_path[:-1])+'/'
            if self.cur_path == '/':
                self.cur_path = ''
        else:
            print('Alreay in root dir.')

    def open(self, fileName):
        response = self.maStub.ls(st_pb2.file_path(path = self.cur_path))
        if fileName in response.list:# and os.path.isfile(self.server_root_path+self.cur_path+fileName):
            # 确定文件存在且是文件而非文件夹
            # 对文件进行上锁
            response = self.maStub.lockFile(ma_pb2.lockInfo(clientId=self.id, filePath=self.cur_path+fileName))
            if response.done == 1:
                # 成功上锁
                self.openFile.append(self.cur_path+fileName)
                # 下载文件到本地
                self.download(fileName)
                print('Successfully open: '+fileName)
            else:
                print(response.info)
        else:
            print('Can\'t find this file.')

    def read(self, fileName):
        # 输出文件信息
        if self.cur_path+fileName not in self.openFile:
            print('You haven\'t open this file.')
            return
        print('************FILE CONTENT*************')
        with open(self.root_path+self.cur_path+fileName, 'r') as f:
            buf = f.read()
            print(buf)
        f.close()
        print('*************************************')

    def write(self, fileName):
        with open(self.root_path+self.cur_path+fileName, 'w') as file:
            try:
                msg = input("Enter the new content: use ctrl+c to end input\n")
                file.write(msg+"\n")
                while True:
                    msg = input()
                    file.write(msg+"\n")
            except KeyboardInterrupt:
                # 结束写入
                file.close()
                print(f"Content written to {self.cur_path+fileName}")
            
    def close(self, fileName):
        path = self.cur_path + fileName
        if path in self.openFile:
            self.openFile.remove(path)
            # 上传文件
            self.upload(fileName)
            # 解锁文件
            response = self.maStub.unlockFile(ma_pb2.lockInfo(clientId=self.id, filePath=self.cur_path+fileName))
            if response.done == 1:
                os.remove(self.root_path+self.cur_path+fileName)
                print('Successfully close: '+fileName)
            else:
                print(response.info)
        else:
            print('You haven\'t open this file.')
    
    def quit(self):
        for path in self.openFile:
            fileName = path.split("/")[-1]
            # 上传文件
            self.upload(fileName)
            # 解锁文件
            response = self.maStub.unlockFile(ma_pb2.lockInfo(clientId=self.id, filePath=self.cur_path+fileName))
            if response.done == 1:
                os.remove(self.root_path+self.cur_path+fileName)
                print('Successfully close: '+fileName)
            else:
                print(response.info)

    def help(self):
        print('client ID: %d'%(self.id))
        print("------------------COMMAND LIST------------------")
        print("ls: list file directories")
        print("cd: change current path")
        print("cd..: back to previous path")
        print("create: create files locally")
        print("open: open files")
        print("read: read files")
        print("write: write files")
        print("close: close files")
        print("mkdir: create folder")
        print("rm: delete files")
        print("quit: quit terminal")
        print("------------------------------------------------")


# 启动客户端
def startClient(id):
    client = Client(id)
    while True:
        print('$'+client.cur_path+'>', end = '')
        try:
            command = input().split()
        except KeyboardInterrupt:
            client.quit()
            print("Client {} is offline".format(id))
            break
        if len(command) == 0:
            continue
        elif command[0] == 'help':
            client.help()
        elif command[0] == 'ls':
            client.ls()
        elif command[0] == 'tree':
            client.tree()
        elif command[0] == 'cd..':
            client.cdBack()
        elif command[0] == 'cd':
            client.cd(command[1])
        elif command[0] == 'upload':
            client.upload(command[1])
        elif command[0] == 'download':
            client.download(command[1])
        elif command[0] == 'rm':
            client.rm(command[1])
        elif command[0] == 'mkdir':
            client.mkdir(command[1])
        elif command[0] == 'open':
            client.open(command[1])
        elif command[0] == 'read':
            client.read(command[1])
        elif command[0] == 'write':
            client.write(command[1])
        elif command[0] == 'close':
            client.close(command[1])
        elif command[0] == 'create':
            client.create(command[1])
        elif command[0] == 'disconnect':
            client.disconnect()
        elif command[0] == 'quit':
            client.quit()
            break
        

if __name__=="__main__":
    # 执行时输入客户端id: python3 client.py arg_id
    clientId = int(sys.argv[1])
    startClient(clientId)