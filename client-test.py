import socket
import threading
import json  # json.dumps(some)打包   json.loads(some)解包
import tkinter
import tkinter.messagebox
from tkinter.scrolledtext import ScrolledText  # 导入多行文本框用到的包
import time
import requests
from tkinter import filedialog
import vachat
import os
import hashlib
from time import sleep
from PIL import Image, ImageTk, ImageSequence
from PIL import ImageGrab
from netifaces import interfaces, ifaddresses, AF_INET6

IP = ''
PORT = ''
user = ''
password = ''
listbox1 = ''  # 用于显示在线用户的列表框
ii = 0  # 用于判断是开还是关闭列表框
users = []  # 在线用户列表
chat = '------Group chat-------'  # 聊天对象, 默认为群聊
is_register = False  # 标识是注册还是登录

# 表情功能初始化
b1 = ''
b2 = ''
b3 = ''
b4 = ''
p1 = None
p2 = None
p3 = None
p4 = None
dic = {}
ee = 0

# GIF表情功能初始化
g1 = ''
g2 = ''
g3 = ''
g4 = ''
gp1 = None
gp2 = None
gp3 = None
gp4 = None
gdic = {}
ge = 0

# 视频聊天初始化
IsOpen = False    # 判断视频/音频的服务器是否已打开
Resolution = 0    # 图像传输的分辨率 0-4依次递减
Version = 4       # 传输协议版本 IPv4/IPv6
ShowMe = True     # 视频聊天时是否打开本地摄像头
AudioOpen = True  # 是否打开音频聊天

# 登陆窗口
root = tkinter.Tk()
root.title('Log in')
root['height'] = 200
root['width'] = 300
root.resizable(0, 0)  # 限制窗口大小

IP1 = tkinter.StringVar()
IP1.set('127.0.0.1:50007')  # 默认显示的ip和端口
User = tkinter.StringVar()
User.set('')
Password = tkinter.StringVar()
Password.set('')
LoginMode = tkinter.StringVar()
LoginMode.set('login')  # 'login', 'register', or 'deregister'

# 初始化聊天相关变量
chat = '------Group chat-------'  # 聊天对象, 默认为群聊

# 服务器标签
labelIP = tkinter.Label(root, text='Server address')
labelIP.place(x=20, y=10, width=100, height=20)

entryIP = tkinter.Entry(root, width=80, textvariable=IP1)
entryIP.place(x=120, y=10, width=160, height=20)

# 用户名标签
labelUser = tkinter.Label(root, text='Username')
labelUser.place(x=20, y=40, width=100, height=20)

entryUser = tkinter.Entry(root, width=80, textvariable=User)
entryUser.place(x=120, y=40, width=160, height=20)

# 密码标签
labelPassword = tkinter.Label(root, text='Password')
labelPassword.place(x=20, y=70, width=100, height=20)

entryPassword = tkinter.Entry(root, width=80, textvariable=Password, show='*')
entryPassword.place(x=120, y=70, width=160, height=20)

# 设置模式函数
def set_login_mode():
    LoginMode.set('login')
    loginButton.config(text='Login')
    root.title('Log in')

def set_register_mode():
    LoginMode.set('register')
    loginButton.config(text='Register')
    root.title('Register')

def set_deregister_mode():
    LoginMode.set('deregister')
    loginButton.config(text='Deregister')
    root.title('Deregister')

# 创建模式选择的单选按钮
login_rb = tkinter.Radiobutton(root, text='Login', variable=LoginMode, value='login', command=set_login_mode)
login_rb.place(x=30, y=100, width=70, height=30)

register_rb = tkinter.Radiobutton(root, text='Register', variable=LoginMode, value='register', command=set_register_mode)
register_rb.place(x=110, y=100, width=80, height=30)

deregister_rb = tkinter.Radiobutton(root, text='Deregister', variable=LoginMode, value='deregister', command=set_deregister_mode)
deregister_rb.place(x=200, y=100, width=80, height=30)

# 登录和注册按钮
def process_login_register(*args):
    global IP, PORT, user, password, is_register
    IP, PORT = entryIP.get().split(':')  # 获取IP和端口号
    PORT = int(PORT)                     # 端口号需要为int类型
    user = entryUser.get()
    password = entryPassword.get()
    
    if not user:
        tkinter.messagebox.showerror('Error', message='Username cannot be empty!')
        return
    
    if not password:
        tkinter.messagebox.showerror('Error', message='Password cannot be empty!')
        return
    
    # 设置是登录/注册/注销模式
    mode = LoginMode.get()
    is_register = (mode == 'register')
    is_deregister = (mode == 'deregister')
    
    try:
        # 登录或注册验证
        global s
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((IP, PORT))

        # 发送用户名和密码，以及是登录、注册还是注销
        auth_data = {
            "username": user,
            "password": hashlib.sha256(password.encode()).hexdigest(),
            "is_register": is_register,
            "is_deregister": is_deregister
        }
        s.send(json.dumps(auth_data).encode())

        # 接收服务器验证结果
        auth_result = s.recv(1024).decode()
        if auth_result == "AUTH_FAILED":
            tkinter.messagebox.showerror('Authentication Failed', message='Incorrect password!')
            s.close()
            return
        elif auth_result == "REGISTER_SUCCESS":
            tkinter.messagebox.showinfo('Success', message='Registration successful! You are now logged in.')
        elif auth_result == "LOGIN_SUCCESS":
            tkinter.messagebox.showinfo('Success', message='Login successful! Welcome back.')
        elif auth_result == "DEREGISTER_SUCCESS":
            tkinter.messagebox.showinfo('Success', message='User deregistered successfully!')
            s.close()
            return
        elif auth_result == "USER_EXISTS":
            tkinter.messagebox.showerror('Registration Failed', message='User already exists! Please try a different username.')
            s.close()
            return
        elif auth_result == "USER_NOT_FOUND":
            tkinter.messagebox.showerror('Error', message='User not found! Please check your username or register.')
            s.close()
            return

        # 如果没有用户名则将ip和端口号设置为用户名
        addr = s.getsockname()  # 获取客户端ip和端口号
        addr = addr[0] + ':' + str(addr[1])
        if user == '':
            user = addr
            
        # 登录成功，转换为聊天窗口
        # 清除登录窗口的所有控件
        for widget in root.winfo_children():
            widget.destroy()
        
        # 设置聊天窗口
        setup_chat_window()
        
    except Exception as e:
        tkinter.messagebox.showerror('Connection Error', message=f'Failed to connect to server: {str(e)}')
        return

