import json  # 解析服务器数据，修改格式串
import random  # 生成随机数模块，生成随机体温
import re
import time  # 获取时间模块，可能需考虑时区
from io import BytesIO

import requests  # 爬虫模块，本程序的根本
from lxml import etree  # from…import   * 爬虫？还是数据解析来着，忘记了
from PIL import Image
from requests.packages.urllib3.exceptions import \
    InsecureRequestWarning  # 最后一行用于修复代理的问题，如果没有会报错。

dict_text = []    # 创建一个空字典用于存储推送内容
dict_state = []
classnums = ['学号1', '学号2', '学号3']  # 填写学号
passages = [('密码1'), ('密码2'), ('密码3')]
sckey = "sckey"  # Server酱推送提醒，需要填写sckey，官网：https://sct.ftqq.com/sendkey
# 由于云服务器时间有问题，所有在这里进行修正。具体根据服务器确定
now = int(time.time())
timeArray = time.localtime(now)   # 转换为其他日期格式,如:"%Y-%m-%d %H:%M:%S"

def rands():   # 随机数模块，实现范围内的随机体温，不建议修改此项
    temp = '{:.1f}'.format(random.uniform(35.9, 36.4))
    print("填报体温为:" + temp)
    return temp    # 相当于 赋值temp=rands（）

def pr1(n):    # 打印函数，实现输出打印内容的同时追加字典
    get_dict0 = n
    get_dict1 = "##### " + n
    print(get_dict0)
    dict_text.append(get_dict1)

def pushwechat(param):    # 推送函数
    scurl = f"https://sctapi.ftqq.com/{sckey}.send"
    requests.post(scurl, params=param)

def 验证码识别(value):
    im = Image.open(BytesIO(value)) # 将bytes数据转为图片
    pix = im.load()
    # 数字 0-9 对应二值化编码
    numbers =[
        "111000000011111110000000000011111001111111001111001111111110011100111111111001110011111111100111100111111100111110000000000011111110000000111111",
        "111111111111111110011111111001111001111111100111000111111110011100000000000001110000000000000111111111111110011111111111111001111111111111100111",
        "100111111100011100111111100001110011111100100111001111100110011100111100111001110011100111100111100000111110011111000111111001111111111111111111",
        "100111111100111100111001111001110011100111100111001110011110011100111001111001110011000011000111100001000000111110001110000111111111111111111111",
        "111111110011111111111100001111111111000000111111111000110011111110001111001111110000000000000111000000000000011111111111001111111111111100111111",
        "000000011100111100000001111001110011100111100111001110011110011100111001111001110011110011000111001111000000111100111110000111111111111111111111",
        "111100000011111111000000000011111000110011001111001110011110011100111001111001110011100111100111001110001100011110011100000011111111111000011111",
        "111111111111111100111111111111110011111111100111001111111000011100111110000111110011100011111111001100111111111100000111111111110001111111111111",
        "111111110001111110000110000011110000000011000111001100011110011100111001111001110011100011100111000000001100011110001110000011111111111100011111",
        "110000111111111110000001110011110001100011100111001111001110011100111100111001110011110011100111100110011000111110000000000111111110000001111111"
    ]
    captcha = ""
    num = 0
    while num <4:
        i = 13*num+7
        ldString = ""
        # 获取图片中所有数字的二值化编码
        while i < 13*num+7+9:
            j = 3
            while j<19:
                pixel = pix[i,j]
                ldString = ldString + str((+(pixel[0] * 0.3 + pixel[1] * 0.59 + pixel[2] * 0.11 >= 128)))
                j +=1
            i+=1
        comLen = []
        # 获取编码对应数字
        for i in range (len(numbers)):
            temp = 0
            for j in range(len(numbers[i])):
                if numbers[i][j]==ldString[j]:
                    temp +=1
            comLen.append(temp)
        captcha += str(comLen.index(max(comLen)))
        num +=1
    print("二值化识别验证码"+captcha)
    return captcha

def getCap(session):  # 获取验证码
    url = 'https://web-vpn.sues.edu.cn/https/77726476706e69737468656265737421f3f652d234256d43300d8db9d6562d/cas/captcha.jpg?vpn-1'
    resp = session.get(url=url)
    return 验证码识别(resp.content)

