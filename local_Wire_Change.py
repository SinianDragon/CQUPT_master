# -*- coding: utf-8 -*-
import ctypes
import os
import random
import re
import socket
import sys
import time

import psutil
import requests


def get_ip():
    netcard_info = []
    info = psutil.net_if_addrs()
    for k, v in info.items():
        for item in v:
            if item[0] == 2 and not item[1] == '127.0.0.1':
                netcard_info.append((k, item[1]))
    return netcard_info


def getip():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(('8.8.8.8', 80))
        ip = s.getsockname()[0]
    finally:
        s.close()
    return ip


def login(arg, ip):
    arg["ip"] = ip
    arg["device"] = 0
    res = requests.get(
        'http://192.168.200.2:801/eportal/?c=Portal&a=login&callback=dr1003&login_method=1&user_account=%2C{device}%2C{account}%40{operator}&user_password={password}&wlan_user_ip={ip}&wlan_user_ipv6=&wlan_user_mac=000000000000&wlan_ac_ip=&wlan_ac_name='.format_map(
            arg))
    # print(res.text)
    if '"msg":""' in res.text:
        print('当前设备已登录')
        return
    elif 'dXNlcmlkIGVycm9yMQ' in res.text:
        print('用户名出错')
        return
    elif r'\u8ba4\u8bc1\u6210\u529f' in res.text:
        print('登录成功')
        return
    elif 'bGRhcCBhdXRoIGVycm9y' in res.text:
        print("密码错误")
        return
    elif 'aW51c2UsIGxvZ2luIGFnYWluL' in res.text:
        login(ip, arg)
    else:
        print("失败")


def logout(arg, ip):
    arg["ip"] = ip
    res = requests.get(
        'http://192.168.200.2:801/eportal/?c=Portal&a=unbind_mac&callback=dr1002&user_account={account}%40cmcc&wlan_user_mac=000000000000&wlan_user_ip={ip}'.format_map(
            arg))
    print(res.text)


class IpManage:
    def __init__(self):
        self.ip_list = self.scan()

    def set_ip(self, name, ip, mask="255.255.128.0", gateway="10.16.0.1"):
        command = f'''netsh interface ip set address name="{name}" static {ip} {mask} {gateway}'''
        runas = "runas /savecred /user:Administrator "
        print(command)
        process = os.popen(command)
        print(process.read())

    def set_DNS(self, name, dns="202.202.32.33"):
        command = f'''netsh interface ip set dns name="{name}" static {dns} register = primary'''
        runas = "runas /savecred /user:Administrator "
        print(command)
        process = os.popen(command)
        print(process.read())

    def set_ip_dhcp(self, name):
        command = f'''netsh interface ip set address name="{name}" source=dhcp'''
        runas = "runas /savecred /user:Administrator "
        print(command)
        process = os.popen(command)
        print(process.read())

    def set_dns_dhcp(self, name):
        command = f'''"netsh interface ip set dns name="{name}" source=dhcp'''
        runas = "runas /savecred /user:Administrator "
        print(command)
        process = os.popen(command)
        print(process.read())

    def scan(self):
        result = os.popen('ipconfig')
        res = result.read()
        resultlist = re.findall('''(?<=以太网适配器 ).*?(?=:)|(?<=无线局域网适配器 ).*?(?=:)''', res)
        print(resultlist)
        return resultlist

    def is_admin(self):
        try:
            return ctypes.windll.shell32.IsUserAnAdmin()
        except:
            return False


# 要修改的数据
data = {"account": "1674373",  # 账号
        "password": "bAr8426G",  # 密码
        "operator": "cmcc",  # 运营商  默认移动cmcc   电信telecom  联通unicom
        "Wireless": "WLAN",  # 无线网卡的名称
        "wired": ""  # 有线网卡的名称
        }
true_ip = ""
fake_ip = ""
res = get_ip()
for i in res:
    if i[0] == data["Wireless"]:
        fake_ip = i[1]
    if i[0] == data["wired"]:
        true_ip = i[1]
ip = true_ip
print(true_ip, fake_ip)
ip = ip.split(".")
ip[-1] = str((int(ip[-1]) + random.randint(1, 10)) % 255)
ip[-2] = str((int(ip[-2]) + random.randint(1, 10)) % 255)
ip = ".".join(ip)
print(fake_ip, true_ip)

if __name__ == '__main__':
    im = IpManage()
    if im.is_admin():
        logout(data, true_ip)
        time.sleep(2)
        # login(data, fake_ip)
        # time.sleep(3)  # 休眠3较好，看机器运行怎么样
        # login(data, true_ip)
        # time.sleep(3)
        card_id = im.ip_list.index(data["wired"])
        im.set_ip(im.ip_list[card_id], ip)
        im.set_DNS(im.ip_list[card_id])
        print(im.ip_list[card_id], " 静态IP设置完成！")
        login(data, ip)
        im.set_ip_dhcp(im.ip_list[card_id])
        im.set_dns_dhcp(im.ip_list[card_id])
        print(im.ip_list[card_id], " 动态IP设置完成！")
        time.sleep(6)
        ip = getip()
        login(data, ip)
        print(ip)
    else:
        ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, __file__, None, 1)