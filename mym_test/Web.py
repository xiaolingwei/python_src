
import logging
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service


class Web(object):
    def __init__(self, driver):
        self.driver = driver
        logging.basicConfig(level=logging.DEBUG, filename='web.log', filemode='a', format='%(asctime)s - %(pathname)s[line:%(lineno)d] - %(levelname)s: %(message)s')

    def open_url(self, url):
        logging.info(f"打开页面:{url}")
        self.driver.set_page_load_timeout(60)
        try:
            self.driver.get(url)
        except TimeoutException:
            raise TimeoutException("打开%s超时" % url)

    def find_element(self, locator, timeout=10):
        logging.info(f"定位元素{locator}")
        return WebDriverWait(self.driver, timeout).until(EC.presence_of_element_located(locator))  # 返回定位到的web元素对象

    def find_elements(self, locator, timeout=10):
        logging.info(f"定位多个元素{locator}")
        return WebDriverWait(self.driver, timeout).until(EC.presence_of_all_elements_located(locator))

    def visibility_element_located(self, locator, timeout=10):
        logging.info(f"定位元素是否可见{locator}")
        return WebDriverWait(self.driver, timeout).until(EC.visibility_of_element_located(locator))

    def click_js(self, locator, timeout=10):
        element = self.find_element(locator, timeout)
        logging.info(f"点击元素(js){element}")
        self.driver.execute_script("arguments[0].click();", element)

    def click(self, locator, timeout=10):
        element = self.find_element(locator, timeout)
        logging.info(f"点击元素{element}")
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


if __name__ == '__main__':
    wd = webdriver.Chrome(service=Service(r'D:\chorme_drivers\chromedriver.exe'))
    my_web = Web(wd)
    my_web.open_url("http://55.149.1.83/dsm/#/storage/handyha")