def setup_chat_window():
    global listbox, chat, users
    # 确保聊天对象已初始化
    chat = '------Group chat-------'  # 聊天对象, 默认为群聊
    users = []  # 重置在线用户列表
    
    # 设置窗口属性
    root.title(user)  # 窗口命名为用户名
    root['height'] = 400
    root['width'] = 580
    root.resizable(0, 0)  # 限制窗口大小
    
    # 创建多行文本框
    listbox = ScrolledText(root)
    listbox.place(x=5, y=0, width=570, height=320)
    # 文本框使用的字体颜色
    listbox.tag_config('red', foreground='red')
    listbox.tag_config('blue', foreground='blue')
    listbox.tag_config('green', foreground='green')
    listbox.tag_config('pink', foreground='pink')
    listbox.insert(tkinter.END, 'Welcome to the chat room!', 'blue')
    
    # 这里添加所有聊天窗口的UI元素和功能
    setup_chat_ui()
    
    # 确保窗口处于活动状态
    root.update()
    
    # 启动GIF动画更新
    root.after(100, update_gifs)
    
    # 开始接收消息的线程
    r = threading.Thread(target=recv)
    r.start()

def setup_chat_ui():
    global eBut, pBut, sBut, fBut, button1, entry, a, button, vbutton, listbox1, ii, gBut
    global p1, p2, p3, p4, dic, b1, b2, b3, b4, ee
    global gp1, gp2, gp3, gp4, gdic, g1, g2, g3, g4, ge
    global gif_frames, gif_labels, last_gif_id  # 添加新的全局变量
    
    # 表情功能代码部分
    b1 = ''
    b2 = ''
    b3 = ''
    b4 = ''
    
    # GIF表情功能部分
    g1 = ''
    g2 = ''
    g3 = ''
    g4 = ''
    
    # 初始化GIF动画相关变量
    gif_frames = {}  # 用于存储GIF的帧序列
    gif_labels = {}  # 用于存储显示GIF的标签
    last_gif_id = 0   # 用于生成唯一的GIF ID
    
    # 将图片打开存入变量中
    try:
        p1 = tkinter.PhotoImage(file='./emoji/facepalm.png')
        p2 = tkinter.PhotoImage(file='./emoji/smirk.png')
        p3 = tkinter.PhotoImage(file='./emoji/concerned.png')
        p4 = tkinter.PhotoImage(file='./emoji/smart.png')
        # 用字典将标记与表情图片一一对应, 用于后面接收标记判断表情贴图
        dic = {'aa**': p1, 'bb**': p2, 'cc**': p3, 'dd**': p4}
        
        # 将GIF动图打开并调整大小后存入变量中
        # 使用PIL库加载GIF并调整大小
        gif1 = resize_gif('./emoji/gif1.gif', (50, 50))
        gif2 = resize_gif('./emoji/gif2.gif', (50, 50))
        gif3 = resize_gif('./emoji/gif3.gif', (50, 50))
        gif4 = resize_gif('./emoji/gif4.gif', (50, 50))
        
        # 获取第一帧作为按钮显示用
        gp1 = ImageTk.PhotoImage(gif1[0])
        gp2 = ImageTk.PhotoImage(gif2[0])
        gp3 = ImageTk.PhotoImage(gif3[0])
        gp4 = ImageTk.PhotoImage(gif4[0])
        
        # 存储完整的帧序列，用于动画显示
        gif_frames['gg1**'] = gif1
        gif_frames['gg2**'] = gif2
        gif_frames['gg3**'] = gif3
        gif_frames['gg4**'] = gif4
        
        # 用字典将标记与GIF动图一一对应（仅用于按钮显示，实际动画使用gif_frames）
        gdic = {'gg1**': gp1, 'gg2**': gp2, 'gg3**': gp3, 'gg4**': gp4}
    except Exception as e:
        print(f"Error loading emoji images: {e}")
        # 创建空图片以避免错误
        p1 = tkinter.PhotoImage(width=1, height=1)
        p2 = tkinter.PhotoImage(width=1, height=1)
        p3 = tkinter.PhotoImage(width=1, height=1)
        p4 = tkinter.PhotoImage(width=1, height=1)
        dic = {'aa**': p1, 'bb**': p2, 'cc**': p3, 'dd**': p4}
        
        # 同样为GIF创建空图片
        gp1 = tkinter.PhotoImage(width=1, height=1)
        gp2 = tkinter.PhotoImage(width=1, height=1)
        gp3 = tkinter.PhotoImage(width=1, height=1)
        gp4 = tkinter.PhotoImage(width=1, height=1)
        gdic = {'gg1**': gp1, 'gg2**': gp2, 'gg3**': gp3, 'gg4**': gp4}
        gif_frames = {'gg1**': [], 'gg2**': [], 'gg3**': [], 'gg4**': []}

    ee = 0  # 判断表情面板开关的标志
    ge = 0  # 判断GIF面板开关的标志
    
    # 创建表情按钮
    eBut = tkinter.Button(root, text='emoji', command=express)
    eBut.place(x=5, y=320, width=60, height=30)
    
    # 创建GIF表情按钮
    gBut = tkinter.Button(root, text='GIF', command=gif_express)
    gBut.place(x=305, y=320, width=60, height=30)
    
    # 创建发送图片按钮
    pBut = tkinter.Button(root, text='Image', command=picture)
    pBut.place(x=65, y=320, width=60, height=30)
    
    # 创建截屏按钮
    sBut = tkinter.Button(root, text='Capture', command=buttonCaptureClick)
    sBut.place(x=125, y=320, width=60, height=30)
    
    # 创建文件按钮
    fBut = tkinter.Button(root, text='File', command=fileClient)
    fBut.place(x=185, y=320, width=60, height=30)
    
    # 创建多行文本框, 显示在线用户
    listbox1 = tkinter.Listbox(root)
    listbox1.place(x=445, y=0, width=130, height=320)
    
    # 查看在线用户按钮
    ii = 0
    button1 = tkinter.Button(root, text='Users online', command=users)
    button1.place(x=485, y=320, width=90, height=30)
    
    # 创建输入文本框和关联变量
    a = tkinter.StringVar()
    a.set('')
    entry = tkinter.Entry(root, width=120, textvariable=a)
    entry.place(x=5, y=350, width=570, height=40)
    
    # 创建发送按钮
    button = tkinter.Button(root, text='Send', command=send)
    button.place(x=515, y=353, width=60, height=30)
    root.bind('<Return>', send)  # 绑定回车发送信息
    
    # 视频聊天按钮
    vbutton = tkinter.Button(root, text="Video", command=video_connect_option)
    vbutton.place(x=245, y=320, width=60, height=30)
    
    # 在显示用户列表框上设置绑定事件
    listbox1.bind('<ButtonRelease-1>', private)