def login(session, execution, Num, Pwd):
    # 第二步：模拟登入网页VPN
    url2 = ("https://web-vpn.sues.edu.cn/https/77726476706e69737468656265737421f3f652d234256d43300d8db9d6562d/cas/"
            "login?service=https%3A%2F%2Fweb-vpn.sues.edu.cn%2Flogin%3Fcas_login%3Dtrue")
    headers2 = {
        "User-Agent": ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) C"
                       "hrome/91.0.4472.164 Safari/537.36 Edg/91.0.864.71"),
        "Referer": (
            "https://web-vpn.sues.edu.cn/https/77726476706e69737468656265737421f3f652d234256d43300d8db9d6562d/cas/"
            "login?service=https%3A%2F%2Fweb-vpn.sues.edu.cn%2Flogin%3Fcas_login%3Dtrue")
    }

    cap = getCap(session)
    # print("验证码为" + str(cap))
    data2 = {
        "username": Num,
        "password": Pwd,
        "execution": execution,  # 登录参数，没有这个参数会登录失败
        "encrypted": "true",
        "_eventId": "submit",
        "loginType": "1",  # 登录类型，对于本科生1就好
        "submit": "登 录",
        "authcode": cap,
    }
    requests.packages.urllib3.disable_warnings(
        InsecureRequestWarning)  # 用于修复证书安全校验
    z2 = session.post(url=url2, headers=headers2, data=data2,
                      verify=False, timeout=(3, 7))
    print("登陆成功")

