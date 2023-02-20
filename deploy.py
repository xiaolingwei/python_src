from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
import logging
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from func_timeout import func_set_timeout
import time
import copy


class Web:
    def __init__(self, driver):
        self.driver = driver

    def open_url(self, url):

        logging.info(f"******************************打开页面:{url}")
        self.driver.set_page_load_timeout(60)
        try:
            self.driver.get(url)
        except TimeoutException:
            raise TimeoutException("打开%s超时" % url)

    def find_element(self, locator, timeout=10):
        logging.info(f"定位元素{locator}")
        return WebDriverWait(self.driver, timeout).until(EC.presence_of_element_located(locator))  # 返回定位到的web元素对象

    def find_elements(self, locator, timeout=10):
        logging.info(f"定位元素{locator}")
        return WebDriverWait(self.driver, timeout).until(EC.presence_of_all_elements_located(locator))

    def visibility_element_located(self, locator, timeout=10):
        logging.info(f"定位元素{locator}")
        return WebDriverWait(self.driver, timeout).until(EC.visibility_of_element_located(locator))

    def click_js(self, locator, timeout=10):
        element = self.find_element(locator, timeout)
        logging.info("点击元素")
        self.driver.execute_script("arguments[0].click();", element)

    def click(self, locator, timeout=10):
        element = self.find_element(locator, timeout)
        logging.info("点击元素")
        element.click()

    def send_keys(self, locator, text, timeout=10):
        element = self.find_element(locator, timeout)
        logging.info(f"输入内容: {text}")
        element.clear()
        element.send_keys(text)

    def clear(self, locator, timeout=10):
        element = self.find_element(locator, timeout)
        logging.info("清空内容")
        element.clear()

    def get_screenshot_as_png(self):
        res = self.driver.get_screenshot_as_png()
        return res

    @property
    def get_source(self):
        """
        获取页面源代码
        """
        return self.driver.page_source

    def refresh(self):
        """
        刷新页面
        """
        logging.info("刷新页面")
        self.driver.refresh()
        time.sleep(2)

    def get_table_content(self, table_selector):
        """
        获取表格当前页数据
        Args:
            table_selector: 要操作的表的定位信息。 ("xpath", "...")
        Returns: 二维数组
        【
        【1，‘a’】，
        【2，‘b’】
        】
        """
        arr = []
        table_tr_list = self.find_element(table_selector).find_elements("tag name", "tr")
        for tr in table_tr_list:
            arr1 = tr.text.split("\n")
            arr.append(arr1)
        return arr

    def click_table_cell_at(self, table_selector, base_text, column_or_text_to_click, tag="button", base_column=None):
        """通过文本内容找到某一行，然后点击这一行的某个单元格
        :param table_selector: 要操作的表的定位信息。 ("xpath", "...")
        :param base_text: 某个单元格的文本内容，通过它查找出信息所在的行。文本内容要精确匹配。
        :param column_or_text_to_click: 通过列或者单元格的文本内容指定要点击的单元格。列号从1开始，列号指的是第几个按钮。文本内容要精确匹配。
        :param tag:点击元素标签类型
        :param base_column: 标示性元素所在的列，为了防止同一行中多个单元格中内容相同导致混淆，加入这个参数，
                如果不存在混淆的可能性，可以不传入这个参数。列号从1开始。
        :return:无返回值
        使用举例：
        比如有一张表，它显示学生的信息，每一行显示一个学生的信息，姓名在第二列，删除按钮在第1个。删除指定姓名的学生的信息，可以如下操作：
        click_table_cell_at("id=>table1","张三","删除")
        click_table_cell_at("id=>table1","张三","删除",base_column=2) #指明姓名在第二列
        click_table_cell_at("id=>table1","张三",1) #指明删除按钮在第1个
        click_table_cell_at("id=>table1","张三",1,base_column=2) #指明删除按钮在第1个,姓名在第二列
        """
        base = self.find_element(table_selector)
        time.sleep(1)
        if type(base_text) != str:
            raise ValueError("Parameter base_text must be a string!")
        if base_column is not None:
            self._is_valid_row_or_column_no(base_column)
            base = base.find_element("xpath", "./tbody[1]/tr/td[{0:d} and string() = '{1:s}']".format(base_column, base_text))
        else:
            base = base.find_element("xpath", "./tbody[1]/tr/td[string() = '{0:s}']".format(base_text))
        if type(column_or_text_to_click) == int:
            if column_or_text_to_click <= 0:
                raise ValueError("Parameter column_or_text_to_click must be a positive integer"
                                 " when used as column number to click")
            base.find_element("xpath", "../td//{1:s}[{0:d}]".format(column_or_text_to_click, tag)).click()
        elif type(column_or_text_to_click) == str:
            base.find_element("xpath", "../td//{1:s}[normalize-space(string())='{0:s}']".format(column_or_text_to_click, tag)).click()
        else:
            raise ValueError("Parameter column_or_text_to_click must be integer or string")

    @staticmethod
    def _is_valid_row_or_column_no(row_or_column_number):
        if type(row_or_column_number) != int:
            raise ValueError("Row and column number must be a integer.")
        if row_or_column_number <= 0:
            raise ValueError("Row and column number must be a positive integer.")


