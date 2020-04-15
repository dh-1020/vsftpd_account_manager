from django.shortcuts import render, HttpResponse
from django.conf import settings
from os import path, listdir
from json import dumps, loads
from .ftp import Ftp
import subprocess


# Create your views here.
class Page:
    def __init__(self):
        self.ftp = Ftp()
        self.context = {}
        self.modify_user = ''
        self.modify_homedir = ''


    def index(self, request):
        if request.user.is_authenticated:
            result = subprocess.Popen("ps -ef|grep vsftpd|grep -v grep", shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            stdout, errout = result.communicate()
            if stdout:
                result = "vsftpd service running"
            else:
                self.context['error_info'] = "vsftpd 服务未启动" 
                return render(request, "html/error.html", self.context)

            self.context['status'] = result
            return render(request, "html/index.html", self.context)
        else:
            self.context['error_info'] = "您还没有登录！！！"
            return render(request, "html/error_admin.html", self.context)


    def register(self, request):
        # POST request
        if request.method == "POST":
            # 获取前端提交参数
            username = request.POST.get('user')
            password = request.POST.get('password')
            confirm_password = request.POST.get('confirm_password')
            homedir = request.POST.get('homedir')
            can_upload = request.POST.get('can_upload')
            can_download = request.POST.get('can_download')
            can_createdir = request.POST.get('can_createdir')
            can_deletion = request.POST.get('can_deletion')
      
            # 用户密码以及确认密码是否为空
            if not username or not password or not confirm_password:
                self.context['error_info'] = "用户或密码不能为空" 
                return render(request, "html/error.html", self.context)

            if not username[0].isalpha():
                self.context['error_info'] = "用户名请以字母开头"
                return render(request, "html/error.html", self.context)

            if len(username) > 30 or len(password) > 30:
                self.context['error_info'] = "您输入的用户或密码太长了,请最多输入30位"
                return render(request, "html/error.html", self.context)

            if len(password) < 6:
                self.context['error_info'] = "您输入的密码太短了,请最少输入6位"
                return render(request, "html/error.html", self.context)
    
            # 家目录是否为空、是否以"/"开头、是否以"FTP_DIR"开头
            if not homedir:
                self.context['error_info'] = "用户家目录不能为空"
                return render(request, "html/error.html", self.context)
            else:
                if not homedir.startswith('/'):
                    homedir = settings.FTP_DIR + '/' + homedir
                else:
                    if not homedir.startswith(settings.FTP_DIR):
                        self.context['error_info'] = "您无权访问%s目录" % homedir
                        return render(request, "html/error.html", self.context)
                        
    
            # 密码和确认密码是否相同
            if password == confirm_password:
                users = self.ftp.getuser()
                if username in users:
                    self.context['error_info'] = "用户已存在"
                    return render(request, "html/error.html", self.context)
                else:
                    # 创建用户、家目录
                    self.ftp.create_user(username, password, homedir) 
                    # 写入用户配置文件
                    self.ftp.write_config(username, homedir, can_upload, can_download, can_createdir, can_deletion)
                    # 返回创建成功信息
                    self.context['username'] = username
                    self.context['homedir'] = homedir
                    self.context['can_upload'] = can_upload
                    self.context['can_download'] = can_download
                    self.context['can_createdir'] = can_createdir
                    self.context['can_deletion'] = can_deletion
                    self.ftp.write_db(self.context)
                    return render(request, "html/c_table.html", self.context)
            else:
                self.context['error_info'] = "两次密码输入不一致"
                return render(request, "html/error.html", self.context)
        else:
            if request.user.is_authenticated:
                self.context['home'] = settings.FTP_DIR
                self.context['ck'] = "checked"
                return render(request, "html/register.html", self.context)
            else:
                self.context['error_info'] = "您还没有登录！！！"
                return render(request, "html/error_admin.html", self.context)

    

    def delete(self, request):
        if request.method == "POST": 
            users = request.POST.getlist('delete_user')
            if not users:
                self.context['error_info'] = "不允许提交空值"
                return render(request, "html/error.html", self.context)

            self.ftp.delete(users)
            self.context['username'] = users
            return render(request, "html/d_table.html", self.context)
        else:
            if request.user.is_authenticated:
                self.context['Users'] = self.ftp.getuser()
                return render(request, "html/delete.html", self.context)
            else:
                self.context['error_info'] = "您还没有登录！！！"
                return render(request, "html/error_admin.html", self.context)



    def select(self, request):
        # self.context = self.ftp.alluser_context()
   
        if request.method == "POST":
            users = request.POST.getlist('select_user')
            user_l = []
            for user in users:
                user_l.append(user)
  
            if len(user_l) != 1:
                self.context['error_info'] = "一次只能查看一个用户"
                return render(request, "html/error.html", self.context)
          
            self.context = self.ftp.userinfo_context(users[0])
            return render(request, "html/s_table.html", self.context) 
        else:
            if request.user.is_authenticated:
                self.context['info'] = "一次只能查看一个用户"
                self.context['alluser'] =  self.ftp.getuser()
                return render(request, "html/select.html", self.context)
            else:
                self.context['error_info'] = "您还没有登录！！！"
                return render(request, "html/error_admin.html", self.context)



    def choise(self, request):
        if request.method == "POST":
            user = request.POST.get('modify_user')
            self.context = self.ftp.userinfo_context(user)

            for key, value in self.context.items():
                if value == "YES":
                    self.context[key] = 'checked'

            self.modify_user = user
            self.modify_homedir = self.context['homedir']

            with open('/root/1.txt', 'w') as f:
                f.write(dumps(self.context['homedir']))
            
            return render(request, "html/modify.html", self.context)
        else:
            if request.user.is_authenticated:
                self.context['Users'] = self.ftp.getuser()
                return render(request, "html/choise.html", self.context)
            else:
                self.context['error_info'] = "您还没有登录！！!"
                return render(request, "html/error_admin.html", self.context)

 
    def modify(self, request):
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')
        homedir = request.POST.get('homedir')
        can_upload = request.POST.get('can_upload')
        can_download = request.POST.get('can_download')
        can_createdir = request.POST.get('can_createdir')
        can_deletion = request.POST.get('can_deletion')


        if request.method == "POST":
            if not password or not confirm_password:
                password = None
                confirm_password = None
            else:
                if len(password) > 30:
                    self.context['error_info'] = "您输入的密码太长了,请最多输入30位"
                    return render(request, "html/error.html", self.context)

                if len(password) < 6:
                    self.context['error_info'] = "您输入的密码太短了,请最少输入6位"
                    return render(request, "html/error.html", self.context)

           # 家目录是否以"/"开头、是否以"FTP_DIR"开头
            if not homedir:
                homedir = self.modify_homedir
            else:
                if not homedir.startswith('/'):
                    homedir = settings.FTP_DIR + '/' + homedir
                else:
                    if not homedir.startswith(settings.FTP_DIR):
                        self.context['error_info'] = "您无权访问%s目录" % homedir
                        return render(request, "html/error.html", self.context)


            # 密码和确认密码是否相同
            if password == confirm_password:
                users = self.ftp.getuser()
                if self.modify_user not in users:
                    self.context['error_info'] = "用户不存在,请注册"
                    return render(request, "html/error.html", self.context)
                else:
                    # 修改用户配置文件，创建用户家目录
                    self.ftp.write_config(self.modify_user, homedir, can_upload, can_download , can_createdir, can_deletion)
                    self.ftp.create_homedir(homedir)

                    if password:
                        # 修改用户密码
                        self.ftp.modify_passwd(self.modify_user, password)

                    # 返回修改成功信息
                    self.context['username'] = self.modify_user
                    self.context['homedir'] = homedir
                    self.context['can_upload'] = can_upload
                    self.context['can_download'] = can_download
                    self.context['can_createdir'] = can_createdir
                    self.context['can_deletion'] = can_deletion
                    self.ftp.write_db(self.context)

                    return render(request, "html/m_table.html", self.context)
            else:
                self.context['error_info'] = "两次密码输入不一致"
                return render(request, "html/error.html", self.context)
        else:
            if request.user.is_authenticated:
                self.context['Users'] = self.ftp.getuser()
                return render(request, "html/choise.html", self.context)
            else:
                self.context['error_info'] = "您还没有登录！！!"
                return render(request, "html/error_admin.html", self.context)
