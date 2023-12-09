import grpc
import os
import sys
import time
from concurrent.futures import ThreadPoolExecutor
# 添加路径

ROOT_PATH = '/Users/yuhaonan/Desktop/cpps/LiteDFS'
sys.path.append(ROOT_PATH)
sys.path.append(ROOT_PATH + '/storageServer')
sys.path.append(ROOT_PATH + '/managementServer')
# 数据服务器rpc
import storageServer_pb2 as st_pb2
import storageServer_pb2_grpc as st_pb2_grpc
# 管理服务器rpc
import managementServer_pb2 as ma_pb2
import managementServer_pb2_grpc as ma_pb2_grpc
# 参数文件
import parameter

class File:
    def __init__(self, name):
        self.name = name

    def __str__(self):
        return self.name


class Folder:
    def __init__(self, name):
        self.name = name
        self.contents = []

    def add_file(self, file):
        self.contents.append(file)

    def remove_file(self, path):
        path_list = path.split("/")
        while "" in path_list:
            path_list.remove("")
        tmp_folder = self
        for name in path_list:
            found = False
            for item in tmp_folder.contents:
                if item.name == name:
                    if name == path_list[-1]:
                        tmp_folder.contents.remove(item)
                        return True
                    tmp_folder = item
                    found = True
                    break
            if not found:
                return False
        return False

    def find(self, file_name):
        for item in self.contents:
            if item.name == file_name:
                return item
        return None

    def __str__(self, level=0):
        result = f"{'  ' * level}Folder: {self.name}\n"
        for item in self.contents:
            if isinstance(item, File):
                result += f"{'  ' * (level + 1)}File: {item}\n"
            elif isinstance(item, Folder):
                result += item.__str__(level + 1)
        return result
    
    def get_tree(self, indent=""):
        tree = []
        tree.append(indent + self.name + "/")
        for item in self.contents:
            if isinstance(item, File):
                tree.append(indent + "  " + item.name)
            elif isinstance(item, Folder):
                tree.extend(item.get_tree(indent + "  "))
        return tree
    
    def get_item(self, path):
        path_list = path.split("/")
        while "" in path_list:
            path_list.remove("")
        tmp_folder = self
        for name in path_list:
            found = False
            for item in tmp_folder.contents:
                if item.name == name:
                    tmp_folder = item
                    found = True
                    break
            if not found:
                return None
        return tmp_folder
    
    def write_to_file(self, file_path):
        with open(file_path, 'w') as file:
            file.write("\n".join(self.get_tree()))

    @staticmethod
    def read_from_file(file_path):
        try:
            with open(file_path, 'r') as file:
                lines = file.readlines()
            return Folder._build_from_tree_lines(lines)
        except:
            return None

    @staticmethod
    def _build_from_tree_lines(lines):
        def build_tree_helper(lines, level):
            if not lines:
                return None

            line = lines[0]
            curr_level = (len(line) - len(line.lstrip())) // 2

            if curr_level < level:
                return None

            if "/" in line:
                folder_name = line.strip().strip('/')
                node = Folder(folder_name)
            else:
                file_name = line.lstrip()
                node = File(file_name)

            lines.pop(0)
            while lines and curr_level == level:
                child = build_tree_helper(lines, level + 1)
                if child:
                    node.contents.append(child)
                else:
                    return node
            return node

        return build_tree_helper(lines, 0)


