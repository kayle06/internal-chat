from flask import Flask, render_template, request, send_from_directory
from flask_socketio import SocketIO, emit
import random
import string
import os
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
app.config['UPLOAD_FOLDER'] = 'uploads'  # 创建上传文件夹
app.config['MAX_CONTENT_LENGTH'] = 100 * 1024 * 1024  # 100MB

# 确保上传文件夹存在
if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])

# 允许的文件类型
ALLOWED_EXTENSIONS = {
    # 图片
    'png', 'jpg', 'jpeg', 'gif', 
    # 音频
    'mp3', 'wav', 
    # 文档
    'pdf', 'doc', 'docx', 'txt',
    # 压缩包
    'zip', 'rar', '7z', 'tar', 'gz',
    # 安装包
    'apk', 'exe', 'dmg', 'pkg'
}

socketio = SocketIO(app)
users = {}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

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

@socketio.on('username_change')
def handle_username_change(data):
    """
        处理用户名修改请求
        检查新用户名是否已存在
        如果不存在则更新，并广播新的用户列表
        如果存在则返回错误消息
    """
    new_username = data['new_username']
    if new_username in users.values():
        emit('username_change_response', {'success': False, 'message': '用户名已存在'})
        return
    
    users[request.sid] = new_username
    emit('username_change_response', {'success': True, 'message': '用户名修改成功', 'newUsername': new_username})
    emit('user_list', {'users': list(users.values())}, broadcast=True)

def generate_username():
    """
        生成随机用户名 
        返回格式为"用户_随机字符串"
    """
    return '用户_' + ''.join(random.choices(string.ascii_letters + string.digits, k=5))

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return {'success': False, 'message': '没有文件'}, 400
    
    file = request.files['file']
    if file.filename == '':
        return {'success': False, 'message': '没有选择文件'}, 400
    
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        random_prefix = ''.join(random.choices(string.ascii_letters + string.digits, k=8))
        filename = f"{random_prefix}_{filename}"
        
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        
        # 获取文件类型并进行分类
        file_ext = filename.rsplit('.', 1)[1].lower()
        if file_ext in {'png', 'jpg', 'jpeg', 'gif'}:
            file_type = 'image'
        elif file_ext in {'zip', 'rar', '7z', 'tar', 'gz'}:
            file_type = 'archive'
        elif file_ext in {'mp3', 'wav'}:
            file_type = 'audio'
        elif file_ext in {'pdf', 'doc', 'docx', 'txt'}:
            file_type = 'document'
        elif file_ext in {'apk', 'exe', 'dmg', 'pkg'}:
            file_type = 'application'
        else:
            file_type = 'file'
        
        username = request.form.get('username', '未知用户')
        
        socketio.emit('message', {
            'username': username,
            'content': filename,
            'type': file_type,
            'original_name': file.filename  # 添加原始文件名
        })
        
        return {'success': True, 'filename': filename}, 200
    
    return {'success': False, 'message': '不支持的文件类型'}, 400

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=5001, debug=True)