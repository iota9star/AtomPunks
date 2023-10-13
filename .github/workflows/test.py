import os
import json
import requests
from urllib3.util.retry import Retry

MAX_RETRY = 3
RETRY_DELAY = 1

# 獲取存儲庫的根目錄
script_dir = os.path.dirname(__file__)
repository_root = os.path.join(script_dir, "..", "..")
json_file_path = os.path.join(repository_root, "atompunk_data_list_v0.json")

def process_atompunks_data_list_v0(filename):
    # 读取JSON文件
    with open(filename, 'r') as file:
        data = json.load(file)

    # 创建一个字典来存储最小的 "atomical_number" 值
    unique_punks = {}

    # 迭代处理数据
    new_data = []
    for item in data:
        punk_id = item['punk_id']
        atomical_number = item['atomical_number']

        # 如果 punk_id 不在字典中，或者 atomical_number 更小，更新字典
        if punk_id not in unique_punks or atomical_number < unique_punks[punk_id]:
            unique_punks[punk_id] = atomical_number

    # 再次迭代数据，只保留最小的 "atomical_number" 值的项
    for item in data:
        punk_id = item['punk_id']
        atomical_number = item['atomical_number']

        if atomical_number == unique_punks[punk_id]:
            new_data.append(item)

    # 将结果写回JSON文件
    with open(filename, 'w') as file:
        json.dump(new_data, file, indent=4)
        print("[Remove duplicate objects] atompunk_data_list_v0.json")

# 递归函数来查找所需的值
def find_value(data, target_key):
    if isinstance(data, dict):
        for key, value in data.items():
            if key == target_key:
                return value
            else:
                result = find_value(value, target_key)
                if result is not None:
                    return result
    elif isinstance(data, list):
        for item in data:
            result = find_value(item, target_key)
            if result is not None:
                return result

def get_data_from_url(number):
    url = f"https://ep.atomicals.xyz/proxy/blockchain.atomicals.get?params=[{number}]&pretty"

    session = requests.Session()
    retries = Retry(total=MAX_RETRY, backoff_factor=RETRY_DELAY)
    adapter = requests.adapters.HTTPAdapter(max_retries=retries)
    session.mount('http://', adapter)
    session.mount('https://', adapter)

    try:
        response = session.get(url, timeout=10)

        if response.status_code == 200:
            data = response.json()
            print(f"fetch data for atomical {number}")
            return data
        else:
            print(f"Failed to fetch data for number {number}. Retrying...")
    except requests.RequestException as e:
        print(f"Error occurred while fetching data for number {number}: {e}")

    return None

def process_data(start_number, end_number, existing_data_file, v0_file):
    if os.path.exists(existing_data_file):
        with open(existing_data_file, 'r') as existing_file:
            existing_data = json.load(existing_file)
    
    if os.path.exists(v0_file):
        with open(v0_file, 'r') as v0_file_obj:
            v0_data = json.load(v0_file_obj)
    
    result_list = []

    for number in range(start_number, end_number):
        data = get_data_from_url(number)
        
        # 指定要查找的目标字段
        target_key = "$b"

        # 查找目标值
        b_value = find_value(data, target_key)

        # 檢查 desired_value 是否為 None
        if b_value is not None:
            hex = b_value['$d']
            target_string = "89504e470d0a1a0a0000000d4948445200000018000000180806000000e0773df8000000"

            if data and data["response"]["result"]["type"] == "NFT":
            
                if target_string in hex:
                    atomical_number = int(data["response"]["result"]["atomical_number"])
                    atomical_id = data["response"]["result"]["atomical_id"]
                    
                    for v0_item in v0_data:
                        if v0_item["hex"] in hex:
                            break
                    else:
                        for existing_item in existing_data:
                            if existing_item["hex"] in hex:
                                new_data = {
                                    "atomical_number": atomical_number,
                                    "atomical_id": atomical_id,
                                    "punk_id": existing_item["punk_id"],
                                    "hex": hex,
                                    "version": 0
                                }
                                result_list.append(new_data)
                                print(f"Found matching hex in existing_data, atomicals_number: {number}, punk id: {existing_item['punk_id']}")

    if result_list:
        v0_data.extend(result_list)
    else:
        print("no new data")

    with open(v0_file, "w") as v0_file_obj:
        json.dump(v0_data, v0_file_obj, indent=4)
        print("[Update Finished] atompunk_data_list_v0.json")

def get_atomical_count():
    url = "https://ep.atomicals.xyz/proxy/blockchain.atomicals.list?params=%5B1,-1,0%5D"

    # 发送GET请求获取JSON数据
    response = requests.get(url)

    # 检查响应状态码，200表示成功
    if response.status_code == 200:
        data = response.json()  # 解析JSON数据

        # 提取"atomical_count"的值
        atomical_count = data["response"]["global"]["atomical_count"]
        return atomical_count
    else:
        print("无法获取数据，HTTP状态码:", response.status_code)
        return None

def get_last_atomical_number(filename):
    try:
        with open(filename, 'r', encoding='utf-8') as file:
            data = json.load(file)
            if data:
                last_item = data[-1]
                return last_item["atomical_number"]
            else:
                return None
    except Exception as e:
        print(f"Error while getting last atomical number: {e}")
        return None

def process_data_sync():
    last_atomical_number = get_last_atomical_number(json_file_path)

    if last_atomical_number is not None:
        # 设置start_number为最后一个元素的"atomical_number"值
        start_number = last_atomical_number

        # 获取end_number的值
        end_number = get_atomical_count()
        print(f"start:{start_number},end:{end_number}")

        if end_number is not None:
            # 使用获取的start_number和end_number进行进一步处理
            existing_data_file = "10kpunk_data.json"
            v0_file = json_file_path
            process_data(start_number, end_number, existing_data_file, v0_file)
            # 使用函数处理 JSON 文件
            process_atompunks_data_list_v0(v0_file)

if __name__ == "__main__":
    process_data_sync()
    print("UpdatePunkList.py 执行完成")
