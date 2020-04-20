# vsftpd 虚拟用户管理


# 依赖于
    1. python3.x (本人测试版本为3.6.8)
    2. django (本人测试版本为3.0.4) pip安装
    3. mysqlclient (本人测试版本为1.4.6) pip安装
    4. vsftpd server
    5. mysql server，devel


# vsftpd 配置文件,首次启动可进行修改(符合虚拟用户的配置)
    other/vsftpd.conf

# vusers 配置文件,首次启动可进行修改,确保db=虚拟用户文件
    other/vusers

# 启动文件
    other/accountManager
        1. PYTHON=$(which python3)
        2. BASEDIR='/opt/ftp_account_manager/account_manager' # 修改为ftp_account_manage工作绝对路径
        3. BIND_ADDRESS='0.0.0.0:8099' 			      # 监听ip和端口
        4. LOGFILE='/var/log/account_manager.log'	      # 日志文件路径

# settings 配置文件,将vsftpd服务配置完成后根据配置信息配置settings文件
    # vsftpd 本地用户(用于虚拟用户映射),需要手动创建
    FTP_USER = 'vftpuser'
    # vsftpd 主目录路径,需要手动创建
    FTP_DIR = '/ftp'
    # vsftpd 虚拟用户记录文件,需要手动创建 
    FTP_USER_FILE = '/etc/vsftpd/vusers.txt'
    # vsftpd 虚拟用户记录db文件(除后缀名尽量与虚拟用户记录文件保持一致)
    FTP_USER_DB_FILE = '/etc/vsftpd/vusers.db'
    # vsftpd 虚拟用户配置文件目录路径,需要手动创建
    FTP_USER_CONFIG_DIR = '/etc/vsftpd/user_conf'
    # vsftpd 虚拟用户信息记录文件
    FTP_USER_DB = os.path.join(BASE_DIR, 'data/user.db')

# running command
    # 检查数据改动
    python3 manage.py makemigrations
    # 进行数据迁移
    python3 manage.py migrate 
    # 创建超级用户
    python3 manage.py createsuperuser
    # 运行
    # 第一次运行请先运行 init_ftp.py 进行ftp初始化配置，否则可能会有问题
    python3 manage.py runserver ip:port
