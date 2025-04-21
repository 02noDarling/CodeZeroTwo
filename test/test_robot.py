import time

import requests
import json

# 修改成自己的api key和secret key
API_KEY = "FAClUPFPOXbUeRenNHNeCV1y"
SECRET_KEY = "qhNhYWCCcphILktjbeQKziHkHcJddTI6"


def main():
    url = "https://aip.baidubce.com/rpc/2.0/ai_custom/v1/wenxinworkshop/chat/eb-instant?access_token=" + get_access_token()
    while (1):
        s = input()
        # 注意message必须是奇数条
        payload = json.dumps({
            "messages": [
                {
                    "role": "user",
                    "content": s
                }
            ]
        })
        headers = {
            'Content-Type': 'application/json'
        }

        res = requests.request("POST", url, headers=headers, data=payload).json()
        if 'result' in res:
            # 使用time.sleep来模拟打字效果，逐行打印回答
            for line in res['result'].split('\n'):
                print(line, end='')
                time.sleep(0.2)  # 每行之间暂停0.2秒
            print()  # 打印换行符，开始新的一行


def get_access_token():
    """
    使用 AK，SK 生成鉴权签名（Access Token）
    :return: access_token，或是None(如果错误)
    """
    url = "https://aip.baidubce.com/oauth/2.0/token"
    params = {"grant_type": "client_credentials", "client_id": API_KEY, "client_secret": SECRET_KEY}
    return str(requests.post(url, params=params).json().get("access_token"))


if __name__ == '__main__':
    main()