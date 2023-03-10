import logging
import paramiko
import time

class SSH(object):
    def __init__(self):
        self._ssh = paramiko.SSHClient()
        self._ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        self.ip = None
        self.username = None
        self.password = None

    def connect(self, ip, username, password):
        logging.info("******************* 登录节点:%s" % ip)
        self._ssh.connect(ip, 22, username, password, timeout=10)
        self.ip = ip
        self.username = username
        self.password = password

    def close_connection(self):
        if self._ssh:
            logging.info("***************** 关闭节点连接:%s" % self.ip)
            self._ssh.close()

    def __del__(self):
        self.close_connection()

    def run_command(self, cmd, check=False, timeout=None, output=1):
        """
        命令执行完成后，返回结果，且该方法不可交互
        Args:
            cmd: 命令
            check: 是否检查运行命令是否成功
            timeout: 设置超时
            output: 0：返回标准输入，
                    1：返回标准输出，
                    2：返回标准错误
                    3：全部返回,列表形式
                    4：不返回
        Returns:返回标准输出stdout

        """
        logging.info("*******************%s 执行命令%s" % (self.ip, cmd))
        stdin, stdout, stderr = self._ssh.exec_command(cmd, timeout=timeout)

        try:
            stdin_info = "stdin: {0}".format(stdin.read().decode('utf-8'))
        except Exception as e:
            stdin_info = "stdin: ERROR " + str(e)

        stdout_info = stdout.read().decode("utf-8")
        if stdout_info:
            logging.info("stdout输出:%s" % stdout_info)

        stderr_info = stderr.read().decode("utf-8")
        if stderr_info:
            logging.info("stderr输出:%s" % stderr_info)

        if check:
            assert stdout.channel.recv_exit_status() == 0, ["stdout:" + stdout_info, "stderr:" + stderr_info]

        result = list()
        result.append(stdin_info.strip())
        result.append(stdout_info.strip())
        result.append(stderr_info.strip())

        if output == 0:
            return result[0]
        elif output == 1:
            return result[1]
        elif output == 2:
            return result[2]
        elif output == 3:
            return result
        else:
            return

    def sftp_upload(self, source_dir, target_dir, ip=None, user=None, password=None):
        """
        文件上传
        Args:
            source_dir: 源文件路径
            target_dir: 目标路径,需指定文件名
            ip: 目标ip（如果调用了connect方法已经传过该参数，可不传）
            user: 用户（如果调用了connect方法已经传过该参数，可不传）
            password: 密码（如果调用了connect方法已经传过该参数，可不传）

        Returns:

        """
        ip = self.ip if not ip else ip
        user = self.username if not user else user
        password = self.password if not password else password

        trans = paramiko.Transport(sock=(ip, 22))
        trans.connect(username=user, password=password)
        sftp_client = paramiko.SFTPClient.from_transport(trans)
        logging.info("******************* 拷贝%s到%s" % (source_dir, target_dir))
        sftp_client.put(source_dir, target_dir)

        sftp_client.close()

    def sftp_download(self, source_dir, target_dir, ip=None, user=None, password=None):
        """
        文件下载
        Args:
            source_dir: 源文件路径
            target_dir: 目标路径,需指定文件名
            ip: 目标ip（如果调用了connect方法已经传过该参数，可不传）
            user: 用户（如果调用了connect方法已经传过该参数，可不传）
            password: 密码（如果调用了connect方法已经传过该参数，可不传）

        Returns:

        """
        ip = self.ip if not ip else ip
        user = self.username if not user else user
        password = self.password if not password else password

        trans = paramiko.Transport(sock=(ip, 22))
        trans.connect(username=user, password=password)
        sftp_client = paramiko.SFTPClient.from_transport(trans)
        logging.info("******************* 拷贝%s到%s" % (source_dir, target_dir))
        sftp_client.get(source_dir, target_dir)

        sftp_client.close()
if __name__ == "__main__":
    my_ssh = SSH()

    for i in range(3):
        print("This is turn :", i)

        # 执行node83
        print("this node is 87")
        my_ssh.connect("55.148.1.87", "root", "Admin@123stor")
        result = my_ssh.run_command("dmg sys query -v")
        print(result)
        time.sleep(5)
        result = my_ssh.run_command("dmg pool query p1")
        print(result)
        time.sleep(10)
        my_ssh.run_command("reboot")
        my_ssh.close_connection()
        time.sleep(7000)

        # 执行node85
        print("this node is 88")
        my_ssh.connect("55.148.1.88", "root", "Admin@123stor")
        result = my_ssh.run_command("dmg sys query -v")
        print(result)
        time.sleep(5)
        result = my_ssh.run_command("dmg pool query p1")
        print(result)
        time.sleep(10)
        my_ssh.run_command("reboot")
        my_ssh.close_connection()
        time.sleep(7000)

        # 执行node86
        print("this node is 89")
        my_ssh.connect("55.148.1.89", "root", "Admin@123stor")
        result = my_ssh.run_command("dmg sys query -v")
        print(result)
        time.sleep(5)
        result = my_ssh.run_command("dmg pool query p1")
        print(result)
        time.sleep(10)
        my_ssh.run_command("reboot")
        my_ssh.close_connection()
        time.sleep(7000)




