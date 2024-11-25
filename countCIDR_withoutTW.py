# -*- coding: utf-8 -*-
"""
Created on Mon Nov 25 22:01:05 2024

@author: Chiakai
"""

import requests
import os
import tarfile
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# 下載檔案的函式
def download_file(url, file_name):
    try:
        os.remove(file_name)  # 如果檔案已存在，先刪除
    except:
        pass
    response = requests.get(url, stream=True, verify=False)
    response.raise_for_status()
    with open(file_name, 'wb') as file:
        for chunk in response.iter_content(chunk_size=8192):
            file.write(chunk)
    return file_name

# 處理壓縮檔並排除台灣 (TW) 的 IP CIDR
def process_cidr_excluding_tw(tar_gz_path, output_path, ip_version):
    with tarfile.open(tar_gz_path, 'r:gz') as tar, open(output_path, 'w') as output_file:
        for member in tar.getmembers():
            data_file_name = member.name
            if 'MD5SUM' in data_file_name:  # 略過校驗檔案
                continue
            if data_file_name != '.':
                # 獲取檔案名稱
                base_name = os.path.basename(data_file_name)
                if not base_name.startswith('.'):
                    # 從檔名中提取國家代碼
                    country_code, ext = os.path.splitext(base_name)
                    country_code = country_code.upper()
                    # 排除台灣 (TW)
                    if country_code == 'TW':
                        continue
                    # 略過不符合規範的檔案
                    if '.' in country_code or len(country_code) > 2:
                        print(f'{data_file_name} 資料異常，國家代碼為 {country_code}')
                    # 讀取 CIDR 並寫入輸出檔案
                    with tar.extractfile(member) as file:
                        content = file.read().strip()
                        if content:
                            content_lines = content.decode(encoding='utf-8').split('\n')
                            for cidr in content_lines:
                                if cidr:
                                    output_file.write(cidr + '\n')
    # 處理完成後刪除壓縮檔
    try:
        os.remove(tar_gz_path)
    except:
        pass

if __name__ == "__main__":
    # 定義下載連結
    IPv4_file_url = 'https://www.ipdeny.com/ipblocks/data/countries/all-zones.tar.gz'
    IPv6_file_url = 'https://www.ipdeny.com/ipv6/ipaddresses/blocks/ipv6-all-zones.tar.gz'
    
    # 處理 IPv4 資料
    print('>> 開始下載 IPv4 國家 IP 資料庫...')
    ipv4_file_path = download_file(IPv4_file_url, "ipv4.tar.gz")
    print('>> 解析 IPv4 國家 IP 資料庫...')
    process_cidr_excluding_tw(ipv4_file_path, 'ipv4_excluding_tw.txt', 4)
    
    # 處理 IPv6 資料
    print('>> 開始下載 IPv6 國家 IP 資料庫...')
    ipv6_file_path = download_file(IPv6_file_url, "ipv6.tar.gz")
    print('>> 解析 IPv6 國家 IP 資料庫...')
    process_cidr_excluding_tw(ipv6_file_path, 'ipv6_excluding_tw.txt', 6)
    
    print('>> 完成！結果已儲存到 ipv4_excluding_tw.txt 和 ipv6_excluding_tw.txt 中。')