# 表情功能代码部分
# 四个按钮, 使用全局变量, 方便创建和销毁
b1 = ''
b2 = ''
b3 = ''
b4 = ''
# 将图片打开存入变量中
p1 = None
p2 = None
p3 = None
p4 = None
# 用字典将标记与表情图片一一对应, 用于后面接收标记判断表情贴图
dic = {}
ee = 0  # 判断表情面板开关的标志

# GIF表情功能代码部分
# 四个按钮, 使用全局变量, 方便创建和销毁
g1 = ''
g2 = ''
g3 = ''
g4 = ''
# 将GIF图片打开存入变量中
gp1 = None
gp2 = None
gp3 = None
gp4 = None
# 用字典将标记与GIF表情图片一一对应
gdic = {}
ge = 0  # 判断GIF表情面板开关的标志

# 发送表情图标记的函数, 在按钮点击事件中调用
def mark(exp):  # 参数是发的表情图标记, 发送后将按钮销毁
    global ee
    mes = exp + ':;' + user + ':;' + chat
    s.send(mes.encode())
    b1.destroy()
    b2.destroy()
    b3.destroy()
    b4.destroy()
    ee = 0

# GIF表情发送函数
def gmark(exp):  # 参数是发的GIF表情图标记, 发送后将按钮销毁
    global ge
    mes = exp + ':;' + user + ':;' + chat
    s.send(mes.encode())
    g1.destroy()
    g2.destroy()
    g3.destroy()
    g4.destroy()
    ge = 0

# 四个对应的GIF按钮函数
def gg1():
    gmark('gg1**')

def gg2():
    gmark('gg2**')

def gg3():
    gmark('gg3**')

def gg4():
    gmark('gg4**')

# 四个对应的函数
def bb1():
    mark('aa**')

def bb2():
    mark('bb**')

def bb3():
    mark('cc**')

def bb4():
    mark('dd**')

def express():
    global b1, b2, b3, b4, ee, g1, g2, g3, g4, ge
    # 如果GIF面板是打开的，先关闭它
    if ge == 1:
        ge = 0
        g1.destroy()
        g2.destroy()
        g3.destroy()
        g4.destroy()
    
    if ee == 0:
        ee = 1
        b1 = tkinter.Button(root, command=bb1, image=p1,
                            relief=tkinter.FLAT, bd=0)
        b2 = tkinter.Button(root, command=bb2, image=p2,
                            relief=tkinter.FLAT, bd=0)
        b3 = tkinter.Button(root, command=bb3, image=p3,
                            relief=tkinter.FLAT, bd=0)
        b4 = tkinter.Button(root, command=bb4, image=p4,
                            relief=tkinter.FLAT, bd=0)

        b1.place(x=5, y=248)
        b2.place(x=75, y=248)
        b3.place(x=145, y=248)
        b4.place(x=215, y=248)
    else:
        ee = 0
        b1.destroy()
        b2.destroy()
        b3.destroy()
        b4.destroy()

def gif_express():
    global g1, g2, g3, g4, ge, b1, b2, b3, b4, ee
    # 如果普通表情面板是打开的，先关闭它
    if ee == 1:
        ee = 0
        b1.destroy()
        b2.destroy()
        b3.destroy()
        b4.destroy()
    
    if ge == 0:
        ge = 1
        g1 = tkinter.Button(root, command=gg1, image=gp1,
                            relief=tkinter.FLAT, bd=0)
        g2 = tkinter.Button(root, command=gg2, image=gp2,
                            relief=tkinter.FLAT, bd=0)
        g3 = tkinter.Button(root, command=gg3, image=gp3,
                            relief=tkinter.FLAT, bd=0)
        g4 = tkinter.Button(root, command=gg4, image=gp4,
                            relief=tkinter.FLAT, bd=0)

        g1.place(x=5, y=248)
        g2.place(x=75, y=248)
        g3.place(x=145, y=248)
        g4.place(x=215, y=248)
    else:
        ge = 0
        g1.destroy()
        g2.destroy()
        g3.destroy()
        g4.destroy()

