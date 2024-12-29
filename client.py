# import socket
# import json
# import threading
# import tkinter as tk
# from tkinter import ttk, messagebox

# class ChatClient:
#     def __init__(self, host='localhost', port=5000):
#         self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
#         self.socket.connect((host, port))
        
#         self.setup_gui()
#         self.start_receiving()
    
#     def setup_gui(self):
#         """设置图形界面"""
#         self.root = tk.Tk()
#         self.root.title("局域网聊天")
        
#         # 用户列表
#         self.users_frame = ttk.Frame(self.root)
#         self.users_frame.pack(side=tk.LEFT, fill=tk.Y)
        
#         ttk.Label(self.users_frame, text="在线用户").pack()
#         self.users_listbox = tk.Listbox(self.users_frame, width=20)
#         self.users_listbox.pack(fill=tk.Y)
        
#         # 聊天区域
#         self.chat_frame = ttk.Frame(self.root)
#         self.chat_frame.pack(expand=True, fill=tk.BOTH)
        
#         self.chat_text = tk.Text(self.chat_frame, state='disabled')
#         self.chat_text.pack(expand=True, fill=tk.BOTH)
        
#         # 输入区域
#         self.input_frame = ttk.Frame(self.root)
#         self.input_frame.pack(fill=tk.X)
        
#         self.input_entry = ttk.Entry(self.input_frame)
#         self.input_entry.pack(side=tk.LEFT, expand=True, fill=tk.X)
#         self.input_entry.bind('<Return>', self.send_message)
        
#         ttk.Button(self.input_frame, text="发送", command=self.send_message).pack(side=tk.RIGHT)
#         ttk.Button(self.input_frame, text="修改用户名", command=self.change_username).pack(side=tk.RIGHT)
    
#     def send_message(self, event=None):
#         """发送消息"""
#         message = self.input_entry.get()
#         if message:
#             self.socket.send(json.dumps({
#                 'type': 'chat',
#                 'content': message
#             }).encode())
#             self.input_entry.delete(0, tk.END)
    
#     def change_username(self):
#         """修改用户名"""
#         new_username = tk.simpledialog.askstring("修改用户名", "请输入新的用户名：")
#         if new_username:
#             self.socket.send(json.dumps({
#                 'type': 'username_change',
#                 'new_username': new_username
#             }).encode())
    
#     def receive_messages(self):
#         """接收服务器消息"""
#         while True:
#             try:
#                 message = json.loads(self.socket.recv(1024).decode())
                
#                 if message['type'] == 'chat':
#                     self.chat_text.configure(state='normal')
#                     self.chat_text.insert(tk.END, f"{message['username']}: {message['content']}\n")
#                     self.chat_text.configure(state='disabled')
#                     self.chat_text.see(tk.END)
                
#                 elif message['type'] == 'user_list':
#                     self.users_listbox.delete(0, tk.END)
#                     for user in message['users']:
#                         self.users_listbox.insert(tk.END, user)
#             except:
#                 messagebox.showerror("错误", "与服务器断开连接")
#                 self.root.quit()
#                 break
    
#     def start_receiving(self):
#         """启动接收消息的线程"""
#         thread = threading.Thread(target=self.receive_messages)
#         thread.daemon = True
#         thread.start()
    
#     def run(self):
#         self.root.mainloop()

# if __name__ == '__main__':
#     client = ChatClient()
#     client.run() 