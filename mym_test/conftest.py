import pytest
from config import my_config
import requests
from config import my_config
import logging
from urllib.parse import urljoin
from requests.utils import dict_from_cookiejar

logging.basicConfig(level=logging.DEBUG, filename='ncs.log', filemode='a',
                    format='%(asctime)s - %(pathname)s[line:%(lineno)d] - %(levelname)s: %(message)s')


@pytest.fixture(autouse=True, scope="session")
def context(request):
    context = request.config.cache
    user = my_config['user']['admin']
    password = my_config['user']['password']
    context.set("user", "admin")
    info = context.get("user", {})

    print(info)
    return context


