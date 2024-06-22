import pyautogui
from DTClientAutotest import pc, global_var
import global_var_project
import time
import pytest
import os
import json
import pyperclip
import re
import inspect
import requests
import oss2
from multiprocessing import Process, Pipe
from threading import Thread

def init_dtclientautotest():
    pyautogui.FAILSAFE = False
    # 全局相似度阈值
    global_var.threshold = 0.80
    # 项目根目录
    global_var.root_path = pc.get_path_by_dirname(__file__, 2)

def setup_module():
    '''
    当前py最先调用的函数，且只调用1次
    :return:
    '''

    init_dtclientautotest()

def write_log(content):
    log_path = os.path.join(pc.get_path_by_dirname(__file__, times=3), 'my_log.txt')
    pre_str = ''
    if os.path.exists(log_path):
        with open(log_path, 'r') as f:
            pre_str = f.read()
    with open(log_path, 'w') as f:
        f.write(pre_str + '\n' + content)

def case_info(**kws):
    '''
    装饰器，给case添加自定义属性，也可对加了该装饰器的case批量hook
    :param kws: 自定义属性列表
    :return: 装饰后的新函数
    '''

    def inner1(func):
        def inner2(self):

            func(self)

        # 给case添加自定义属性
        for item in kws.items():
            key = item[0]
            value = item[1]
            inner2.__annotations__[key] = value
        return inner2
    return inner1

class TestBase():
    '''
    测试基类
    '''

    def setup(self):
        '''
        每个case执行前执行的函数
        :return:
        '''

        pass

    def teardown(self):
        '''
        每个case执行后执行的函数
        :return:
        '''

        pass