import socket
import threading
import queue
import json  # json.dumps(some)打包   json.loads(some)解包
import time
import os
import os.path
import requests
import sys
from user_auth import UserAuth

# IP = socket.gethostbyname(socket.getfqdn(socket.gethostname()))
IP = ''
PORT = 50007
apikey = 'ee19328107fa41e987a42a064a68d0da'
url = 'http://openapi.tuling123.com/openapi/api/v2'
que = queue.Queue()                             # 用于存放客户端发送的信息的队列
users = []                                      # 用于存放在线用户的信息  [conn, user, addr]
lock = threading.Lock()                         # 创建锁, 防止多个线程写入数据的顺序打乱

# 确保必要的目录存在
def ensure_directories():
    # 用户数据目录
    if not os.path.exists('./user_data'):
        os.makedirs('./user_data')
    
    # 图片缓存目录
    if not os.path.exists('./Server_image_cache'):
        os.makedirs('./Server_image_cache')
    
    # 资源目录
    if not os.path.exists('./resources'):
        os.makedirs('./resources')

# 确保目录存在
ensure_directories()

# 创建用户认证对象，文件保存在用户数据目录
user_auth = UserAuth(csv_file='./user_data/users.csv')

def call_robot(url, apikey, msg):
    data = {
        "reqType": 0,
        "perception": {
            "inputText": {  # inputText文本信息
                "text": msg
            },
            # 用户输入图片url
            "inputImage": {  # 图片信息，后跟参数信息为url地址，string类型
                "url": "https://cn.bing.com/images/"
            },
            # 用户输入音频地址信息
            "inputMedia": {  # 音频信息，后跟参数信息为url地址，string类型
                "url": "https://www.1ting.com/"
            },
            # 客户端属性信息
            "selfInfo": {  # location 为selfInfo的参数信息，
                "location": {  # 地理位置信息
                    "city": "杭州",  # 所在城市，不允许为空
                    "province": "浙江省",  # 所在省份，允许为空
                    "street": "灵隐街道"  # 所在街道，允许为空
                }
            },
        },
        "userInfo": {  # userInfo用户参数，不允许为空
            "apiKey": "ee19328107fa41e987a42a064a68d0da",  # 你注册的apikey,机器人标识,32位
            "userId": "Brandon"  # 随便填，用户的唯一标识，长度小于等于32位
        }
    }
    headers = {'content-type': 'application/json'}  # 必须是json
    r = requests.post(url, headers=headers, data=json.dumps(data))
    return r.json()

#####################################################################################


# 将在线用户存入online列表并返回
def onlines():
    online = []
    for i in range(len(users)):
        online.append(users[i][1])
    return online


