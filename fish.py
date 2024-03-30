from http.server import BaseHTTPRequestHandler, HTTPServer
import os
import subprocess
from PIL import ImageGrab
import json
import win32api, win32con, win32gui
import urllib.parse

# 定义一些操作
def shutdown():
    os.system('shutdown /s /t 1')

def restart():
    os.system('shutdown /r /t 1')

def run_cmd(command):
    output = subprocess.check_output(command, shell=True)
    return output.decode('utf-8')

def capture_desktop():
    # 使用Pillow截图
    image = ImageGrab.grab()
    image_path = "desktop.png"
    image.save(image_path)
    return image_path

def send_message(title, message):
    win32api.MessageBox(0, message, title)

# HTTP请求处理类
class MyServer(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/shutdown':
            shutdown()
            self.send_response(200)
            self.send_header('Content-type', 'text/html; charset=utf-8')
            self.end_headers()
            self.wfile.write(b'Shutdown initiated.')
        elif self.path == '/restart':
            restart()
            self.send_response(200)
            self.send_header('Content-type', 'text/html; charset=utf-8')
            self.end_headers()
            self.wfile.write(b'Restart initiated.')
        elif self.path.startswith('/cmd?'):
            query = self.path.split('?')[1]
            command = urllib.parse.unquote(query.split('=')[1])
            output = run_cmd(command)
            self.send_response(200)
            self.send_header('Content-type', 'text/html; charset=utf-8')
            self.end_headers()
            self.wfile.write(output.encode('utf-8'))
        elif self.path == '/desktop':
            # capture_desktop() 的结果应是一个图像文件的路径
            image_path = capture_desktop()
            with open(image_path, 'rb') as f:
                self.send_response(200)
                self.send_header('Content-type', 'image/png')
                self.end_headers()
                self.wfile.write(f.read())
        elif self.path.startswith('/message?'):
            query = self.path.split('?')[1]
            title, message = query.split('&')
            title = urllib.parse.unquote(title.split('=')[1])
            message = urllib.parse.unquote(message.split('=')[1])
            send_message(title, message)
            self.send_response(200)
            self.send_header('Content-type', 'text/html; charset=utf-8')
            self.end_headers()
            self.wfile.write(b'Message sent.')
        else:
            self.send_response(200)
            self.send_header('Content-type', 'text/html; charset=utf-8')
            self.end_headers()
            # 嵌入HTML，并指定UTF-8编码
            html = '''
            <!DOCTYPE html>
            <html>
            <head>
            <meta charset="UTF-8">
            </head>
            <body>
            <h1>Fish鲫鱼操作面板</h1>
            <p>鲫鱼v1.0.3</p>
            <a href="//hiluoli.cn/fish">鲫鱼</a>
            <p> </p>
            <button onclick="shutdown()">关机</button>
            <button onclick="restart()">重启</button>
            <button onclick="runCmd()">运行命令</button>
            <button onclick="viewDesktop()">查看桌面</button>
            <button onclick="sendMessage()">发送消息</button>
            <script>
            function shutdown() {
                fetch('/shutdown').then(response => response.text()).then(text => console.log(text));
            }
            function restart() {
                fetch('/restart').then(response => response.text()).then(text => console.log(text));
            }
            function runCmd() {
                let command = prompt("输入命令:");
                fetch('/cmd?command=' + encodeURIComponent(command)).then(response => response.text()).then(text => alert(text));
            }
            function viewDesktop() {
                window.open('/desktop');
            }
            function sendMessage() {
                let title = prompt("输入消息标题:");
                let message = prompt("输入消息内容:");
                fetch('/message?title=' + encodeURIComponent(title) + '&message=' + encodeURIComponent(message)).then(response => response.text()).then(text => console.log(text));
            }
            </script>
            </body>
            </html>
            '''
            self.wfile.write(html.encode('utf-8'))

# 主函数
def run():
    print('启动服务器...')

    # 服务器设置
    server_address = ('0.0.0.0', 8511)
    httpd = HTTPServer(server_address, MyServer)
    print('服务器正在运行...')
    print('端口:8511')
    httpd.serve_forever()

if __name__ == '__main__':
    run()