def tianbao():
    time_tbsj = time.strftime("%Y-%m-%d %H:%M", timeArray)  # 输出：年-月-日，小时：分钟
    n = "今天是" + time_tbsj
    pr1(n)  # 追加内容，日期

    requests.DEFAULT_RETRIES = 5
    s = requests.session()
    s.keep_alive = False

    for i in range(0, len(classnums), 1):    # 根据用户数自动选择循环次数
        classnum = classnums[i]
        passage = passages[i]
        get_dict = {
            'username': classnum,
            'password': passage
        }
        n = "===========正在填报" + get_dict['username'] + "同学的体温==========="
        pr1(n)
        tem_tj = rands()  # 要提交的体温值

        # 第一步：获取一个关键值execution，供登陆时使
        url1 = ("https://web-vpn.sues.edu.cn/https/77726476706e69737468656265737421f3f652d234256d43300d8db9d6562d/cas/"
                "login?service=https%3A%2F%2Fweb-vpn.sues.edu.cn%2Flogin%3Fcas_login%3Dtrue")  # 登录网址  # 代码过长用（）连接
        z1 = requests.get(url1)
        z1.encoding = 'utf-8'
        content = etree.HTML(z1.text)  # 便于使用下面的Xpath
        execution = content.xpath('//input[@name="execution"]/@value')[0] # 用于登陆

        # 第二步：模拟登入网页VPN
        session = requests.session()  # 保持登录操作，懒得使用cookie了
        login(session, execution,get_dict['username'], get_dict['password'])
           
        # 获取效验码
        url3 = ("https://web-vpn.sues.edu.cn/https/77726476706e69737468656265737421e7f8539"
                "7213c6747301b9ca98b1b26312700d3d1/default/work/shgcd/jkxxcj/jkxxcj.jsp")
        z3 = session.post(url=url3, verify=False, timeout=(3, 7))
        searched = re.search(r'(?<=verification-code":").*(?="})', z3.text)
        verifyCode = searched.group() # 用于提交体温

        # 第四步 获取变量数据（提交时间）同时判断当前时段
        time_tjsj1 = time.strftime("%Y-%m-%d %H:%M", timeArray)   #
        time_tjsj0 = time.strftime("%Y-%m-%d", timeArray)
        tjsj1 = time.strftime("%H", timeArray)
        print("time_tjsj1：现在是" + time_tjsj1)
        # print("time_tjsj0：今天是" + time_tjsj0)
        # print("tjsj1：当前为" + tjsj1 + "时")
        if int(tjsj1) > 11:
            sd = "下午"
        else:
            sd = "上午"
        print("当前时段为：" + sd)  # 获得时间的KET并打印time_key判断是否正确
        time_key = time.strftime("%Y-%m-%d %H:%M", timeArray)

        #  第五步 获得ID参数等值（同第二步）
        time.sleep(2)
        url5 = ("https://web-vpn.sues.edu.cn/https/77726476706e69737468656265737421e7f85397213c6747301b9ca98b1b263127"
                "00d3d1/default/work/shgcd/jkxxcj/com.sudytech.work.shgcd.jkxxcj.jkxxcj.queryNear.biz.ext?vpn-12-o2-"
                "workflow.sues.edu.cn")  # 很重要，通过这个界面获得ID等参数
        headers5 = {
            "User-Agent": ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) C"
                           "hrome/91.0.4472.164 Safari/537.36 Edg/91.0.864.71"),
            "Referer": ("https://web-vpn.sues.edu.cn/https/77726476706e69737468656265737421e7f85397213c6747301b9ca98b1b"
                        "26312700d3d1/default/work/shgcd/jkxxcj/jkxxcj.jsp"),
            "Content-Type": "text/json",
        }
        z5 = session.post(url=url5, headers=headers5, verify=False,
                          timeout=(3, 7))  # data=json.dumps(data5),

        j5 = z5.json()
        # 解析服务器数据，提取有用的值
        ID = j5["resultData"][0]['ID']
        SQRID = j5["resultData"][0]['SQRID']
        SQBMID = j5["resultData"][0]['SQBMID']
        RYSF = j5["resultData"][0]['RYSF']
        SQRMC = j5["resultData"][0]['SQRMC']
        SFZH = j5["resultData"][0]['SFZH']
        SQBMMC = j5["resultData"][0]['SQBMMC']
        XB = j5["resultData"][0]['XB']
        LXDH = j5["resultData"][0]['LXDH']
        NL = j5["resultData"][0]['NL']
        XRYWZ = j5["resultData"][0]['XRYWZ']
        XQ = j5["resultData"][0]['XQ']
        SHENG = j5["resultData"][0]['SHENG']
        SHI = j5["resultData"][0]['SHI']
        QU = j5["resultData"][0]['QU']
        JTDZINPUT = j5["resultData"][0]['JTDZINPUT']
        JKZK = j5["resultData"][0]['JKZK']
        JKQK = j5["resultData"][0]['JKQK']
        print(get_dict['username'] + "同学的当前填报的唯一ID是：" + str(ID))  # 用于调试程序

        # 第六步 发送体温包（同第二步）
        url6 = ("https://web-vpn.sues.edu.cn/https/77726476706e69737468656265737421e7f85397213c6747301b9ca98b1b26312700d3"
                "d1/default/work/shgcd/jkxxcj/com.sudytech.work.shgcd.jkxxcj.jkxxcj.saveOrUpdate.biz.ext?vpn-12-o"
                "2-workflow.sues.edu.cn")
        headers6 = {
            "User-Agent": "Mozilla/5.0 (Linux; Android 6.0.1; Moto G (4)) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.69 Mobile Safari/537.36",
            "referer": "https://web-vpn.sues.edu.cn/https/77726476706e69737468656265737421e7f85397213c6747301b9ca98b1b26312700d3d1/default/work/shgcd/jkxxcj/jkxxcj.jsp",
            "Content-Type": "text/json",
            "verification-code": verifyCode
        }
        # 构造数据包
        data6 = {
            "params": {
                "id": ID,
                "sqrid": SQRID,
                "sqbmid": SQBMID,
                "rysf": RYSF,
                "sqrmc": SQRMC,
                "gh": get_dict['username'],
                "sfzh": SFZH,
                "sqbmmc": SQBMMC,
                "xb": XB,
                "lxdh": LXDH,
                "nl": NL,
                "tjsj": time_tjsj1,
                "xrywz": XRYWZ,
                "xq": XQ,
                "sheng": SHENG,
                "shi": SHI,
                "qu": QU,
                "jtdzinput": JTDZINPUT,
                "gj": "",
                "jtgj": "",
                "jkzk": JKZK,
                "jkqk": JKQK,
                "tw": tem_tj,
                "sd": sd,
                "bz": "",
                "_ext": "{}"
            }
        }

        z6 = session.post(url=url6, headers=headers6, data=json.dumps(
            data6), verify=False, timeout=(3, 7))
        # 判断体温是否填报成功
        if z6.text == "{\"result\":{\"code\":\"\",\"errorcode\":\"0\",\"msg\":\"\",\"success\":true}}":  # 小变动，code不含200
            n = get_dict['username'] + "体温填写成功，今天填报的体温是" + str(tem_tj) + "摄氏度。"
            dict_state.append('1')
            pr1(n)
            print("===========" + get_dict['username']+"的体温填报完成===========")
        else:
            n = get_dict['username'] + "填写失败，请手动填报"
            dict_state.append('0')
            pr1(n)
        time.sleep(5)

    print("体温填报结束，按回车退出\n\n\n")
    print("以下是推送文章的内容\n" + str(dict_text))
    b = ""
    for add in dict_text:
        Vsuccess = dict_state.count('1')
        Vfailed = dict_state.count('0')
        b = b + str(add) + "\n\n"
    print("b是：" + b)

    param = {
        'title': '体温填报 成功:' + str(Vsuccess) + ',失败:' + str(Vfailed),  # 推送标题
        'desp': b  # 推送内容
    }
    pushwechat(param)
    return

def main(fail_num):  # 体温填报的函数入口 上云的时候使用
    
    fail_num += 1
    if fail_num <= 3:
        try:
            tianbao()
            return fail_num, True
        except:
            print("出现错误，正在进行第"+str(fail_num)+"次重试")
            return fail_num, False
    # 错误推送
    print("体温填报出现异常，请手动填报")
    param = {
        'title': '体温填报出现异常，请手动填报',  # 推送标题
        'desp': '体温填报出现异常，请手动填报'  # 推送内容
    }
    pushwechat(param)
    return fail_num, False


if __name__ == '__main__':
    fail_num = 0
    valid = False
    while (not valid) and (fail_num < 4):
        fail_num, valid = main(fail_num)