class ChatServer(threading.Thread):
    global users, que, lock

    def __init__(self, port):
        threading.Thread.__init__(self)
        # self.setDaemon(True)
        self.ADDR = ('', port)
        # self.PORT = port
        os.chdir(sys.path[0])
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # self.conn = None
        # self.addr = None

    # 用于接收所有客户端发送信息的函数
    def tcp_connect(self, conn, addr):
        # 接收用户信息并进行身份验证
        try:
            auth_data = conn.recv(1024).decode()
            auth_data = json.loads(auth_data)
            
            username = auth_data.get('username', '')
            password_hash = auth_data.get('password', '')
            is_register = auth_data.get('is_register', False)
            
            if is_register:
                success, message = user_auth.register_user(username, password_hash)
                conn.send(message.encode())
                if not success:
                    conn.close()
                    return
            else:
                success, message = user_auth.verify_user(username, password_hash)
                conn.send(message.encode())
                if not success:
                    conn.close()
                    return
            
            user = username
            
            # 检查用户名是否已在线
            for i in range(len(users)):
                if user == users[i][1]:
                    print('User already online')
                    user = '' + user + '_2'
                    
            users.append((conn, user, addr))
            print(' New connection:', addr, ':', user, end='')
            d = onlines()
            self.recv(d, addr)
            
            # 处理消息接收
            try:
                while True:
                    data = conn.recv(1024)
                    data = data.decode()
                    self.recv(data, addr)
                conn.close()
            except:
                print(user + ' Connection lose')
                self.delUsers(conn, addr)
                conn.close()
        except Exception as e:
            print(f"Authentication error: {e}")
            conn.close()

    # 判断断开用户在users中是第几位并移出列表, 刷新客户端的在线用户显示
    def delUsers(self, conn, addr):
        a = 0
        for i in users:
            if i[0] == conn:
                users.pop(a)
                print(' Remaining online users: ', end='')         # 打印剩余在线用户(conn)
                d = onlines()
                self.recv(d, addr)
                print(d)
                break
            a += 1

    # 将接收到的信息(ip,端口以及发送的信息)存入que队列
    def recv(self, data, addr):
        lock.acquire()
        try:
            que.put((addr, data))
        finally:
            lock.release()

    # 将队列que中的消息发送给所有连接到的用户
    def sendData(self):
        while True:
            if not que.empty():
                data = ''
                reply_text = ''
                message = que.get()                               # 取出队列第一个元素
                if isinstance(message[1], str):                   # 如果data是str则返回Ture
                    for i in range(len(users)):
                        # user[i][1]是用户名, users[i][2]是addr, 将message[0]改为用户名
                        for j in range(len(users)):
                            if message[0] == users[j][2]:
                                print(' this: message is from user[{}]'.format(j))
                                if '@Robot' in message[1] and reply_text == '':
                                    
                                    msg = message[1].split(':;')[0]
                                    reply = call_robot(url, apikey, msg)
                                    reply_text = reply['results'][0]['values']['text']
                                    data = ' ' + users[j][1] + '：' + message[1] + ':;' + 'Robot：' + '@' + \
                                           users[j][1] + ',' + reply_text
                                    break
                                elif '@Robot' in message[1] and (not reply_text == ''):
                                    data = ' ' + users[j][1] + '：' + message[1] + ':;' + 'Robot：' + '@' + \
                                           users[j][1] + ',' + reply_text
                                else:
                                    data = ' ' + users[j][1] + '：' + message[1]
                                    break      
                        users[i][0].send(data.encode())
                # data = data.split(':;')[0]
                if isinstance(message[1], list):  # 同上
                    # 如果是list则打包后直接发送  
                    data = json.dumps(message[1])
                    for i in range(len(users)):
                        try:
                            users[i][0].send(data.encode())
                        except:
                            pass

    def run(self):

        self.s.bind(self.ADDR)
        self.s.listen(5)
        print('Chat server starts running...')
        q = threading.Thread(target=self.sendData)
        q.start()
        while True:
            conn, addr = self.s.accept()
            t = threading.Thread(target=self.tcp_connect, args=(conn, addr))
            t.start()
        self.s.close()

################################################################