# 图片功能代码部分
# 从图片服务端的缓存文件夹中下载图片到客户端缓存文件夹中
def fileGet(name):
    PORT3 = 50009
    ss2 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    ss2.connect((IP, PORT3))
    message = 'get ' + name
    ss2.send(message.encode())
    fileName = '.\\Client_image_cache\\' + name
    print('Start downloading image!')
    print('Waiting.......')
    with open(fileName, 'wb') as f:
        while True:
            data = ss2.recv(1024)
            if data == 'EOF'.encode():
                print('Download completed!')
                break
            f.write(data)
    time.sleep(0.1)
    ss2.send('quit'.encode())

# 将图片上传到图片服务端的缓存文件夹中
def filePut(fileName):
    PORT3 = 50009
    ss = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    ss.connect((IP, PORT3))
    # 截取文件名
    print(fileName)
    name = fileName.split('/')[-1]
    print(name)
    message = 'put ' + name
    ss.send(message.encode())
    time.sleep(0.1)
    print('Start uploading image!')
    print('Waiting.......')
    with open(fileName, 'rb') as f:
        while True:
            a = f.read(1024)
            if not a:
                break
            ss.send(a)
        time.sleep(0.1)  # 延时确保文件发送完整
        ss.send('EOF'.encode())
        print('Upload completed')
    ss.send('quit'.encode())
    time.sleep(0.1)
    # 上传成功后发一个信息给所有客户端
    mes = '``#' + name + ':;' + user + ':;' + chat
    s.send(mes.encode())

def picture():
    # 选择对话框
    fileName = tkinter.filedialog.askopenfilename(title='Select upload image')
    # 如果有选择文件才继续执行
    if fileName:
        # 调用发送图片函数
        filePut(fileName)

# 截屏函数如下所示
class MyCapture:
    def __init__(self, png):
        # 变量X和Y用来记录鼠标左键按下的位置
        self.X = tkinter.IntVar(value=0)
        self.Y = tkinter.IntVar(value=0)
        # 屏幕尺寸
        screenWidth = root.winfo_screenwidth()
        screenHeight = root.winfo_screenheight()
        # 创建顶级组件容器
        self.top = tkinter.Toplevel(root, width=screenWidth, height=screenHeight)
        # 不显示最大化、最小化按钮
        self.top.overrideredirect(True)
        self.canvas = tkinter.Canvas(self.top, bg='white', width=screenWidth, height=screenHeight)
        # 显示全屏截图，在全屏截图上进行区域截图
        self.image = tkinter.PhotoImage(file=png)
        self.canvas.create_image(screenWidth / 2, screenHeight / 2, image=self.image)
        self.sel = None

        # 鼠标左键按下的位置
        def onLeftButtonDown(event):
            self.X.set(event.x)
            self.Y.set(event.y)
            # 开始截图
            self.sel = True

        self.canvas.bind('<Button-1>', onLeftButtonDown)

        # 鼠标左键移动，显示选取的区域
        def onLeftButtonMove(event):
            if not self.sel:
                return
            global lastDraw
            try:
                # 删除刚画完的图形，要不然鼠标移动的时候是黑乎乎的一片矩形
                self.canvas.delete(lastDraw)
            except Exception as e:
                print(e)
            lastDraw = self.canvas.create_rectangle(self.X.get(), self.Y.get(), event.x, event.y, outline='black')

        self.canvas.bind('<B1-Motion>', onLeftButtonMove)

        # 获取鼠标左键抬起的位置，保存区域截图
        def onLeftButtonUp(event):
            self.sel = False
            try:
                self.canvas.delete(lastDraw)
            except Exception as e:
                print(e)
            sleep(0.1)
            # 考虑鼠标左键从右下方按下而从左上方抬起的截图
            left, right = sorted([self.X.get(), event.x])
            top, bottom = sorted([self.Y.get(), event.y])
            pic = ImageGrab.grab((left + 1, top + 1, right, bottom))
            # 弹出保存截图对话框
            fileName = tkinter.filedialog.asksaveasfilename(title='Save screenshot',
                                                            filetypes=[('image', '*.jpg *.png')])
            if fileName:
                pic.save(fileName)
            # 关闭当前窗口
            self.top.destroy()

        self.canvas.bind('<ButtonRelease-1>', onLeftButtonUp)
        # 让canvas充满窗口，并随窗口自动适应大小
        self.canvas.pack(fill=tkinter.BOTH, expand=tkinter.YES)

# 开始截图
def buttonCaptureClick():
    # 最小化主窗口
    root.state('icon')
    sleep(0.2)
    filename = 'temp.png'
    # grab()方法默认对全屏幕进行截图
    im = ImageGrab.grab()
    im.save(filename)
    im.close()
    # 显示全屏幕截图
    w = MyCapture(filename)
    sBut.wait_window(w.top)
    # 截图结束，恢复主窗口，并删除临时的全屏幕截图文件
    root.state('normal')
    os.remove(filename)

# 文件功能代码部分
# 将在文件功能窗口用到的组件名都列出来, 方便重新打开时会对面板进行更新
list2 = ''  # 列表框
label = ''  # 显示路径的标签
upload = ''  # 上传按钮
close = ''  # 关闭按钮

