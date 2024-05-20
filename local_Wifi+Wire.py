# -*- coding: utf-8 -*-
import socket
import time
import psutil
import requests


def get_ip_list():
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
    arg["device"] = 1
    res = requests.get(
        'http://192.168.200.2:801/eportal/?c=Portal&a=login&callback=dr1003&login_method=1&user_account=%2C{device}%2C{account}%40{operator}&user_password={password}&wlan_user_ip={ip}&wlan_user_ipv6=&wlan_user_mac=000000000000&wlan_ac_ip=&wlan_ac_name='.format_map(
            arg))
    if '"msg":""' in res.text:
        print('当前设备已登录')
        return
    elif r'\u8ba4\u8bc1\u6210\u529f' in res.text:
        print('登录成功')
        return
    elif 'dXNlcmlkIGVycm9yMQ' in res.text:
        print('用户名出错')
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
    info = requests.get(
        'http://192.168.200.2:801/eportal/?c=Portal&a=unbind_mac&callback=dr1002&user_account={account}%40cmcc&wlan_user_mac=000000000000&wlan_user_ip={ip}'.format_map(
            arg))
    print(info,type(info))
    if(info == [200]):
        print("注销成功")

data = {"account": "1674373",  # 账号
        "password": "bAr8426G",  # 密码
        "operator": "cmcc"}  # 运营商  默认移动cmcc   电信telecom  联通unicom

if __name__ == '__main__':
    res = get_ip_list()
    for i in res:
        if i[0] == 'WLAN':  # 无线网卡的名称
            fake_ip = i[1]
        if i[0] == '以太网':  # 有线网卡的名称
            true_ip = i[1]
    logout(data, getip())
    time.sleep(3)
    login(data, fake_ip)
    time.sleep(3)
    login(data, true_ip)