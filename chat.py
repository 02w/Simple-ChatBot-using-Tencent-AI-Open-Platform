import requests
import random
import string
from os import remove
from time import time
from base64 import b64decode
from urllib.parse import quote
from hashlib import md5
from pygame import mixer


def getParamWithSign(params, appkey):
    ''' 开放平台鉴权 '''
    raw = ""
    for key in sorted(params):
        if params[key] != "":
            raw = raw + key + "=" + quote(params[key]) + "&"
    raw = raw + "AppKey=" + appkey
    sign = md5(raw.encode("UTF-8"))
    params["sign"] = sign.hexdigest().upper()
    return params


def chat():
    ''' 调用智能闲聊API，返回（问题，答案）组'''
    appkey = "your AppKey"
    appid = "your AppId"
    quest = input("我: ")
    nonce = ''.join(random.sample(string.ascii_letters + string.digits, 10))
    param_before = {
        "app_id": appid,
        "time_stamp": str(int(time())),
        "nonce_str": nonce,
        "sign": "",
        "session": "10000",
        "question": quest.encode("utf-8")
    }

    param = getParamWithSign(param_before, appkey)
    API_ROOT = "https://api.ai.qq.com/fcgi-bin/nlp/nlp_textchat"
    resp = requests.post(API_ROOT, data=param)
    ans = resp.json()["data"]["answer"]
    return (quest, ans)


def getVoice(content):
    ''' 将回复作为内容调用语音合成API '''
    content = content.encode("utf-8")
    appkey = "your AppKey"
    appid = "your AppId"
    nonce = ''.join(random.sample(string.ascii_letters + string.digits, 10))
    param_before = {
        "app_id": appid,
        "time_stamp": str(int(time())),
        "nonce_str": nonce,
        "sign": "",
        "speaker": "5",
        "format": "3",
        "volume": "0",
        "speed": "80",
        "text": content,
        "aht": "0",
        "apc": "58"
    }
    param = getParamWithSign(param_before, appkey)
    API_ROOT = "https://api.ai.qq.com/fcgi-bin/aai/aai_tts"
    resp = requests.post(API_ROOT, data=param)
    ans = resp.json()["data"]["speech"]
    voice = b64decode(ans)        # 将base64编码转存为MP3
    file = open("temp.mp3", "wb")
    file.write(voice)
    file.close()
    return "temp.mp3"


def playMP3(address):
    ''' 利用pygame播放MP3 '''
    mixer.init()
    file = open(address)
    mixer.music.load(file)
    mixer.music.play()
    while mixer.music.get_busy():
        pass
    mixer.music.stop()
    mixer.quit()
    file.close()
    remove(address) # 播放完毕，删除音频文件


if __name__ == "__main__":
    while True:
        ans = chat()
        print(ans[1])
        voiceFile = getVoice(ans[1])
        playMP3(voiceFile)
        if ans[0] == "再见":   # 输入中文 “再见” 结束
            break