class MyDeploy(Web):

    username = "admin"
    passwd = "Admin@123"
    url = ""

    # 登录页面license继续试用按钮
    license_probation_button_locator = ("xpath", "/html/body/div/div[2]/div[2]/div/div[2]/div/div[4]/div/div[3]/div/button[2]")
    # 用户名输入框
    name_input_locator = ("xpath", "/html/body/div/div[2]/div[2]/div/div[2]/div/div[1]/div[2]/form/div[1]/div/div/input")
    # 密码输入框
    passwd_input_locator = ("xpath", "/html/body/div/div[2]/div[2]/div/div[2]/div/div[1]/div[2]/form/div[2]/div/div/input")
    # 验证码图片
    verify_code_locator = ("xpath", '//*[@id="code"]')
    # 验证码错误时提示语
    error_verify_locator = ("xpath", "/html/body/div/div[2]/div[2]/div/div[2]/div/div[1]/div[2]/div[2]")
    # 验证码输入框
    verify_code_input_locator = ("xpath", "/html/body/div/div[2]/div[2]/div/div[2]/div/div[1]/div[2]/form/div[3]/div/div/input")
    # 确认登录按钮
    submit_button_locator = ("xpath", "/html/body/div/div[2]/div[2]/div/div[2]/div/div[1]/div[2]/form/div[5]/div/button")

    # 关闭登录后弹出的风险按钮
    close_risk_button_locator = ("xpath", "/html/body/div[2]/div/div[2]")
    # 首页警告按钮:您的密码为默认密码，请尽快修改密码。
    passwd_prompt_button_locator = ("xpath", "/html/body/div[2]/div/div[2]")
    # ipv4管理网段输入框
    ipv4_management_network_input_locator = ('xpath', '/html/body/div[1]/div[2]/div[3]/div/div[2]/div/div[2]/div/div/div[1]/div/div[2]/form/div/div/div[1]/div/div[2]/div[2]/div/div/input')
    # 存储前端网段输入框
    storage_front_end_network_input_locator = ('xpath', '/html/body/div[1]/div[2]/div[3]/div/div[2]/div/div[2]/div/div/div[1]/div/div[2]/form/div/div/div[2]/div/div[2]/input')
    # 存储后端网输入框
    storage_back_end_network_input_locator = ('xpath', '/html/body/div[1]/div[2]/div[3]/div/div[2]/div/div[2]/div/div/div[1]/div/div[2]/form/div/div/div[3]/div/div[2]/input')
    # 节点管理员密码输入框
    node_passwd_input_locator = ('xpath', '/html/body/div[1]/div[2]/div[3]/div/div[2]/div/div[2]/div/div/div[1]/div/div[2]/form/div/div/div[4]/div/div/input')
    # 节点密码明文、密文切换
    node_passwd_hide_locator = ('xpath', '/html/body/div[1]/div[2]/div[3]/div/div[2]/div/div[2]/div/div/div[1]/div/div[2]/form/div/div/div[5]/div/div/span/span/i')
    # 客户名称
    customer_locator = ('xpath', '/html/body/div[1]/div[2]/div[3]/div/div[2]/div/div[2]/div/div/div[1]/div/div[2]/form/div/div/div[7]/div/div/input')
    # 集群名称
    cluster_name_locator = ('xpath', '/html/body/div[1]/div[2]/div[3]/div/div[2]/div/div[2]/div/div/div[1]/div/div[2]/form/div/div/div[8]/div/div/input')
    # ntp on
    ntp_on_locator = ('xpath', '/html/body/div[1]/div[2]/div[3]/div/div[2]/div/div[2]/div/div/div[1]/div/div[2]/form/div/div/div[5]/div/div/div/div/label[2]/span')
    # 下一步按钮
    next_button_locator = ('xpath', '/html/body/div[1]/div[2]/div[3]/div/div[2]/div/div[3]/div/button/span')

    # 节点池名称
    nodepool_name_input_locator = ('xpath', '/html/body/div/div[2]/div[3]/div/div[2]/div/div[2]/div/div/div[2]/div/div[2]/div[1]/form/div[1]/div/div/input')
    # 节点池描述
    nodepool_description_locator = ('xpath', '/html/body/div/div[2]/div[3]/div/div[2]/div/div[2]/div/div/div[2]/div/div[2]/div[1]/form/div[2]/div/div/input')
    # 节点池新建按钮
    nodepool_create_button_locator = ('xpath', '/html/body/div/div[2]/div[3]/div/div[2]/div/div[2]/div/div/div[2]/div/div[2]/div[1]/form/div[4]/div/button')
    # 节点池新建确认按钮
    nodepool_create_button_confirm_locator = ('xpath', '/html/body/div[1]/div[2]/div[3]/div/div[2]/div/div[2]/div/div/div[2]/div/div[4]/div/div[3]/div/button[1]')
    # 节点池列表
    nodepool_list_locator = ('xpath', '/html/body/div/div[2]/div[3]/div/div[2]/div/div[2]/div/div/div[2]/div/div[2]/div[2]/div/div[3]/table')
    # 新建节点池页面的下一步按钮
    next_button1_locator = ('xpath', '/html/body/div/div[2]/div[3]/div/div[2]/div/div[3]/div/button[2]/span')
    # 单节点满配磁盘数目
    nodepool_node_disk_num_locator = ("xpath", "/html/body/div/div[2]/div[3]/div/div[2]/div/div[2]/div/div/div[2]/div/div[2]/div[1]/form/div[3]/div/div/input")

    # 网络扫描按钮
    network_scan_button_locator = ('xpath', '/html/body/div/div[2]/div[3]/div/div[2]/div/div[2]/div/div/div[3]/div/div[2]/div[1]/form/div[7]/div/button/span')
    # 扫描出来的主机列表 表格定位
    host_list_table_locator = ('xpath', '/html/body/div/div[2]/div[3]/div/div[2]/div/div[2]/div/div/div[3]/div/div[2]/div[2]/div/div[1]/div[3]/table')
    # 下一页按钮
    host_list_next_page_button_locator = ('xpath', '/html/body/div[1]/div[2]/div[3]/div/div[2]/div/div[2]/div/div/div[3]/div/div[2]/div[2]/div/div[3]/div/button[3]/i')
    # 上一页按钮
    host_list_previous_page_button_locator = ('xpath', '/html/body/div[1]/div[2]/div[3]/div/div[2]/div/div[2]/div/div/div[3]/div/div[2]/div[2]/div/div[3]/div/button[2]/i')
    # 选页按钮
    host_list_select_page_button_locator = ("xpath", '/html/body/div[1]/div[2]/div[3]/div/div[2]/div/div[2]/div/div/div[3]/div/div[2]/div[2]/div/div[3]/div/slot/div/span/i')
    # 选页列表 1
    host_list_1_page_button_locator = ("xpath", '/html/body/ul/li[1]')

    # 选盘页面主机列表
    disk_host_list_locator = (By.CSS_SELECTOR, '.index_li.selectDiskHostName')
    #选盘页面NVME盘列表
    disk_disk_list_locator = (By.CSS_SELECTOR, '.card-right-list-data.nomore-name')
    #选盘页面的下一步
    next_button_in_diskpage_locator = ("xpath", '/html/body/div[1]/div[2]/div[3]/div/div[2]/div/div[3]/div/button[2]/span')
    # NUMA分配不均衡确认按钮
    disk_button_confirm_numa_uneven = ("xpath", '/html/body/div[8]/div/div[3]/button[1]/span')

    # 确认信息页面确认按钮
    info_button_confirm = ("xpath", '/html/body/div[1]/div[2]/div[3]/div/div[2]/div/div[3]/div/button[3]')

    def name_input(self):
        """
        输入用户名
        """
        self.send_keys(self.name_input_locator, self.username)

    def passwd_input(self):
        """
        输入密码
        """
        self.send_keys(self.passwd_input_locator, self.passwd)

    def click_submit(self):
        """
        点击登录按钮
        """
        self.click(self.submit_button_locator)

    def click_license_probation(self):
        """
        关闭license提示框
        """
        self.click(self.license_probation_button_locator)

    # def verify_code_input(self):
    #     """
    #     识别验证码并输入
    #     """
    #     element = self.find_element(("xpath", '//*[@id="code"]'))
    #     x, y = element.location.values()
    #     h, w = element.size.values()
    #     image_data = self.get_screenshot_as_png()
    #     screenshot = Image.open(BytesIO(image_data))
    #     result = screenshot.crop((x, y, x + w, y + h))
    #     result.save('verify_code.png')
    #     code = self.recognize('verify_code.png')
    #
    #     self.send_keys(self.verify_code_input_locator, code)

    def is_success_verify_code(self):
        """
        校验验证码是否正确
        """
        try:
            self.find_element(self.error_verify_locator, timeout=2)
        except TimeoutException:
            return True
        else:
            return False

    def close_risk_prompt(self, timeout=3):
        """
        关闭登录后风险提示框
        """
        self.click(self.close_risk_button_locator, timeout=timeout)

    def close_passwd_prompt(self):
        """
        关闭右上角提示修改密码的提示框
        """
        self.click(self.passwd_prompt_button_locator)

    "输入ipv4管理网段"
    def ipv4_management_network_input(self, text):
        self.send_keys(self.ipv4_management_network_input_locator, text)

    "输入存储前端网"
    def storage_network1_input(self, text):
        self.send_keys(self.storage_front_end_network_input_locator, text)


    "输入存储后端网"
    def storage_network2_input(self, text):
        self.send_keys(self.storage_back_end_network_input_locator, text)

    "输入节点密码"
    def node_passwd_input(self, text):
        self.send_keys(self.node_passwd_input_locator, text)

    "清空节点密码框"
    def node_passwd_clear(self):
        self.clear(self.node_passwd_input_locator)

    "密码切换明文、密文"
    def node_passwd_hide_click(self):
        self.click(self.node_passwd_hide_locator)

    "ntp同步开启"
    def ntp_on_click(self):
        self.click(self.ntp_on_locator)

    "ntp集群内"
    def ntp_in_cluster_click(self):
        self.click(self.ntp_in_cluster_locator)

    "输入客户名称"
    def customer_input(self, text):
        self.send_keys(self.customer_locator, text)

    "输入集群名称"
    def cluster_name_input(self, text):
        self.send_keys(self.cluster_name_locator, text)

    "点击下一步"
    def click_next_button(self):
        self.click(self.next_button_locator)

    "输入nodepool 名称"
    def nodepool_name_input(self, text):
        self.send_keys(self.nodepool_name_input_locator, text)

    "输入nodepool 描述"
    def nodepool_description_input(self, text):
        self.send_keys(self.nodepool_description_locator, text)

    '点击新建节点池按钮'
    def nodepool_create_button_click(self):
        self.click(self.nodepool_create_button_locator)

    '点击新建节点池按钮确认'
    def nodepool_create_button_confirm(self):
        self.click(self.nodepool_create_button_confirm_locator)

    "返回节点池列表数据"
    def get_nodepool_table_data(self):
        """
        获取表格每行元素
        Returns:返回为列表，例：
        for i in list_data:
            print(i.text)
        """
        table = self.find_element(self.nodepool_list_locator)
        list_data = table.find_elements("tag name", "tr")
        return list_data

    # 输入单节点满盘数目
    def nodepool_node_disk_num_input(self, num_str):
        self.send_keys(self.nodepool_node_disk_num_locator, num_str)

    "下一步"
    def click_next_button_in_nodepool_page(self):
        self.click(self.next_button1_locator)


    "点击网络扫描按钮"
    def click_network_scan_button(self):
        self.click(self.network_scan_button_locator)


    "主机列表第一页"
    def host_list_first_page(self):
        self.click(self.host_list_select_page_button_locator)
        time.sleep(0.5)
        self.click(self.host_list_1_page_button_locator)

    "主机列表翻页"
    def click_host_list_next_page(self):
        self.click(self.host_list_next_page_button_locator)

    "等待主机认证"
    @func_set_timeout(300)
    def wait_host_check(self, tr_ele):
        while True:
            if tr_ele.find_element("xpath", "../td[3]/div/div").text == "正在获取...":
                time.sleep(1)
                continue
            elif tr_ele.find_element("xpath", "../td[3]/div/div").text in ["认证失败", "已存在集群"]:
                raise AssertionError("节点存在问题")
            break

    "勾选指定主机并配置主机用途、节点池、描述"
    def host_configure_all(self, host_list: list, host_role=None, host_nodepool=True, description=None):
        host_list = copy.deepcopy(host_list)

        base = self.find_element(self.host_list_table_locator)
        self.host_list_first_page()

        while True:
            res = self.get_table_content(self.host_list_table_locator)

            for i in res:
                for j in host_list:
                    if j in i:
                        base_tr = base.find_element("xpath", "./tbody[1]/tr/td[{0:d} and string() = '{1:s}']".format(2, j))
                        self.driver.execute_script("arguments[0].scrollIntoView();", base_tr)

                        self.wait_host_check(base_tr)

                        if not base_tr.find_element("xpath", "../td[1]/div/label").get_attribute("aria-checked"):
                            base_tr.find_element("xpath", "../td[1]/div/label/span/span").click()
                        else:
                            base_tr.find_element("xpath", "../td[1]/div/label/span/span").click()
                            base_tr.find_element("xpath", "../td[1]/div/label/span/span").click()

                        if host_role:
                            time.sleep(0.5)
                            base_tr.find_element("xpath", "../td[4]/div/div/div[2]/div/input").click()
                            if host_role == "监控节点":
                                time.sleep(0.5)
                                self.find_element(("xpath", "/html/body/div[last()]/div/div[1]/ul/li[1]/span")).click()
                            elif host_role == "存储节点":
                                time.sleep(0.5)
                                self.find_element(("xpath", "/html/body/div[last()]/div/div[1]/ul/li[2]/span")).click()
                            elif host_role == "监控节点和存储节点":
                                time.sleep(0.5)
                                self.find_element(("xpath", "/html/body/div[last()]/div/div[1]/ul/li[3]/span")).click()
                            else:
                                raise ValueError("节点类型要求为：监控节点、存储节点、监控节点和存储节点")
                        if host_nodepool:
                            time.sleep(0.5)
                            base_tr.find_element("xpath", "../td[2]/div").click()
                            ele = base_tr.find_element("xpath", "../td[5]/div/div/div[2]/div/input")
                            self.driver.execute_script("arguments[0].click();", ele)
                            time.sleep(1)
                            self.find_element(("xpath", "/html/body/div[last()]/div/div[1]/ul/li/span")).click()

                        if description:
                            time.sleep(0.5)
                            base_tr.find_element("xpath", "../td[2]/div").click()
                            ele = base_tr.find_element("xpath", "../td[6]/div/div/div[2]/input")
                            ele.clear()
                            ele.send_keys(description)

                        host_list.remove(j)

            if host_list:
                if self.find_element(self.host_list_next_page_button_locator).is_enabled():
                    self.click_host_list_next_page()
                else:
                    raise AssertionError("未匹配到主机列表")
            else:
                break

    "获取硬盘页面主机列表"
    def disk_host_list_get(self, hostname_list):
        disk_host_list = []
        for hostname in hostname_list:
            disk_host_list.append((self.disk_host_list_locator[0], self.disk_host_list_locator[1] + "[title=\"%s\"]"%hostname))
        return disk_host_list

    "获取硬盘页面硬盘列表"
    def disk_disk_list_get(self, diskname_list):
        disk_disk_list = []
        for diskname in diskname_list:
            disk_disk_list.append((self.disk_disk_list_locator[0], self.disk_disk_list_locator[1] + "[title=\"%s\"]"%diskname))
        return disk_disk_list

    "选择硬盘页面硬盘"
    def disk_disk_list_choose(self, hostname_list, diskname_list):
        disk_host_list = self.disk_host_list_get(hostname_list)
        disk_disk_list = self.disk_disk_list_get(diskname_list)
        print(disk_host_list)
        print(disk_disk_list)
        for disk_host in disk_host_list:
            self.click(disk_host)
            for disk_disk in disk_disk_list:
                self.click(disk_disk)

    "硬盘页面下一步"
    def click_next_button_in_disk_page(self):
        self.click(self.next_button_in_diskpage_locator)

    def click_disk_button_confirm_numa_uneven(self):
        self.click(self.disk_button_confirm_numa_uneven)

    def click_info_button_confirm(self):
        self.click(self.info_button_confirm)

