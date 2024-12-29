from flask import Flask, render_template, request
from flask_socketio import SocketIO, emit
import random
import string

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app)

users = {}

@app.route('/')
def index():
    return render_template('index.html')

@socketio.on('connect')
def handle_connect():
    """
        处理新用户连接
        为新连接的用户生成随机用户名并保存到users字典中
        向所有客户端广播更新后的用户列表
    """
    users[request.sid] = generate_username()
    emit('user_list', {'users': list(users.values())}, broadcast=True)

@socketio.on('disconnect')
def handle_disconnect():
    """
        处理用户断开连接
        从users字典中删除对应的用户
        向所有客户端广播更新后的用户列表
    """
    if request.sid in users:
        del users[request.sid]
        emit('user_list', {'users': list(users.values())}, broadcast=True)

@socketio.on('message')
def handle_message(data):
    """
        处理聊天消息
        将消息广播给所有连接的客户端
    """
    emit('message', {
        'username': users[request.sid],
        'content': data['content'],
        'sender_id': request.sid    # 用于渲染时判断是否为自己发送的消息，从而渲染不同的样式
    }, broadcast=True, include_self=True)

@socketio.on('get_username')
def handle_get_username():
    """
        处理获取用户名请求
        向客户端发送当前用户的用户名
    """
    emit('username', {'username': users[request.sid]})

def generate_username():
    """
        生成随机用户名 
        返回格式为"用户_随机字符串"
    """
    return '用户_' + ''.join(random.choices(string.ascii_letters + string.digits, k=5))

if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=5001, debug=True)