def fileClient():
    PORT2 = 50008  # 聊天室的端口为50007
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((IP, PORT2))

    # 修改root窗口大小显示文件管理的组件
    root['height'] = 390
    root['width'] = 760

    # 创建列表框
    list2 = tkinter.Listbox(root)
    list2.place(x=580, y=25, width=175, height=325)

    # 将接收到的目录文件列表打印出来(dir), 显示在列表框中, 在pwd函数中调用
    def recvList(enter, lu):
        try:
            s.settimeout(5.0)  # 设置5秒超时
            s.send(enter.encode())
            data = s.recv(4096)
            data = json.loads(data.decode())
            list2.delete(0, tkinter.END)  # 清空列表框
            lu = lu.split('\\')
            if len(lu) != 1:
                list2.insert(tkinter.END, 'Return to the previous dir')
                list2.itemconfig(0, fg='green')
            for i in range(len(data)):
                list2.insert(tkinter.END, ('' + data[i]))
                if '.' not in data[i]:
                    list2.itemconfig(tkinter.END, fg='orange')
                else:
                    list2.itemconfig(tkinter.END, fg='blue')
        except Exception as e:
            print(f"Error in recvList: {e}")
            list2.delete(0, tkinter.END)
            list2.insert(tkinter.END, "Error loading directory")
        finally:
            s.settimeout(None)  # 恢复默认设置

    # 创建标签显示服务端工作目录
    def lab():
        global label
        try:
            s.settimeout(5.0)  # 设置5秒超时
            data = s.recv(1024)  # 接收目录
            lu = data.decode()
            try:
                label.destroy()
                label = tkinter.Label(root, text=lu)
                label.place(x=580, y=0, )
            except:
                label = tkinter.Label(root, text=lu)
                label.place(x=580, y=0, )
            recvList('dir', lu)
        except socket.timeout:
            print("Timeout waiting for directory information")
            try:
                label.destroy()
                label = tkinter.Label(root, text="Connection timeout")
                label.place(x=580, y=0, )
            except:
                label = tkinter.Label(root, text="Connection timeout")
                label.place(x=580, y=0, )
        except Exception as e:
            print(f"Error in lab: {e}")
        finally:
            s.settimeout(None)  # 恢复默认设置

    # 进入指定目录(cd)
    def cd(message):
        s.send(message.encode())

    # 刚连接上服务端时进行一次面板刷新
    cd('cd same')
    lab()

    # 接收下载文件(get)
    def get(message):
        # print(message)
        name = message.split(' ')
        # print(name)
        name = name[1]  # 获取命令的第二个参数(文件名)
        # 选择对话框, 选择文件的保存路径
        fileName = tkinter.filedialog.asksaveasfilename(title='Save file to', initialfile=name)
        # 如果文件名非空才进行下载
        if fileName:
            # 创建进度窗口
            progress_window = tkinter.Toplevel(root)
            progress_window.title('Downloading')
            progress_window.geometry('300x100')
            
            # 添加进度标签
            progress_label = tkinter.Label(progress_window, text=f"Downloading {name}...")
            progress_label.pack(pady=10)
            
            # 添加取消按钮
            cancel_download = False
            
            def on_cancel():
                nonlocal cancel_download
                cancel_download = True
                progress_window.destroy()
                
            cancel_button = tkinter.Button(progress_window, text="Cancel", command=on_cancel)
            cancel_button.pack(pady=10)
            
            # 开始下载文件的线程
            def download_thread():
                try:
                    # 设置超时
                    s.settimeout(10.0)
                    s.send(message.encode())
                    
                    with open(fileName, 'wb') as f:
                        while True and not cancel_download:
                            try:
                                data = s.recv(1024)
                                if data == 'EOF'.encode():
                                    break
                                if not data:  # 连接中断
                                    raise Exception("Connection lost")
                                f.write(data)
                                # 更新进度标签
                                progress_window.update_idletasks()
                            except socket.timeout:
                                if not cancel_download:
                                    tkinter.messagebox.showerror(title='Error', 
                                                              message='Download timed out!')
                                break
                    
                    # 完成下载，关闭进度窗口
                    if not cancel_download:
                        progress_window.destroy()
                        tkinter.messagebox.showinfo(title='Message',
                                                  message='Download completed!')
                except Exception as e:
                    if not cancel_download:
                        progress_window.destroy()
                        tkinter.messagebox.showerror(title='Error',
                                                  message=f'Download failed: {str(e)}')
                finally:
                    s.settimeout(None)  # 恢复默认超时设置
                    
            # 启动下载线程
            download_thread = threading.Thread(target=download_thread)
            download_thread.daemon = True
            download_thread.start()
            
            # 等待进度窗口关闭
            root.wait_window(progress_window)

    # 创建用于绑定在列表框上的函数
    def run(*args):
        try:
            indexs = list2.curselection()
            index = indexs[0]
            content = list2.get(index)
            
            # 创建处理操作的线程函数
            def process_action():
                try:
                    # 如果有一个 . 则为文件
                    if '.' in content:
                        content_command = 'get ' + content
                        get(content_command)
                        cd('cd same')
                    elif content == 'Return to the previous dir':
                        content_command = 'cd ..'
                        cd(content_command)
                    else:
                        content_command = 'cd ' + content
                        cd(content_command)
                    lab()  # 刷新显示页面
                except Exception as e:
                    print(f"Error in process_action: {e}")
            
            # 使用线程执行可能阻塞的操作
            action_thread = threading.Thread(target=process_action)
            action_thread.daemon = True
            action_thread.start()
            
        except Exception as e:
            print(f"Error in run: {e}")
            # 可能没有选中项目等异常情况

    # 在列表框上设置绑定事件
    list2.bind('<ButtonRelease-1>', run)

    # 上传客户端所在文件夹中指定的文件到服务端, 在函数中获取文件名, 不用传参数
    def put():
        # 选择对话框
        fileName = tkinter.filedialog.askopenfilename(title='Select upload file')
        # 如果有选择文件才继续执行
        if fileName:
            name = fileName.split('/')[-1]
            message = 'put ' + name
            s.send(message.encode())
            with open(fileName, 'rb') as f:
                while True:
                    a = f.read(1024)
                    if not a:
                        break
                    s.send(a)
                time.sleep(0.1)  # 延时确保文件发送完整
                s.send('EOF'.encode())
                tkinter.messagebox.showinfo(title='Message',
                                            message='Upload completed!')
            
            # 使用线程来刷新文件列表，避免阻塞主线程
            def refresh_filelist():
                try:
                    # 设置超时，防止长时间阻塞
                    s.settimeout(5.0)
                    cd('cd same')
                    lab()  # 上传成功后刷新显示页面
                except Exception as e:
                    print(f"Error refreshing file list: {e}")
                finally:
                    # 恢复默认超时设置
                    s.settimeout(None)
                
            # 创建并启动线程
            refresh_thread = threading.Thread(target=refresh_filelist)
            refresh_thread.daemon = True  # 设为守护线程，随主线程退出
            refresh_thread.start()

    # 创建上传按钮, 并绑定上传文件功能
    upload = tkinter.Button(root, text='Upload file', command=put)
    upload.place(x=600, y=353, height=30, width=80)

    # 关闭文件管理器, 待完善
    def closeFile():
        root['height'] = 390
        root['width'] = 580
        # 关闭连接
        s.send('quit'.encode())
        s.close()

    # 创建关闭按钮
    close = tkinter.Button(root, text='Close', command=closeFile)
    close.place(x=685, y=353, height=30, width=70)

