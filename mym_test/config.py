import pathlib
import yaml
file = pathlib.Path(__file__).parent.joinpath("conf.yml") # 取当前文件父文件夹下的conf.yml路径


# 集群信息的配置对象
class Config:

    @staticmethod
    def get_config_yml():
        with open(file) as f:
            conf_yml = yaml.load(f, Loader=yaml.FullLoader)
        return conf_yml
    
    @staticmethod
    def update_config_yml(flag, data):
        file_data = ""
        with open(file) as f:
            for line in f:
                if flag in line:
                    line = line.replace(line, data)
                file_data += line
        with open(file, mode='w') as f:
            f.write(file_data)
    
    @property
    def host_ips(self):
        return self.get_config_yml()["cluster"]["host_ips"]

    @property
    def user(self):
        return self.get_config_yml()["cluster"]["user"]

    @property
    def password(self):
        return self.get_config_yml()["cluster"]["passwd"]


conf = Config()
my_config = conf.get_config_yml() # 获取集群配置信息


if __name__ == "__main__":
    print(my_config['cluster']['data_disk']) # 输出集群的主页路径
