from requests.sessions import Session
from urllib.parse import urljoin
import urllib3
from config import my_config


def request(
        method,
        path,
        cookie=None,
        headers=None,
        params=None,
        data=None,
        json=None,
        files=None,
        timeout=None
):
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
    homepage = my_config['homepage']
    url = urljoin(homepage, path)
    if not headers:
        headers = {}
    headers.update({"Referer": urljoin(homepage, '/dsm/'),
                    "Accept": "application/json, text/plain, */*",
                    "Accept-Encoding": "gzip, deflate, br",
                    "Accept-Language": "zh-CN,zh;q = 0.9",
                    "Origin": homepage,
                    "User-Agent": "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.127 Safari/537.36"
                    })
    if cookie:
        headers.update({"Cookie": "XSRF-TOKEN="+cookie[0]+"; calamari_sessionid="+cookie[1], "X-XSRF-Token":cookie[0]})

    with Session() as session:
        response = session.request(
            method=method,
            url=url,
            headers=headers,
            params=params,
            data=data,
            json=json,
            files=files,
            timeout=timeout,
            verify=False,
            allow_redirects=False
        )
        # 解决响应中文为Unicode编码
        # response.encoding = 'unicode_escape'
    return response