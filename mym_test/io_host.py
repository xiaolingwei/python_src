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

    b1 = ('xpath', '/html/body/div/div[2]/div[3]/div/div[2]/div/div[2]/div/div/div[3]/div/div[2]/div[2]/div/div[1]/div[3]/table')
    b2 = ('xpath', '/html/body/div[1]/div[2]/div[3]/div/div[2]/div/div[1]/div[1]/div[2]/ul/li[2]/div/span')
    b3 = ('xpath', '/html/body/div[1]/div[2]/div[3]/div/div[2]/div/div[1]/div[1]/div[2]/ul/li[2]/ul/div/li[1]/span')
    b4 = ('xpath', '/html/body/div/div[2]/div[3]/div/div[2]/div/div[2]/div/div[1]/div[3]/div[1]/div/button[1]/span') # 新建业务主机
    b5 = ('xpath', '/html/body/div[1]/div[2]/div[3]/div/div[2]/div/div[2]/div/div[2]/div/div[2]/form/div[2]/div/div/input') # 名字
    b6 = ('xpath', '/html/body/div[1]/div[2]/div[3]/div/div[2]/div/div[2]/div/div[2]/div/div[2]/form/div[3]/div/div/div/span/span/i') # 下拉框
    b7 = ('xpath', '/html/body/div[4]/div[1]/div[1]/ul/li[2]') #linux
    b8 = ('xpath', '/html/body/div[1]/div[2]/div[3]/div/div[2]/div/div[2]/div/div[2]/div/div[2]/form/div[5]/div/div/input') # nqn
    b9 = ('xpath', '/html/body/div[1]/div[2]/div[3]/div/div[2]/div/div[2]/div/div[2]/div/div[3]/div/button[1]') # 确定


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

    def cb1(self):
        self.click(self.b1)
    def cb2(self):
        self.click(self.b2)
    def cb3(self):
        self.click_js(self.b3)
    def cb4(self):
        self.click_js(self.b4)
    def cb5(self, name):
        self.send_keys(self.b5, name)
    def cb6(self):
        self.click(self.b6)
    def cb7(self):
        self.click(self.b7)
    def cb8(self, nqn):
        self.send_keys(self.b8, nqn)
    def cb9(self):
        self.click(self.b9)

if __name__ == "__main__":
    #创建 WebDriver 对象
    wd = webdriver.Chrome(service=Service(r'D:\chorme_drivers\chromedriver.exe'))
    wd.implicitly_wait(200)
    myweb = MyDeploy(wd)
    myweb.open_url("http://55.149.1.83/dsm/#/login/")

    print("请输入验证码并登录：")
    input()
    # 创建tgt高可用
    for i in range(10000):
        myweb.cb4()
        myweb.cb5("n"+str(i))
        myweb.cb6()
        time.sleep(0.1)
        myweb.cb7()
        myweb.cb8("nqn.2014-08.org.nvmexpress:uuid:2468c5fb-2cce-4b17-ac34-81492f4"+str(i).zfill(5))
        myweb.cb9()
        myweb.cb3()
        time.sleep(2)