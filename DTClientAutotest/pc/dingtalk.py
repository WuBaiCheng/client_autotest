import os
import subprocess
import time
from .core import system, get_uuid
import re
from .. import global_var

def launch_dingtalk(beta=False, open_cef_port=True):
    '''
    启动标准钉进程
    :param beta: beta仅对win生效，表示是否启动beta版的标准钉，默认为False、启动非beta版的标准钉
    :param open_cef_port: 是否开启CEF(Chromium Embedded Framework)远程调试端口，默认开启；开启后可以对CEF pages进行web自动化测试，mac只支持x86架构的钉钉包
    :return:
    '''

    if 'win' == system():
        if beta:
            if open_cef_port:
                os.system('start "" "C:\Program Files (x86)\DingDingBeta\DingtalkLauncher.exe" --remote-debugging-port=16888')
            else:
                os.startfile('C:\\Program Files (x86)\\DingDingBeta\\DingtalkLauncher.exe')
        else:
            if open_cef_port:
                if os.path.exists('C:\Program Files (x86)\DingDing\main\current_new\DingTalk.exe'):
                    os.system('start "" "C:\Program Files (x86)\DingDing\main\current_new\DingTalk.exe" --remote-debugging-port=16888')
                else:
                    os.system('start "" "C:\Program Files (x86)\DingDing\main\current\DingTalk.exe" --remote-debugging-port=16888')
            else:
                os.startfile('C:\\Program Files (x86)\\DingDing\\DingtalkLauncher.exe')
    elif 'mac' == system():
        if open_cef_port:
            # 脱离主程序的控制
            process = subprocess.Popen(['/Applications/DingTalk.app/Contents/MacOS/DingTalk', '--remote-debugging-port=16889'])
            # 使用AppleScript将钉钉窗口置顶
            # 下面这段在pytest case里还是概率性无法将钉钉窗口置顶，而单独放在py的main函数里执行又可以将钉钉窗口置顶，不知道为什么
            # while True:
            #     if not subprocess.call(['osascript', '-e', 'tell application "System Events" to set frontmost of process "DingTalk" to true']):
            #         break
            # 改用这个方式将钉钉窗口置顶
            for i in range(2):
                subprocess.call(['osascript', '-e', f'tell application "System Events" to set frontmost of (every process whose unix id is {process.pid}) to true'])
                if 0 == i:
                    time.sleep(1)
        else:
            os.system('open /Applications/DingTalk.app')

def kill_dingtalk():
    '''
    杀掉钉钉进程
    :return:
    '''

    if 'win' == system():
        # win端标准钉
        os.system("taskkill -f -im DingTalk.exe")
        if get_uuid() not in global_var.skip_aliding_uuids:
            # win端阿里钉
            os.system("taskkill -f -im iDingTalk.exe")
        # win端beta版标准钉
        os.system("taskkill -f -im DingTalkBeta.exe")
        # win端可能拉起的更新进程
        os.system("taskkill -f -im DingTalkUpdater.exe")
    elif 'mac' == system():
        if get_uuid() in global_var.skip_aliding_uuids:
            with os.popen('ps aux | grep DingTalk.app') as p:
                read_str = p.read()
                str_list = read_str.split('\n')
                for _str in str_list:
                    if '/Applications/DingTalk.app/' in _str:
                        re_list = re.findall(r' (\d+) ', _str)
                        pid = re_list[0]
                        os.system('kill ' + pid)
        else:
            os.system('killall DingTalk')

def get_dingtalk_version(beta=False):
    '''
    获取钉钉版本信息
    :param beta: 是否是beta包
    :return: 钉钉版本信息 {'version':'xxx', 'buildNo':'xxx'}
    '''

    version_dict = {}
    if 'mac' == system():
        with open('/Applications/DingTalk.app/Contents/Info.plist', 'r', encoding='utf-8') as h1:
            read_str = h1.read()
            str_list = read_str.split('\n')
            i = 0
            for _str in str_list:
                if 'CFBundleShortVersionString' in _str:
                    version_dict['version'] = re.findall(r"<string>(.+)</string>", str_list[i+1])[0]
                elif 'CFBundleVersion' in _str:
                    version_dict['buildNo'] = re.findall(r"<string>(.+)</string>", str_list[i+1])[0]
                i = i + 1
    elif 'win' == system():
        staticconfig_xml_path = ''
        if beta:
            staticconfig_xml_path = 'C:\\Program Files (x86)\\DingDingBeta\\main\\current\\configurations\\staticconfig.xml'
        else:
            staticconfig_xml_path = 'C:\\Program Files (x86)\\DingDing\\main\\current\\configurations\\staticconfig.xml'
        with open(staticconfig_xml_path, 'r', encoding='utf-8') as h1:
            read_str = h1.read()
            str_list = read_str.split('\n')
            for _str in str_list:
                if 'VersionString' in _str:
                    version_str = re.findall(r'<item id="VersionString">(.+)</item>', _str)[0]
                    version_dict['version'] = version_str.split('-')[0]
                    version_dict['buildNo'] = version_str.split('-')[1]
    return version_dict