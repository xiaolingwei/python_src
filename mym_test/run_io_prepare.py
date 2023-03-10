import requests
from config import my_config
import logging
from urllib.parse import urljoin
from requests.utils import dict_from_cookiejar
from request import request


logging.basicConfig(level=logging.DEBUG, filename='ncs.log', filemode='a',
                    format='%(asctime)s - %(pathname)s[line:%(lineno)d] - %(levelname)s: %(message)s')


def login(user=my_config['user']['user'], password=my_config['user']['password'], homepage=my_config['homepage']):

    path = "/api/v1/auth/login/"
    url = urljoin(homepage, path)
    logging.info(f'登录url:{url}')
    res = request('get', url)
    logging.info(f"登录结果：{res}")
    token = dict_from_cookiejar(res.cookies)["XSRF-TOKEN"]
    logging.info(f'登录get获取token:{token}')
    session_id = dict_from_cookiejar(res.cookies)["calamari_sessionid"]
    logging.info(f'登录get获取session_id:{session_id}')
    headers = {"Cookie": "XSRF-TOKEN="+token+"; calamari_sessionid="+session_id}
    json = {
        "username": user,
        "password": password
    }
    res = request('post', url, headers=headers, json=json)
    token = dict_from_cookiejar(res.cookies)["XSRF-TOKEN"]
    session_id = dict_from_cookiejar(res.cookies)["calamari_sessionid"]
    logging.info(f'登录post获取token:{token}')
    logging.info(f'登录post获取session_id:{session_id}')
    cookie = [token, session_id]
    return cookie


def get_cluster_id(cookie):
    path = my_config['homepage'] + "/api/v3/cluster"
    logging.info(f'get cluster id restful port " {path}')
    response = request('get', path, cookie=cookie).json()
    logging.info(f'get cluster id response:{response}')
    return response['result']['id']


# 创建池
def pool_create(nodepool, name, cookie, size=100, domain="node", data_rebuild="ordinary"):
    cluster_id = get_cluster_id(cookie)
    path = my_config['homepage'] + f"/api/v3/onestor/{cluster_id}/plat/pool"
    logging.info(f"pool create url:{path}")
    summary=[]
    summary.append("pool.rbd.tip.buildPoolCreat")
    summary.append([name])
    json = {
        "nodepool_name": nodepool,
        "pool_name": name,
        "pool_size": size,
        "domain": domain,
        "data_rebuild": data_rebuild,
        "summary": summary,
    }
    logging.info(f"pool create data json:{json}")
    return request('POST', path, cookie=cookie, json=json)


# 创建卷
def lun_create(pool_name, lun_name, lun_size, cookie, lun_type="thin",  redundancy="replicated", replicate_num=3, min_size="data", description=None):
    cluster_id = get_cluster_id(cookie)
    path = my_config['homepage'] + f"/api/v3/onestor/{cluster_id}/blk/lun"
    json = {
        "description": description,
        "lun_name": lun_name,
        "lun_size": lun_size,
        "lun_type": lun_type,
        "pool_name": pool_name,
        "redundancy": redundancy,
        "replicate_num": replicate_num,
        "min_size": min_size
    }

    return request('POST', path, cookie=cookie, json=json)

def set_block_service_network(cookie, block_service_network=my_config['cluster']['storage_network1'], nodepool_name=my_config['cluster']['nodepool'], block_service_network6="", summary="配置块服务网段", noQueue="true"):
    cluster_id = get_cluster_id(cookie)
    path = my_config['homepage'] + f"/api/v3/onestor/{cluster_id}/blk/TGT_put_block_service_network"
    json = {
        "block_service_network": block_service_network,
        "block_service_network6": block_service_network6,
        "summary": summary,
        "noQueue": noQueue,
        "nodepool_name": nodepool_name
    }
    return request('POST', path, cookie=cookie, json=json)


def TGT_host_create(cookie, host_name_tgt, host_os_type, nodepool_name, initiators, host_ip_tgt="", host_description=""):
    cluster_id = get_cluster_id(cookie)
    path = my_config['homepage'] + f"/api/v3/onestor/{cluster_id}/blk/TGT_host_create"
    json = {
        "host_name_tgt": host_name_tgt,
        "host_os_type": host_os_type,
        "host_ip_tgt": host_ip_tgt,
        "host_description": host_description,
        "initiators": initiators,
        "nodepool_name": nodepool_name
    }
    return request('POST', path, cookie=cookie, json=json)

def TGT_host_group_create(cookie, nodepool_name, host_group_name, description="" ):
    cluster_id = get_cluster_id(cookie)
    path = my_config['homepage'] + f"/api/v3/onestor/{cluster_id}/blk/TGT_host_group_create"
    json = {
        "nodepool_name": nodepool_name,
        "host_group_name": host_group_name,
        "description": description
    }
    return request('POST', path, cookie=cookie, json=json)


def TGT_host_group_add_host(cookie, nodepool_name, host_group_id, host_id_tgt ):
    cluster_id = get_cluster_id(cookie)
    path = my_config['homepage'] + f"/api/v3/onestor/{cluster_id}/blk/TGT_host_group_add_host"
    json = {
        "nodepool_name": nodepool_name,
        "host_group_id": host_group_id,
        "host_id_tgt": host_id_tgt
    }
    return request('POST', path, cookie=cookie, json=json)