if __name__ == "__main__":
    #创建 WebDriver 对象
    wd = webdriver.Chrome(service=Service(r'D:\chorme_drivers\chromedriver.exe'))
    wd.implicitly_wait(200)
    myweb = MyDeploy(wd)
    myweb.open_url("http://55.149.1.83/dsm/#/login/")
    myweb.click_license_probation()
    myweb.name_input()
    myweb.passwd_input()
    print("请输入验证码并登录：")
    input()
    myweb.close_risk_prompt()
    myweb.ipv4_management_network_input("55.149.1.0/20")
    myweb.storage_network1_input("197.16.102.0/24")
    myweb.storage_network2_input("198.16.102.0/24")
    myweb.node_passwd_input("Admin@123stor")
    myweb.ntp_on_click()
    myweb.customer_input("customer")
    myweb.cluster_name_input("cluster")
    myweb.click_next_button()
    # 节点池页面
    myweb.nodepool_name_input("n1")
    myweb.nodepool_node_disk_num_input("8")
    myweb.nodepool_create_button_click()
    myweb.nodepool_create_button_confirm()
    myweb.click_next_button_in_nodepool_page()
    # 主机页面
    myweb.click_network_scan_button()
    myweb.host_configure_all(["55.149.1.83", "55.149.1.85", "55.149.1.86"], host_role="监控节点和存储节点", description="")
    myweb.click_next_button_in_nodepool_page()
    myweb.disk_disk_list_choose(["node83", "node85", "node86"], ["nvme0n1", "nvme1n1", "nvme2n1", "nvme3n1"])
    myweb.click_next_button_in_disk_page()
    myweb.click_disk_button_confirm_numa_uneven()
    myweb.click_info_button_confirm()
