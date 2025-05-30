#coding=utf-8

'''
requires Python 3.6 or later
pip install requests
'''
import base64
import json
import uuid
import requests

# 填写平台申请的appid, access_token以及cluster
appid = "1287599635"
access_token= "plZXZxn__u_AnDTpOuG7AUUQF-Rf-VFn"
cluster = "volcano_icl"

voice_type = "S_BmVRJq6t1"
host = "openspeech.bytedance.com"
api_url = f"https://{host}/api/v1/tts"

header = {"Authorization": f"Bearer;{access_token}"}
generate_text = """
清晨，我独自一人来到西湖边。空气中弥漫着淡淡的湿气，带着泥土和植物的清香，沁人心脾。湖面上笼罩着一层薄薄的雾气，如同一条轻柔的丝带，缓缓地飘动着，给西湖增添了一份神秘和朦胧。阳光透过雾气，洒在湖面上，泛起一片金色的光芒，如梦如幻。远处山峦在雾气中若隐若现，宛如一幅水墨画，充满了诗情画意。断桥在晨光中的倒影，呈现出一种独特的对称美，仿佛连接着过去和现在。我静静地站在桥上，感受着这份宁静和美好，心中涌起一种莫名的感动。这西湖的美，不仅仅在于它的景色，更在于它所蕴含的历史和文化，以及它所见证的无数人的人生故事。\n\n阳光渐渐洒落，我登上了一艘游船，开始游览西湖。湖面上波光粼粼，微风拂过脸颊，带来一丝清凉。看着湖边的景色，我不禁回忆起小时候和家人一起来西湖游玩的场景，心中涌起一股淡淡的怀旧之情。时间如流水般逝去，而西湖的美丽却依然如故。人生就像这湖水一样，不断地流逝，但我们可以在有限的时间里，创造出无限的价值，留下属于自己的回忆。\n\n傍晚时分，我来到了雷峰塔。夕阳的余晖洒在湖面上，将湖水染成一片金黄色。我坐在塔边的长椅上，静静地欣赏着雷峰夕照，感受着这份宁静和祥和。所有的烦恼和忧愁都仿佛被这美丽的景色所融化，我的心也随之平静下来。人生就像这夕阳一样，终将走向落幕，但我们可以在有限的时间里，留下属于自己的光芒，照亮他人的人生。\n\n冬日的一天，我再次来到西湖。雪后的断桥，银装素裹，宛如一条玉带横卧在湖面上。我站在桥上，看着这壮丽的景色，不禁发出赞叹之声。大自然的鬼斧神工，真是令人叹为观止。雪后的西湖，更加显得纯洁和美丽，也让我更加珍惜这份难得的美好。人生就像这雪花一样，虽然短暂，但却可以绽放出最美的光芒，给世界带来一份美好。\n\n夜晚，我来到了三潭印月。湖面上倒映着三个小石塔，月光如水，清澈明亮。我坐在湖边的亭子里，欣赏着这美丽的月色，心中充满了喜悦。这美丽的景色，让我感到无比的幸福和满足。人生就像这月亮一样，有阴晴圆缺，但只要我们保持一颗乐观的心，就能欣赏到最美的风景，找到属于自己的幸福。这西湖的月色，也让我明白了人生的真谛：珍惜当下，活在当下，勇敢追逐自己的梦想，才能感受到真正的幸福和实现自己的人生价值。而我的梦想，就是用我的文字，记录下这世间的美好，传递给更多的人，让更多的人感受到幸福和快乐。这西湖之行，不仅是一次美好的回忆，更是一次人生的洗礼，让我更加坚定了自己的梦想，也让我更加热爱这美好的世界。
"""
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
        "text": generate_text,
        "text_type": "plain",
        "operation": "query",
        "with_frontend": 1,
        "frontend_type": "unitTson"

    }
}

if __name__ == '__main__':
    try:
        resp = requests.post(api_url, json.dumps(request_json), headers=header)
        if "data" in resp.json():
            data = resp.json()["data"]
            file_to_save = open("test_submit.mp3", "wb")
            file_to_save.write(base64.b64decode(data))
            print("generate success!!")
    except Exception as e:
        e.with_traceback()
