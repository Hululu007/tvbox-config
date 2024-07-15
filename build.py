import re
import datetime
import requests
import json
import urllib3
import os
from tqdm import tqdm
from Crypto.Cipher import AES
import base64

def create_directory(path):
    if not os.path.exists(path): 
        os.makedirs(path)

# 定义颜色
class TqdmColored(tqdm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.bar_format = '{l_bar}%s{bar}%s{r_bar}' % ('\x1b[47m\x1b[32m', '\x1b[0m')  # \x1b[32m 为绿色

def get_json(url):
    key = url.split(";")[2] if ";" in url else ""
    url = url.split(";")[0] if ";" in url else url
    data = get_data(url)
    if not data:
        raise Exception()
    if is_valid_json(data):
        return data
    if "**" in data:
        data = base64_decode(data)
    if data.startswith("2423"):
        data = cbc_decrypt(data)
    if key:
        data = ecb_decrypt(data, key)
    return data
    
def get_ext(ext):
    try:
        return base64_decode(get_data(ext[4:]))
    except Exception:
        return ""

def get_data(url):
    if url.startswith("http"):
        urlReq = requests.get(url, verify=False)
        return urlReq.text
    return ""

def ecb_decrypt(data, key):
    spec = AES.new(pad_end(key).encode(), AES.MODE_ECB)
    return spec.decrypt(bytes.fromhex(data)).decode("utf-8")

def cbc_decrypt(data):
    decode = bytes.fromhex(data).decode().lower()
    key = pad_end(decode[decode.index("$#") + 2:decode.index("#$")])
    iv = pad_end(decode[-13:])
    key_spec = AES.new(key.encode(), AES.MODE_CBC, iv.encode())
    data = data[data.index("2324") + 4:-26]
    decrypt_data = key_spec.decrypt(bytes.fromhex(data))
    return decrypt_data.decode("utf-8")

def base64_decode(data):
    extract = extract_base64(data)
    return base64.b64decode(extract).decode("utf-8") if extract else data

def extract_base64(data):
    match = re.search(r"[A-Za-z0-9]{8}\*\*", data)
    return data[data.index(match.group()) + 10:] if match else ""

def pad_end(key):
    return key + "0000000000000000"[:16 - len(key)]

def is_valid_json(json_str):
    try:
        json.loads(json_str)
        return True
    except json.JSONDecodeError:
        return False

#  main
def main():
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

    with open('./url.json', 'r', encoding='utf-8') as f:
        urlJson = json.load(f)

    reList = ["https://ghproxy.net/https://raw.githubusercontent.com", "https://raw.kkgithub.com",
            "https://gcore.jsdelivr.net/gh", "https://mirror.ghproxy.com/https://raw.githubusercontent.com",
            "https://github.moeyy.xyz/https://raw.githubusercontent.com", "https://fastly.jsdelivr.net/gh",""]

    with TqdmColored(total= len(urlJson), desc="Build file") as bar:
        for item in urlJson:
            jsonStr = get_json(item["url"])
            for reI in range(len(reList)):
                create_directory('./tv/' + str(reI))
                urlName = item["name"]
                urlPath = item["path"]
                reqText = jsonStr
                if urlName != "gaotianliuyun_0707":
                    reqText = reqText.replace("'./", "'" + urlPath) \
                        .replace('"./', '"' + urlPath)
                if reList[reI] != '':
                    if reList[reI].find('jsdelivr') > 0:
                        reqText = reqText.replace("/raw/", "@")
                    else:
                        reqText = reqText.replace("/raw/", "/")
                        reqText = reqText.replace("'https://github.com", "'" + reList[reI]) \
                        .replace('"https://github.com', '"' + reList[reI]) \
                        .replace("'https://raw.githubusercontent.com", "'" + reList[reI]) \
                        .replace('"https://raw.githubusercontent.com', '"' + reList[reI])
                fp = open("./tv/" + str(reI) + "/" + urlName + ".json", "w+", encoding='utf-8')
                fp.write(reqText)
            bar.update(1) 

    now = datetime.datetime.now()
    fp = open('README.md', "w+", encoding='utf-8')
    fp.write("# 提示\n\n")
    fp.write("该项目Fork自: [https://github.com/hl128k/tvbox](https://github.com/hl128k/tvbox)\n\n")
    fp.write("如果有收录您的配置，您也不希望被收录请[issues](https://github.com/huxuanming/tvbox-config/issues)，必将第一时间移除\n\n")
    fp.write("如果有好的地址配置需要镜像化请提交[issues](https://github.com/huxuanming/tvbox-config/issues)\n\n")
    fp.write("本人不对任何数据源负责，任何情况问题请自行负责，请勿以任何形式进行传播\n\n")
    fp.write("# TvBox 配置\n\n")
    fp.write("本页面只是收集Box，自用请勿宣传\n\n")
    fp.write("所有资源全部搜集于网络，不保证可用性\n\n")
    fp.write("因电视对GitHub访问问题，所以将配置中的GitHub换成镜像源\n\n")
    fp.write("本次更新时间为：" + now.strftime("%Y-%m-%d %H:%M:%S") + "\n\n")
    fp.write("更新仅为自动更新，实际更新情况请以原始路径为准，内容参考url.json\n\n")
    fp.write(
        "如果有必要手动输入建议使用短链如：[http://gg.gg/](http://gg.gg/)，[https://suowo.cn/](https://suowo.cn/)，[https://dlj.li/](https://dlj.li/) 等\n\n")
    fp.write("删除列表，请复制项目后自行对tv目录下的数字目录内的文件进行镜像使用\n\n")
    fp.close()

main()