class maServer(st_pb2_grpc.storageServerServicer):

    def __init__(self):
        self.ip = parameter._MANAGEMENT_IP
        self.port = parameter._MANAGEMENT_PORT
        # 维护在线服务器信息
        self.serverList = list()
        # 维护上锁文件，数据结构为字典: path->id
        self.lockList = dict()
        self.file_system = Folder.read_from_file("file_tree.txt")
        if self.file_system == None:
            self.file_system = Folder("root")
        self.stStubs = list()
        print('Management Server is online')

    def save(self):
        self.file_system.write_to_file("file_tree.txt")
    
    def offline(self):
        # 当还存在在线数据服务器时，发送警告
        if len(self.serverList):
            print('Warning: There are still online servers. Closing may cause exceptions.')
        print('Management Server is offline')

    def serverOnline(self, request, context):
        # 数据服务器上线，向管理器注册信息
        self.serverList.append(request)
        stChannel = grpc.insecure_channel(request.ip+':'+str(request.port))
        self.stStubs.append([request.id,st_pb2_grpc.storageServerStub(stChannel)])
        print('Storage Server:%d is online'%request.id)
        return ma_pb2.ma_reply(done = 1)
        
    def serverOffline(self, request, context):
        # 数据服务器下线，向管理器注销信息
        remove_id = request.id
        for server in self.serverList:
            if server.id == remove_id:
                remove_server = server
                break
        for stStub in self.stStubs:
            if stStub[0] == remove_id:
                remove_stStub = stStub
                break
        self.serverList.remove(remove_server)
        self.stStubs.remove(remove_stStub)
        print('Storage Server:%d is offline'%request.id)
        return ma_pb2.ma_reply(done = 1)
    
    def create(self, request, context):
        path = request.path
        name = request.name
        folder = self.file_system.get_item(path)
        folder.add_file(File(name))
        return ma_pb2.ma_reply(done = 1)

    def delete(self, request, context):
        return ma_pb2.ma_reply(done = self.file_system.remove_file(request.path))

    def mkdir(self, request, context):
        path = request.path
        name = request.name
        folder = self.file_system.get_item(path)
        folder.add_file(Folder(name))
        return ma_pb2.ma_reply(done = 1)

        
    def getServer(self, request, context):
        # 获取在线数据服务器信息
        for stStub in self.stStubs:
            if stStub[1].check(st_pb2.file_path(path = request.path)).done:
                for server in self.serverList:
                    if server.id == stStub[0]:
                        return ma_pb2.serverInfo(id = server.id, ip = server.ip, port = server.port)
        return ma_pb2.serverInfo(id = -1, ip = -1, port = -1)
            
    def getServerList(self, request, context):
        # 获取在线数据服务器信息
        server_list = list()
        for server in self.serverList:
            server_list.append(server)
        return ma_pb2.serverList(list = server_list)

    def lockFile(self, request, context):
        # 给文件上锁
        print('Lock: '+request.filePath)
        if request.filePath in self.lockList:
            finish = 0
            if request.clientId == self.lockList[request.filePath]:
                reply = 'Alreay lock this file'
            else:
                reply = 'This file is locked by other client'
        else:
            finish = 1
            self.lockList[request.filePath] = request.clientId
            reply = 'Successfully lock the file, do not forget to unlock it after used'
        return ma_pb2.lockReply(done = finish, info = reply)

    def unlockFile(self, request, context):
        # 给文件解锁
        # 给文件上锁
        print('Unlock: '+request.filePath)
        if request.filePath in self.lockList:
            if request.clientId == self.lockList[request.filePath]:
                finish = 1
                del self.lockList[request.filePath]
                reply = 'Successfully unlock the file'
            else:
                reply = 'This file is locked by other client, you can`t unlock it'
        else:
            finish = 1
            reply = 'This file isn`t locked by any client'
        return ma_pb2.lockReply(done = finish, info = reply)
    
    def ls(self, request, context):
        # 客户端向服务器查询当前目录
        dirList = "\n".join([folder.name for folder in self.file_system.get_item(request.path).contents])
        return ma_pb2.fileList(list = dirList)

    def tree(self, request, context):
        # 客户端向服务器查询当前目录
        dirList = "\n".join(self.file_system.get_item(request.path).get_tree())
        return ma_pb2.fileList(list = dirList)
        

if __name__=="__main__":
    # 开启管理服务器
    ma_server = maServer()
    server = grpc.server(ThreadPoolExecutor(max_workers=5))
    ma_pb2_grpc.add_managementServerServicer_to_server(ma_server, server)
    server.add_insecure_port(parameter._MANAGEMENT_IP+':'+parameter._MANAGEMENT_PORT)
    server.start()
    try:
        while True:
            time.sleep(parameter._ONE_DAY_IN_SECONDS)
    except KeyboardInterrupt:
        # 管理服务器下线
        # 将文件树写入文本文件
        ma_server.save()
        ma_server.offline()
        server.stop(0)