class FileServer(threading.Thread):
    def __init__(self, port):
        threading.Thread.__init__(self)
        # self.setDaemon(True)
        self.ADDR = ('', port)
        # self.PORT = port
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.first = r'.\resources'
        os.chdir(self.first)                                     # 把first设为当前工作路径
        # self.conn = None

    def tcp_connect(self, conn, addr):
        print(' Connected by: ', addr)
        
        while True:
            data = conn.recv(1024)
            data = data.decode()
            if data == 'quit':
                print('Disconnected from {0}'.format(addr))
                break
            order = data.split(' ')[0]                             # 获取动作
            self.recv_func(order, data, conn)
                
        conn.close()

    # 传输当前目录列表
    def sendList(self, conn):
        listdir = os.listdir(os.getcwd())
        listdir = json.dumps(listdir)
        conn.sendall(listdir.encode())

    # 发送文件函数
    def sendFile(self, message, conn):
        name = message.split()[1]                               # 获取第二个参数(文件名)
        fileName = r'./' + name
        with open(fileName, 'rb') as f:    
            while True:
                a = f.read(1024)
                if not a:
                    break
                conn.send(a)
        time.sleep(0.1)                                          # 延时确保文件发送完整
        conn.send('EOF'.encode())

    # 保存上传的文件到当前工作目录
    def recvFile(self, message, conn):
        name = message.split()[1]                              # 获取文件名
        fileName = r'./' + name
        with open(fileName, 'wb') as f:
            while True:
                data = conn.recv(1024)
                if data == 'EOF'.encode():
                    break
                f.write(data)

    # 切换工作目录
    def cd(self, message, conn):
        message = message.split()[1]                          # 截取目录名
        # 如果是新连接或者下载上传文件后的发送则 不切换 只将当前工作目录发送过去
        if message != 'same':
            f = r'./' + message
            os.chdir(f)
        # path = ''
        path = os.getcwd().split('\\')                        # 当前工作目录
        for i in range(len(path)):
            if path[i] == 'resources':
                break
        pat = ''
        for j in range(i, len(path)):
            pat = pat + path[j] + ' '
        pat = '\\'.join(pat.split())
        # 如果切换目录超出范围则退回切换前目录
        if 'resources' not in path:
            f = r'./resources'
            os.chdir(f)
            pat = 'resources'
        conn.send(pat.encode())

    # 判断输入的命令并执行对应的函数
    def recv_func(self, order, message, conn):
        if order == 'get':
            return self.sendFile(message, conn)
        elif order == 'put':
            return self.recvFile(message, conn)
        elif order == 'dir':
            return self.sendList(conn)
        elif order == 'cd':
            return self.cd(message, conn)

    def run(self):
        print('File server starts running...')
        self.s.bind(self.ADDR)
        self.s.listen(3)
        while True:
            conn, addr = self.s.accept()
            t = threading.Thread(target=self.tcp_connect, args=(conn, addr))
            t.start()
        self.s.close()

#############################################################################


class PictureServer(threading.Thread):

    def __init__(self, port):
        threading.Thread.__init__(self)
        # self.setDaemon(True)
        self.ADDR = ('', port)
        # self.PORT = port
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # self.conn = None
        os.chdir(sys.path[0])
        self.folder = '.\\Server_image_cache\\'  # 图片的保存文件夹

    def tcp_connect(self, conn, addr):
        while True:
            data = conn.recv(1024)
            data = data.decode()
            print('Received message from {0}: {1}'.format(addr, data))
            if data == 'quit':
                break
            order = data.split()[0]  # 获取动作
            self.recv_func(order, data, conn)
        conn.close()
        print('---')

    # 发送文件函数
    def sendFile(self, message, conn):
        print(message)
        name = message.split()[1]                   # 获取第二个参数(文件名)
        fileName = self.folder + name               # 将文件夹和图片名连接起来
        f = open(fileName, 'rb')
        while True:
            a = f.read(1024)
            if not a:
                break
            conn.send(a)
        time.sleep(0.1)                             # 延时确保文件发送完整
        conn.send('EOF'.encode())
        print('Image sent!')

    # 保存上传的文件到当前工作目录
    def recvFile(self, message, conn):
        print(message)
        name = message.split(' ')[1]                   # 获取文件名
        fileName = self.folder + name                  # 将文件夹和图片名连接起来
        print(fileName)
        print('Start saving!')
        f = open(fileName, 'wb+')
        while True:
            data = conn.recv(1024)
            if data == 'EOF'.encode():
                print('Saving completed!')
                break
            f.write(data)

    # 判断输入的命令并执行对应的函数
    def recv_func(self, order, message, conn):
        if order == 'get':
            return self.sendFile(message, conn)
        elif order == 'put':
            return self.recvFile(message, conn)

    def run(self):
        self.s.bind(self.ADDR)
        self.s.listen(5)
        print('Picture server starts running...')
        while True:
            conn, addr = self.s.accept()
            t = threading.Thread(target=self.tcp_connect, args=(conn, addr))
            t.start()
        self.s.close()

####################################################################################


if __name__ == '__main__':
    cserver = ChatServer(PORT)
    fserver = FileServer(PORT + 1)
    pserver = PictureServer(PORT + 2)
    cserver.start()
    fserver.start()
    pserver.start()
    while True:
        time.sleep(1)
        if not cserver.isAlive():
            print("Chat connection lost...")
            sys.exit(0)
        if not fserver.isAlive():
            print("File connection lost...")
            sys.exit(0)
        if not pserver.isAlive():
            print("Picture connection lost...")
            sys.exit(0)
