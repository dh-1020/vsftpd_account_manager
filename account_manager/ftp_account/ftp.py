from django.conf import settings
from json import dumps, loads
from os import system, makedirs, rename, path, mknod
from shutil import copy, move


class Ftp:
    def __init__(self):
        self.config_path = settings.FTP_USER_FILE
        self.config_db_path = settings.FTP_USER_DB_FILE
        self.user_config = settings.FTP_USER_CONFIG_DIR
        self.user_db = settings.FTP_USER_DB
        self.FTP_DIR = settings.FTP_DIR
    

    # 获取已经存在的用户
    def getuser(self):
        with open(self.config_path, 'r', encoding='utf-8') as r_file:
            user_l = []
            for num, value in enumerate(r_file):
                if num % 2 == 0:
                    user_l.append(value.rstrip())
            return user_l

    def dbload(self):
        system('rm -f %s' % self.config_db_path)
        system('db_load -T -t hash -f %s %s' % (self.config_path, self.config_db_path))
        system('chmod 600 %s' % self.config_db_path)


    def create_homedir(self, homedir):
        if not path.exists(homedir):
            makedirs(homedir)

        system('chown %s:%s %s' % (settings.FTP_USER, settings.FTP_USER, homedir))
 
    # 创建用户、家目录
    def create_user(self, username, password, homedir):
        with open(self.config_path, 'a', encoding='utf-8') as w_file:
            s = username + '\n' + password + '\n'
            w_file.write(s)

        self.dbload() 
        self.create_homedir(homedir)


    # 写入用户配置及文件
    def write_config(self, username, homedir, can_upload, can_download, can_createdir, can_deletion):
        if can_download == 'YES':
            can_download = 'NO'
        else:
            can_download = 'YES'

        config = 'local_root=%s\nanon_upload_enable=%s\nanon_world_readable_only=%s\nanon_mkdir_write_enable=%s\nanon_other_write_enable=%s' %\
        (homedir, can_upload, can_download, can_createdir, can_deletion)

        with open(self.user_config + '/' + username, 'w', encoding='utf-8') as w_file:
            w_file.write(config)
            system('systemctl restart vsftpd')


    # 删除用户、删除用户db中记录信息、重命名用户家目录
    def delete(self, users):
        with open(self.user_db, 'r', encoding='utf-8') as r_file:
            user_d = loads(r_file.read())

        for user in users:
            user_home = self.FTP_DIR + '/' + user
            system("sed -i '/%s$/,+1d' %s" % (user, self.config_path))
            system("rm -f %s" % (self.user_config + '/' + user))
            rename(user_home, user_home + '_bak')
            user_d.pop(user)

        with open(self.user_db, 'w', encoding='utf-8') as w_file:
            w_file.write(dumps(user_d))       

        self.dbload()
        system('systemctl restart vsftpd')


     # 写入注册用户
    def write_db(self, context):
        # 用户db文件不存在或为空则创建幷写入 {}
        if path.exists(self.user_db):
            if not path.getsize(self.user_db):
                with open(self.user_db, 'a', encoding='utf-8') as w_file:
                    w_file.write('{}')
        else:
            with open(self.user_db, 'w', encoding='utf-8') as w_file:
                w_file.write('{}')

        with open(self.user_db, 'r', encoding='utf-8') as r_file:
            alluser = loads(r_file.read())

        # 写入用户字典
        with open(self.user_db, 'w', encoding='utf-8') as w_file:
            user_d = alluser[context['username']] = {}
            user_d['homedir'] = context['homedir']
            user_d['can_upload'] = context['can_upload']
            user_d['can_download'] = context['can_download']
            user_d['can_createdir'] = context['can_createdir']
            user_d['can_deletion'] = context['can_deletion']
            
            w_file.write(dumps(alluser))


    # 用户信息
    def userinfo_context(self, user):
        with open(self.user_db, 'r', encoding='utf-8') as r_file:
            user_d = loads(r_file.read())

        context = {}
        context['username'] = user
        context['homedir'] = user_d[user]['homedir']
        context['can_upload'] = user_d[user]['can_upload']
        context['can_download'] = user_d[user]['can_download']
        context['can_createdir'] = user_d[user]['can_createdir']
        context['can_deletion'] = user_d[user]['can_deletion']

        return context


    # 修改用户密码
    def modify_passwd(self, user, password):
        system("sed -ir '/%s$/{n;s/.*/%s/}' %s" % (user, password, self.config_path)) 
        self.dbload()
