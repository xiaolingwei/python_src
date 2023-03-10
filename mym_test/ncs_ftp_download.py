import os
import time
import logging
from ftplib import FTP

logging.basicConfig(level=logging.DEBUG, filename='ftp.log', filemode='a',
                    format='%(asctime)s - %(pathname)s[line:%(lineno)d] - %(levelname)s: %(message)s')

class WinScp():
    winscp_local_dir = "D:\WinSCP\WinSCP.com"   # winscp.com所在目录
    winscp_open = "open ftp://rd-ys:h3c%40rd-ys@10.121.207.120/"  # winscp账户密码ip等
    winscp_ftp_dir = "/Data-Out/m28573/version_list/"  # ftp上目录

    def mkdir(self, remote):
        result = os.system(f'{self.winscp_local_dir}  /command "{self.winscp_open}" "mkdir ""{remote}""" "exit"')
        return result

    def put(self, local, remote, version_name="ONEStor-NCS-E1110.tar.gz", times=10):
        result = os.system(
            f'{self.winscp_local_dir}  /command "{self.winscp_open}" "put ""{local}"" ""{remote}""" "exit"')
        count = 0
        while result:
            count += 1
            logging.info(f"第{count}重试FTP传输")
            path = remote + '/' + str(count) + "mym"
            self.mkdir(path)
            result = os.system(
                f'{self.winscp_local_dir}  /command "{self.winscp_open}" "put ""{local}"" ""{path}""" "exit"')
            print(f'{self.winscp_local_dir}  /command "{self.winscp_open}" "put ""{local}"" ""{path}""" "exit"')
            time.sleep(5)
            if count > times:
                logging.info("传输失败ERROR")
                break
        return result

    def get(self, local, remote):
        logging.info(f'{self.winscp_local_dir}  /command "{self.winscp_open}" "get ""{remote}"" ""{local}""" "exit"')
        result = os.system(
            f'{self.winscp_local_dir}  /command "{self.winscp_open}" "get ""{remote}"" ""{local}""" "exit"')
        return result


class My_Ftp(FTP):
    host = '10.121.207.120'
    port = 21
    username = 'rd-ys'
    password = 'h3c@rd-ys'
    path = "/Data-Out/m28573/version_list"
    version_list = []
    version_num_list = []
    new_version = 0

    def get_new_version(self):
        self.version_list = [x.split(' ')[-1] for x in self.version_list]
        logging.info(f'version list : {self.version_list}')
        self.version_num_list = [int(x) for x in self.version_list]
        logging.info(f'version num list : {self.version_num_list}')
        self.new_version = str(max(self.version_num_list))
        logging.info(f'new version : {self.new_version}')
        return self.new_version


class LocalDir():
    new_version = ""
    version_dir = r"D:\version"

    def version_list(self):
        os.chdir(self.version_dir)
        return os.listdir(path=self.version_dir)

    def version_int_list(self):
        os.chdir(self.version_dir)
        temp = self.version_list()
        return [int(x) for x in temp]

    def newest_version(self):
        os.chdir(self.version_dir)
        temp = self.version_int_list()
        self.new_version = str(max(temp))
        return self.new_version


while 1:
    # get ftp new version
    ftp = My_Ftp()
    ftp.connect(ftp.host, ftp.port)
    ftp.login(ftp.username, ftp.password)
    ftp.cwd(ftp.path)
    ftp.dir('.', ftp.version_list.append)
    new_version = ftp.get_new_version()

    # get local new version
    local = LocalDir()
    local_new_version = local.newest_version()

    if local_new_version != new_version:
        os.mkdir(new_version)
        os.chdir(new_version)
        local_path = os.getcwd()
        logging.info(f'local path : {local_path}')
        mywinscp = WinScp()
        mywinscp.get(local_path, f"/Data-Out/m28573/version_list/{new_version}")
        #os.system(f'D:\WinSCP\WinSCP.com  /command "open ftp://rd-ys:h3c@rd-ys@10.121.207.120:21" "get ""/Data-Out/m28573/version_list/{new_version}""  ""{local_path}""" "exit"')
    time.sleep(3600)