def TGT_ha_create(cookie, vip, master_ip, slave_ips, vrid=0, loadbalance=False, multipath=False):
    '''
    Args:
        vip: 高可用ip
        master_ip: 主用节点
        slave_ips：备用节点list
        vrid: 高可用组id
        loadbalance:
        multipath：
    Returns: 响应结果
    '''
    cluster_id = get_cluster_id(cookie)
    path = my_config['homepage'] + f"/api/v3/onestor/{cluster_id}/request"
    json = dict()
    json["comp"] = "COMP_HA"
    json["op"] = "TGT_ha_create"
    json["data"] = {}
    json["data"]["vip"] = vip
    json["data"]["master_ip"] = master_ip
    json["data"]["slave_ips"] = slave_ips
    json["data"]["vrid"] = vrid
    json["data"]["loadbalance"] = loadbalance
    json["data"]["multipath"] = multipath
    json["summary"] = []
    json["summary"].append("blockstorage.iscsi.createIscsi")
    json["summary"].append([vip])

    return request('POST', path, cookie=cookie, json=json)


def add_lun(cookie, nodepool_name, host_group_id, lun_id, lun_map_type="lun"):
    cluster_id = get_cluster_id(cookie)
    path = my_config['homepage'] + f"/api/v3/onestor/{cluster_id}/blk/map/add_lun"
    json = {
        "nodepool_name": nodepool_name,
        "host_group_id": host_group_id,
        "lun_id":lun_id,
        "lun_map_type":lun_map_type
    }
    return request('POST', path, cookie=cookie, json=json)


def TGT_host_get_in_batch(cookie, limit=10, sort_order="asc", sort_key="host_name_tgt", offset=0, key_word="",  nodepool_name=my_config['cluster']['nodepool'],
                         comp="COMP_TGT", op="TGT_host_get_in_batch"):
    cluster_id = get_cluster_id(cookie)
    path = my_config['homepage'] + f"/api/v3/onestor/{cluster_id}/request"
    json = {
        "data":{"limit":limit,"sort_order":sort_order,"sort_key":sort_key,"offset":offset,"key_word":key_word,"nodepool_name":nodepool_name},
        "comp":comp,
        "op":op
    }
    return request('POST', path, cookie=cookie, json=json)


def TGT_host_group_get_in_batch(cookie, limit=10, sort_order="asc", sort_key="host_group_name", offset=0, key_word="",  nodepool_name=my_config['cluster']['nodepool'],
                         comp="COMP_TGT", op="TGT_host_group_get_in_batch"):
    cluster_id = get_cluster_id(cookie)
    path = my_config['homepage'] + f"/api/v3/onestor/{cluster_id}/request"
    json = {
        "data":{"limit":limit,"sort_order":sort_order,"sort_key":sort_key,"offset":offset,"key_word":key_word,"nodepool_name":nodepool_name},
        "comp":comp,
        "op":op
    }
    return request('POST', path, cookie=cookie, json=json)


def lun_query(cookie, nodepool_name, pool_name, limit=200, offset=0, sort_key="", key_word="", sort_order=""):
    cluster_id = get_cluster_id(cookie)
    path = my_config['homepage'] + f"/api/v3/onestor/{cluster_id}/blk/lun?pool_name={pool_name}&nodepool_name={nodepool_name}"
    return request('GET', path, cookie=cookie)


# 参数
nodepool_name = my_config['cluster']['nodepool']
pool_name = "p1"
lun_name = "L1"
lun_size = 1000000
initiators=[{
    "chap_id_in": "",
    "chap_id_out": "",
    "host_nqn": "nqn.2014-08.org.nvmexpress:uuid:2468c5fb-2cce-4b17-ac34-81492f430684",
    "host_id": "5ea60709-7a88-481d-b8e9-4ca06014040e"
    }]
host_name = "n83"
tgt_group_name = "G1"
vip = "197.16.102.234"
master_ip = "197.16.102.151"
slave_ips = ["197.16.102.153"]


# 登录
cookie = login()
# 创池 sub_node  node
res = pool_create(nodepool_name, pool_name, cookie, domain="node")
print(f"pool create:{res.json()}")
# 创卷 ec replicated   3   {"k":4,"m":2}
res = lun_create(pool_name, lun_name, lun_size, cookie, lun_type="thin",  redundancy="ec", replicate_num={"k":4,"m":2}, min_size="data")
print(f"lun create:{res.json()}")
# 块服务网段设置
res = set_block_service_network(cookie)
print(f"block service network set:{res.json()}")
# 创主机
res = TGT_host_create(cookie, host_name, 'Linux', nodepool_name, initiators)
print(f"tgt host create:{res.json()}")
# 创主机组
res = TGT_host_group_create(cookie, nodepool_name, tgt_group_name)
print(f"tgt host group create:{res.json()}")
# 查主机ID
res = TGT_host_get_in_batch(cookie)
host_id_list = [x['host_id_tgt'] for x in res.json()['data']['result']]
print(f"host id list:{host_id_list}")
# 查主机组ID
res = TGT_host_group_get_in_batch(cookie)
host_group_id_list = [x['host_group_id'] for x in res.json()['data']['result']]
print(f"host group id list:{host_group_id_list}")
# 主机加入主机组
res = TGT_host_group_add_host(cookie, nodepool_name, host_group_id_list[0], host_id_list)
print(f"tgt group add host :{res.json()}")
# 创建tgt HA
res=TGT_ha_create(cookie, vip, master_ip, slave_ips, vrid=0, loadbalance=False, multipath=False)
print(f"tgt ha create :{res.json()}")
# 查询卷ID
res = lun_query(cookie, nodepool_name, pool_name)
lun_id_list = [x['lun_id'] for x in res.json()['data']['result']]
print(f"lun id list :{lun_id_list}")
# 添加卷到主机组
res = add_lun(cookie, nodepool_name, host_group_id_list[0], lun_id_list)
print(f"add lun to host group :{res.json()}")