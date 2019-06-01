import string
from os import remove
from time import time
from base64 import b64decode
from random import sample
from urllib.parse import quote
from requests import post
from hashlib import md5
from pygame import mixer


def getParamWithSign(param, appkey):
    ''' 开放平台接口鉴权 '''
    raw = ""
    for key in sorted(param):
        if param[key] != "":
            raw = raw + key + "=" + quote(param[key]) + "&"
    raw = raw + "app_key=" + appkey
    raw = raw.replace("%20", "+")    # 处理空格的urlencode
    sign = md5(raw.encode("utf-8"))
    param["sign"] = sign.hexdigest().upper()
    return param


def chat():
    ''' 调用智能闲聊API，返回（问题，答案）组 '''
    appkey = ""  # your AppKey
    appid = ""   # your AppId
    quest = input("我: ")
    nonce = "".join(sample(string.ascii_letters + string.digits, 10))
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
    resp = post(API_ROOT, data=param).json()

    ans = resp["data"]["answer"]
    if resp["ret"] != 0:          # API调用失败
        ans = "我不知道你在说什么"
    return (quest, ans)


def getVoice(content):
    ''' 将回复作为内容调用语音合成API '''
    content = content.encode("utf-8")
    appkey = ""  # your AppKey
    appid = ""   # your AppId
    nonce = "".join(sample(string.ascii_letters + string.digits, 10))
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
    resp = post(API_ROOT, data=param).json()

    if resp["ret"] != 0:   # API调用失败
        return False

    ans = resp["data"]["speech"]
    voice = b64decode(ans)            # 将base64编码转存为MP3
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
    while mixer.music.get_busy():  # 等待播放完毕
        pass
    mixer.music.stop()
    mixer.quit()

    file.close()
    remove(address)   # 播放完毕，删除音频文件


if __name__ == "__main__":
    while True:
        ans = chat()
        print("AI: {}".format(ans[1]))
        voice = getVoice(ans[1])

        if not voice:
            print("AI: 啊，我不会读这句话啦")
        else:
            playMP3(voice)

        if ans[0] == "再见" or "拜拜" in ans[1]:    # 结束
            break
