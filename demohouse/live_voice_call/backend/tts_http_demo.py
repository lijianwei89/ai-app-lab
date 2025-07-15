#coding=utf-8

'''
requires Python 3.6 or later
pip install requests
'''
import base64
import json
import uuid
import requests

# 填写平台申请的appid, access_token，cluster以及voice_type
appid = "3735242956"
access_token= "WDubf8FD7TunKdtBdzMnmLRuEzvximVu"
cluster = "volcano_icl"
voice_type = "S_pic297Bs1"


host = "openspeech.bytedance.com"
api_url = f"https://openspeech.bytedance.com/api/v1/tts"

header = {"Authorization": f"Bearer;{access_token}"}

request_json = {
    "app": {
        "appid": appid,
        "token": "access_token",
        "cluster": cluster
    },
    "user": {
        "uid": "388808087185088"
    },
    "audio": {
        "voice_type": voice_type,
        "encoding": "mp3",
        "speed_ratio": 1.0,
        "volume_ratio": 1.0,
        "pitch_ratio": 1.0,
    },
    "request": {
        "reqid": str(uuid.uuid4()),
        "text": "您好，这里是小波老师，今天我给大家讲一个故事。故事的名字叫做《小红帽》。从前有一个小女孩，她的名字叫小红帽。小红帽的妈妈给她做了一顶红色的小斗篷，所以大家都叫她小红帽。小红帽有一天要去奶奶家，路上遇到了大灰狼。大灰狼想吃掉小红帽，但是小红帽机智地逃脱了。最后，小红帽安全地到达了奶奶家。",
        "text_type": "plain",
        "operation": "query",
        "with_frontend": 1,
        "frontend_type": "unitTson"

    }
}

if __name__ == '__main__':
    try:
        resp = requests.post(api_url, json.dumps(request_json), headers=header)
        print(f"resp body: \n{resp.json()}")
        if "data" in resp.json():
            data = resp.json()["data"]
            file_to_save = open("test_submit.mp3", "wb")
            file_to_save.write(base64.b64decode(data))
    except Exception as e:
        e.with_traceback()