# 创建文件按钮
fBut = tkinter.Button(root, text='File', command=fileClient)
fBut.place(x=185, y=320, width=60, height=30)

# 创建多行文本框, 显示在线用户
listbox1 = tkinter.Listbox(root)
listbox1.place(x=445, y=0, width=130, height=320)

def users():
    global listbox1, ii
    if ii == 1:
        listbox1.place(x=445, y=0, width=130, height=320)
        ii = 0
    else:
        listbox1.place_forget()  # 隐藏控件
        ii = 1

# 查看在线用户按钮
button1 = tkinter.Button(root, text='Users online', command=users)
button1.place(x=485, y=320, width=90, height=30)

# 创建输入文本框和关联变量
a = tkinter.StringVar()
a.set('')
entry = tkinter.Entry(root, width=120, textvariable=a)
entry.place(x=5, y=350, width=570, height=40)

def call_robot(url, apikey, msg):
    data = {
        "reqType": 0,
        "perception": {
            # 用户输入文文信息
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
        "userInfo": {
            "apiKey": "ee19328107fa41e987a42a064a68d0da",  # 你注册的apikey,机器人标识,32位
            "userId": "Brandon"  # 随便填，用户的唯一标识，长度小于等于32位
        }
    }
    headers = {'content-type': 'application/json'}  # 必须是json
    r = requests.post(url, headers=headers, data=json.dumps(data))
    return r.json()

def send(*args):
    # 没有添加的话发送信息时会提示没有聊天对象
    users.append('------Group chat-------')
    users.append('Robot')
    print(chat)
    if chat not in users:
        tkinter.messagebox.showerror('Send error', message='There is nobody to talk to!')
        return
    if chat == 'Robot':
        print('Robot')
    if chat == user:
        tkinter.messagebox.showerror('Send error', message='Cannot talk with yourself in private!')
        return
    mes = entry.get() + ':;' + user + ':;' + chat  # 添加聊天对象标记
    s.send(mes.encode())
    a.set('')  # 发送后清空文本框

# 创建发送按钮
button = tkinter.Button(root, text='Send', command=send)
button.place(x=515, y=353, width=60, height=30)
root.bind('<Return>', send)  # 绑定回车发送信息

# 视频聊天部分
IsOpen = False    # 判断视频/音频的服务器是否已打开
Resolution = 0    # 图像传输的分辨率 0-4依次递减
Version = 4       # 传输协议版本 IPv4/IPv6
ShowMe = True     # 视频聊天时是否打开本地摄像头
AudioOpen = True  # 是否打开音频聊天

def video_invite():
    global IsOpen, Version, AudioOpen
    if Version == 4:
        host_name = socket.gethostbyname(socket.getfqdn(socket.gethostname()))
    else:
        host_name = [i['addr'] for i in ifaddresses(interfaces()[-2]).setdefault(AF_INET6, [{'addr': 'No IP addr'}])][
            -1]

    invite = 'INVITE' + host_name + ':;' + user + ':;' + chat
    s.send(invite.encode())
    if not IsOpen:
        vserver = vachat.Video_Server(10087, Version)
        if AudioOpen:
            aserver = vachat.Audio_Server(10088, Version)
            aserver.start()
        vserver.start()
        IsOpen = True

def video_accept(host_name):
    global IsOpen, Resolution, ShowMe, Version, AudioOpen

    vclient = vachat.Video_Client(host_name, 10087, ShowMe, Resolution, Version)
    if AudioOpen:
        aclient = vachat.Audio_Client(host_name, 10088, Version)
        aclient.start()
    vclient.start()
    IsOpen = False

def video_invite_window(message, inviter_name):
    invite_window = tkinter.Toplevel()
    invite_window.geometry('300x100')
    invite_window.title('Invitation')
    label1 = tkinter.Label(invite_window, bg='#f0f0f0', width=20, text=inviter_name)
    label1.pack()
    label2 = tkinter.Label(invite_window, bg='#f0f0f0', width=20, text='invites you to video chat!')
    label2.pack()

    def accept_invite():
        invite_window.destroy()
        video_accept(message[message.index('INVITE') + 6:])

    def refuse_invite():
        invite_window.destroy()

    Refuse = tkinter.Button(invite_window, text="Refuse", command=refuse_invite)
    Refuse.place(x=60, y=60, width=60, height=25)
    Accept = tkinter.Button(invite_window, text="Accept", command=accept_invite)
    Accept.place(x=180, y=60, width=60, height=25)

def video_connect_option():
    global Resolution, ShowMe, Version, AudioOpen

    video_connect_option = tkinter.Toplevel()
    video_connect_option.geometry('150x450')
    video_connect_option.title('Connection option')

    var1 = tkinter.StringVar()
    label1 = tkinter.Label(video_connect_option, bg='#f0f0f0', width=20, text='Resolution   ')
    label1.pack()

    def print_resolution():
        global Resolution
        Resolution = var1.get()
        label1.config(text='Resolution   ' + Resolution)

    r0 = tkinter.Radiobutton(video_connect_option, text='0', variable=var1, value='0', command=print_resolution)
    r0.pack()
    r1 = tkinter.Radiobutton(video_connect_option, text='1', variable=var1, value='1', command=print_resolution)
    r1.pack()
    r2 = tkinter.Radiobutton(video_connect_option, text='2', variable=var1, value='2', command=print_resolution)
    r2.pack()
    r3 = tkinter.Radiobutton(video_connect_option, text='3', variable=var1, value='3', command=print_resolution)
    r3.pack()
    r4 = tkinter.Radiobutton(video_connect_option, text='4', variable=var1, value='4', command=print_resolution)
    r4.pack()

    var2 = tkinter.StringVar()
    label2 = tkinter.Label(video_connect_option, bg='#f0f0f0', width=20, text='Protocol version   ')
    label2.pack()

    def print_version():
        global Version
        Version = var2.get()
        label2.config(text='Version   IPv' + Version)

    v0 = tkinter.Radiobutton(video_connect_option, text='IPv4', variable=var2, value='4', command=print_version)
    v0.pack()
    v1 = tkinter.Radiobutton(video_connect_option, text='IPv6', variable=var2, value='6', command=print_version)
    v1.pack()

    var3 = tkinter.StringVar()
    label3 = tkinter.Label(video_connect_option, bg='#f0f0f0', width=20, text='Show yourself   ')
    label3.pack()

    def print_show():
        global ShowMe
        if var3.get() == '1':
            ShowMe = True
            txt = 'Yes'
        else:
            ShowMe = False
            txt = 'No'
        label3.config(text='Show yourself   ' + txt)

    s0 = tkinter.Radiobutton(video_connect_option, text='Yes', variable=var3, value='1', command=print_show)
    s0.pack()
    s1 = tkinter.Radiobutton(video_connect_option, text='No', variable=var3, value='0', command=print_show)
    s1.pack()

    var4 = tkinter.StringVar()
    label4 = tkinter.Label(video_connect_option, bg='#f0f0f0', width=20, text='Audio open   ')
    label4.pack()

    def print_audio():
        global AudioOpen
        if var4.get() == '1':
            AudioOpen = True
            txt = 'Yes'
        else:
            AudioOpen = False
            txt = 'No'
        label4.config(text='Audio open   ' + txt)

    a0 = tkinter.Radiobutton(video_connect_option, text='Yes', variable=var4, value='1', command=print_audio)
    a0.pack()
    a1 = tkinter.Radiobutton(video_connect_option, text='No', variable=var4, value='0', command=print_audio)
    a1.pack()

    def option_enter():
        video_connect_option.destroy()

    Enter = tkinter.Button(video_connect_option, text="Enter", command=option_enter)
    Enter.place(x=10, y=400, width=60, height=35)
    Start = tkinter.Button(video_connect_option, text="Start", command=video_invite)
    Start.place(x=80, y=400, width=60, height=35)

# 私聊功能
def private(*args):
    global chat
    # 获取点击的索引然后得到内容(用户名)
    indexs = listbox1.curselection()
    index = indexs[0]
    if index > 0:
        chat = listbox1.get(index)
        # 修改客户端名称
        if chat == '------Group chat-------':
            root.title(user)
            return
        ti = user + '  -->  ' + chat
        root.title(ti)

# 在显示用户列表框上设置绑定事件
listbox1.bind('<ButtonRelease-1>', private)

# 用于时刻接收服务端发送的信息并打印
def recv():
    global users, gif_frames, gif_labels, last_gif_id
    while True:
        data = s.recv(1024)
        data = data.decode()
        # 没有捕获到异常则表示接收到的是在线用户列表
        try:
            data = json.loads(data)
            users = data
            listbox1.delete(0, tkinter.END)  # 清空列表框
            number = ('   Users online: ' + str(len(data)))
            listbox1.insert(tkinter.END, number)
            listbox1.itemconfig(tkinter.END, fg='green', bg="#f0f0ff")
            listbox1.insert(tkinter.END, '------Group chat-------')
            listbox1.insert(tkinter.END, 'Robot')
            listbox1.itemconfig(tkinter.END, fg='green')
            for i in range(len(data)):
                listbox1.insert(tkinter.END, (data[i]))
                listbox1.itemconfig(tkinter.END, fg='green')
        except:
            data = data.split(':;')
            data1 = data[0].strip()  # 消息
            data2 = data[1]  # 发送信息的用户名
            data3 = data[2]  # 聊天对象
            if 'INVITE' in data1:
                if data3 == 'Robot':
                    tkinter.messagebox.showerror('Connect error', message='Unable to make video chat with robot!')
                elif data3 == '------Group chat-------':
                    tkinter.messagebox.showerror('Connect error', message='Group video chat is not supported!')
                elif (data2 == user and data3 == user) or (data2 != user):
                    video_invite_window(data1, data2)
                continue
            markk = data1.split('：')[1]
            # 判断是不是图片
            pic = markk.split('#')
            # 判断是不是表情
            # 如果字典里有则贴图
            if (markk in dic) or (markk in gdic) or pic[0] == '``':
                data4 = '\n' + data2 + '：'  # 例:名字-> \n名字：
                if data3 == '------Group chat-------':
                    if data2 == user:  # 如果是自己则将则字体变为蓝色
                        listbox.insert(tkinter.END, data4, 'blue')
                    else:
                        listbox.insert(tkinter.END, data4, 'green')  # END将信息加在最后一行
                elif data2 == user or data3 == user:  # 显示私聊
                    listbox.insert(tkinter.END, data4, 'red')  # END将信息加在最后一行
                if pic[0] == '``':
                    # 从服务端下载发送的图片
                    fileGet(pic[1])
                elif markk in dic:
                    # 将表情图贴到聊天框
                    listbox.image_create(tkinter.END, image=dic[markk])
                elif markk in gdic:
                    # 创建动画GIF并显示
                    gif_label = create_animated_gif(markk, (0, 0))
                    if gif_label:
                        listbox.window_create(tkinter.END, window=gif_label)
            else:
                data1 = '\n' + data1
                if data3 == '------Group chat-------':
                    if data2 == user:  # 如果是自己则将则字体变为蓝色
                        listbox.insert(tkinter.END, data1, 'blue')
                    else:
                        listbox.insert(tkinter.END, data1, 'green')  # END将信息加在最后一行
                    if len(data) == 4:
                        listbox.insert(tkinter.END, '\n' + data[3], 'pink')
                elif data3 == 'Robot' and data2 == user:
                    print('Here:Robot')
                    apikey = 'ee19328107fa41e987a42a064a68d0da'
                    url = 'http://openapi.tuling123.com/openapi/api/v2'
                    print('msg = ', data1)
                    listbox.insert(tkinter.END, data1, 'blue')
                    reply = call_robot(url, apikey, data1.split('：')[1])
                    reply_txt = '\nRobot:' + reply['results'][0]['values']['text']
                    listbox.insert(tkinter.END, reply_txt, 'pink')
                elif data2 == user or data3 == user:  # 显示私聊
                    listbox.insert(tkinter.END, data1, 'red')  # END将信息加在最后一行
            listbox.see(tkinter.END)  # 显示在最后

# 调整GIF大小的函数
def resize_gif(path, size):
    """
    调整GIF大小，返回所有调整大小后的帧
    :param path: GIF文件路径
    :param size: 目标尺寸 (width, height)
    :return: 调整后的帧列表
    """
    frames = []
    try:
        img = Image.open(path)
        # 遍历GIF的所有帧
        for frame in ImageSequence.Iterator(img):
            # 复制帧以便修改
            frame_copy = frame.copy()
            # 调整帧大小
            frame_copy = frame_copy.resize(size, Image.LANCZOS)
            frames.append(frame_copy)
    except Exception as e:
        print(f"Error resizing GIF {path}: {e}")
    return frames

# 创建动画GIF的函数
def create_animated_gif(gif_key, position):
    """
    创建一个动画GIF并在指定位置显示
    :param gif_key: GIF在gif_frames字典中的键
    :param position: 显示位置 (x, y)
    """
    global listbox, gif_labels, last_gif_id, gif_frames
    
    if gif_key not in gif_frames or not gif_frames[gif_key]:
        return None
    
    # 生成唯一ID给这个GIF实例
    gif_id = f"gif_{last_gif_id}"
    last_gif_id += 1
    
    # 创建标签显示GIF
    label = tkinter.Label(listbox)
    gif_labels[gif_id] = {
        'label': label,
        'frames': gif_frames[gif_key],
        'current_frame': 0,
        'is_playing': True
    }
    
    # 返回标签引用以便插入到文本框
    return label

# 更新GIF动画的函数
def update_gifs():
    """定期更新所有GIF动画的帧"""
    global gif_labels
    
    for gif_id, gif_data in list(gif_labels.items()):
        if gif_data['is_playing']:
            # 获取下一帧
            frames = gif_data['frames']
            current_frame = gif_data['current_frame']
            
            if frames:  # 确保有帧可以显示
                # 更新到下一帧
                next_frame = (current_frame + 1) % len(frames)
                gif_data['current_frame'] = next_frame
                
                # 显示新帧
                try:
                    frame_image = ImageTk.PhotoImage(frames[next_frame])
                    gif_data['current_image'] = frame_image  # 保存引用防止垃圾回收
                    gif_data['label'].config(image=frame_image)
                except Exception as e:
                    print(f"Error updating GIF frame: {e}")
    
    # 每100毫秒更新一次
    root.after(100, update_gifs)

# 将Enter键绑定到登录功能
root.bind('<Return>', process_login_register)  # 回车绑定登录功能
loginButton = tkinter.Button(root, text='Login', command=process_login_register)
loginButton.place(x=115, y=150, width=70, height=30)

# 主循环
root.mainloop()

# 程序结束时关闭socket连接
if 's' in globals():
    s.close()