import pyautogui
import time
from .. import global_var
import os
import platform
import uuid
from paddleocr import PaddleOCR
import cv2
import pyperclip
from enum import Enum
from pynput import mouse
import copy
import inspect
import hashlib
import socket
import re
from typing import List, Dict
import numpy as np

class Position(Enum):
    '''
    交互位置，枚举类型

    无论是OpenCV的图像模板匹配还是OCR的文字识别，最终是在一张大截图中识别出一块匹配区域（如下用一堆*星号模拟匹配区域），
    而对匹配区域进行诸如单击、双击等操作本质是在一个[x,y]坐标点进行交互，
    DTClientAutotest提供了匹配区域的9个可交互点，默认交互中心点Position.CENTER = [centerX,centerY]

    [left_topX,left_topY]*******************[mid_topX,mid_topY]*******************[right_topX,right_topY]
    *****************************************************************************************************
    *****************************************************************************************************
    *****************************************************************************************************
    *****************************************************************************************************
    *****************************************************************************************************
    [left_midX,left_midY]********************[centerX,centerY]********************[right_midX,right_midY]
    *****************************************************************************************************
    *****************************************************************************************************
    *****************************************************************************************************
    *****************************************************************************************************
    *****************************************************************************************************
    [left_bottomX,left_bottomY]**********[mid_bottomX,mid_bottomY]**********[right_bottomX,right_bottomY]
    '''

    CENTER = 0       # 中心
    LEFT_TOP = 1     # 左上
    MID_TOP = 2      # 中上
    RIGHT_TOP = 3    # 右上
    RIGHT_MID = 4    # 右中
    RIGHT_BOTTOM = 5 # 右下
    MID_BOTTOM = 6   # 中下
    LEFT_BOTTOM = 7  # 左下
    LEFT_MID = 8     # 左中

class ActMode(Enum):
    '''
    交互模式，枚举类型
    '''

    LEFT_CLICK = 0        # 左单击
    RIGHT_CLICK = 1       # 右单击
    DOUBLE_LEFT_CLICK = 2 # 左双击
    MOVE_ON = 3           # 移动到

class SortRule(Enum):
    '''
    模板匹配命中区排序规则，枚举类型
    '''

    THRESHOLD_REVERSE = 0 # 相似度倒序
    Y_X = 1               # 优先按左上点坐标的Y值进行正序排列，Y一样的情况下，再按X值进行正序排列

def get_path_by_dirname(path, times=1):
    '''
    对path循环times进行os.path.dirname操作
    :param path: 待操作的路径
    :param times: 循环os.path.dirname的次数
    :return: 处理后的路径
    '''

    for i in range(times):
        path = os.path.dirname(path)
    return path

def get_uuid():
    '''
    获取PC设备的唯一标识uuid，由框架生成，存储在用户根目录(~)下，名称为pc_uuid.txt
    :return: uuid
    '''

    user_root_path = os.path.expanduser('~')
    pc_uuid_path = os.path.join(user_root_path, 'pc_uuid.txt')
    if os.path.exists(pc_uuid_path):
        with open(pc_uuid_path, 'r', encoding='utf-8') as file:
            pc_uuid_str = file.read()
    else:
        pc_uuid_str = str(uuid.uuid4())
        with open(pc_uuid_path, 'w', encoding='utf-8') as file:
            file.write(pc_uuid_str)
    return pc_uuid_str

def get_local_ip():
    '''
    获取本机ip
    :return: 本机ip
    '''

    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(('8.8.8.8', 80))
        ip = s.getsockname()[0]
    except:
        ip = '127.0.0.1'
    finally:
        s.close()
    return ip

def system():
    '''
    获取PC设备的系统简称
    :return: win / mac
    '''

    system = platform.platform().lower()
    if 'win' in system:
        return 'win'
    elif 'mac' in system:
        return 'mac'
    assert 0, '新系统'

def architecture():
    '''
    获取mac芯片指令集架构
    :return: arm64 / x86
    '''

    system = platform.platform().lower()
    if 'mac' in system:
        if 'arm64' in system:
            return 'arm64'
        elif 'x86' in system:
            return 'x86'
    assert False, 'architecture()只适用于mac'

def move_mouse_to_edge():
    '''
    将鼠标移到角落（左上角），可以干掉 "可能存在的"鼠标UI对图像识别的微小干扰
    :return:
    '''

    pyautogui.FAILSAFE = False
    pyautogui.moveTo(0, 0)

def input_text(text):
    '''
    通过PC设备的剪切板完成文字的瞬间输入，支持中文的输入
    :param text: 要输入的文字
    :return:
    '''

    pyperclip.copy(text)
    if 'mac' == system():
        pyautogui.hotkey('command', 'v', interval=0.25)
    elif 'win' == system():
        pyautogui.hotkey('ctrl', 'v')

def screenshot(name=None, sub_path=None):
    '''
    对PC设备屏幕截图
    :param name: 截图文件名称，默认使用了时间戳避免重名 {time.time()}.png，形如 1681124591.739276.png
    :param sub_path: 截图文件存放路径，默认为 {global_var.root_path}/screenshot
    :return: 截图文件完整路径，形如 {global_var.root_path}/screenshot/1681124591.739276.png
    '''

    # 注意python参数的默认值只会被赋值1次，如果想动态变化，则需要写成None、内部判断
    if name is None:
        name = str(time.time()) + '_' + str(uuid.uuid4())

    if sub_path is None:
        sub_path = os.path.join(global_var.root_path, 'screenshot')
    # 创建文件夹
    os.makedirs(sub_path, exist_ok=True)

    full_path = os.path.join(sub_path, name + '.png')

    # start_time = time.time()
    # while not os.path.exists(full_path):
    #     pyautogui.screenshot(full_path)
    #     end_time = time.time()
    #     if end_time - start_time > 10:
    #         assert False, 'pyautogui截图失败'

    # 貌似上面这段检测截图是否存在的代码会受到录屏的影响
    pyautogui.screenshot(full_path)

    return full_path

def filter_letters_numbers_chinese_characters(origin_str):
    '''
    过滤出字母（大小写）、数字（阿拉伯）、汉字
    :param origin_str: 原始字符串
    :return: 过滤后的字符串
    '''

    return re.sub(r"[^A-Za-z0-9一-龥]", "", origin_str)

def exist_text(text, pic_full_path, equal_filter=False, preview=False, filter_special_chars=False):
    '''
    OCR识别一张图片中目标文字命中的所有区域
    :param text: 目标文字
    :param pic_full_path: 图片的完整路径
    :param equal_filter: 是否过滤出与目标文字完全相等的命中区域。比如当OCR识别出的ocr_text集合为['12abc34','2abc3','abc34']，目标文字text为'2abc3': 当equal_filter为False时，可以命中['12abc34','2abc3']；当equal_filter为True时，只能命中['2abc3']
    :param preview: 是否对目标文字的所有命中区域进行红色描边预览（用于开发脚本时的调试，实际脚本运行测试时要将preview改成False）
    :param filter_special_chars: 是否干掉 除了 "字母（大小写）、数字（阿拉伯）、汉字" 之外 的字符
    :return:
    [bool, # 目标文字是否有命中区域
        [ # 命中区域集合
            [ # 命中区域1
                [centerX,centerY],
                [left_topX,left_topY],
                [mid_topX,mid_topY],
                [right_topX,right_topY],
                [right_midX,right_midY],
                [right_bottomX,right_bottomY],
                [mid_bottomX,mid_bottomY],
                [left_bottomX,left_bottomY],
                [left_midX,left_midY],
                ocr_text # 区域内的具体文字
            ],
            [ # 命中区域2
                [centerX,centerY],
                [left_topX,left_topY],
                [mid_topX,mid_topY],
                [right_topX,right_topY],
                [right_midX,right_midY],
                [right_bottomX,right_bottomY],
                [mid_bottomX,mid_bottomY],
                [left_bottomX,left_bottomY],
                [left_midX,left_midY],
                ocr_text # 区域内的具体文字
            ],
            …… # 命中区域n
        ]
    ]

    [left_topX,left_topY]*******************[mid_topX,mid_topY]*******************[right_topX,right_topY]
    *****************************************************************************************************
    *****************************************************************************************************
    *****************************************************************************************************
    *****************************************************************************************************
    *****************************************************************************************************
    [left_midX,left_midY]********************[centerX,centerY]********************[right_midX,right_midY]
    *****************************************************************************************************
    *****************************************************************************************************
    *****************************************************************************************************
    *****************************************************************************************************
    *****************************************************************************************************
    [left_bottomX,left_bottomY]**********[mid_bottomX,mid_bottomY]**********[right_bottomX,right_bottomY]
    '''

    ocr = PaddleOCR(use_angle_cls=True, use_gpu=True)
    all_lines = ocr.ocr(pic_full_path)
    matched_lines = []
    for line in all_lines:
        if filter_special_chars:
            line[1] = (filter_letters_numbers_chinese_characters(line[1][0]), line[1][1])
        if equal_filter and text == line[1][0]:
            matched_lines.append(line)
        elif not equal_filter and text in line[1][0]:
            matched_lines.append(line)

    img = None
    if preview:
        img = cv2.imread(pic_full_path)

    final_lines = [] # [[[中心点X,中心点Y],[左上X,左上Y],[中上X,中上Y],……顺时针,ocr_text],[]]
    for line in matched_lines:
        final_line = [
            [(line[0][0][0] + line[0][2][0]) / 2, (line[0][0][1] + line[0][2][1]) / 2], # [中心点X,中心点Y]
            [line[0][0][0], line[0][0][1]],                                             # [左上X,左上Y]
            [(line[0][0][0] + line[0][2][0]) / 2, line[0][0][1]],                       # [中上X,中上Y]
            [line[0][1][0], line[0][1][1]],                                             # [右上X,右上Y]
            [line[0][1][0], (line[0][0][1] + line[0][2][1]) / 2],                       # [右中X,右中Y]
            [line[0][2][0], line[0][2][1]],                                             # [右下X,右下Y]
            [(line[0][0][0] + line[0][2][0]) / 2, line[0][2][1]],                       # [中下X,中下Y]
            [line[0][0][0], line[0][2][1]],                                             # [左下X,左下Y]
            [line[0][0][0], (line[0][0][1] + line[0][2][1]) / 2],                       # [左中X,左中Y]
            line[1][0] # ocr_text
        ]
        final_lines.append(final_line)

        if preview:
            cv2.rectangle(img, (int(final_line[1][0]), int(final_line[1][1])), (int(final_line[5][0]), int(final_line[5][1])), (0, 0, 255), 2)

    if preview:
        cv2.imshow('img', img)
        cv2.waitKey()
        cv2.destroyAllWindows()

    return [len(final_lines) > 0, final_lines]

screenshot_resolution = (0, 0)
def get_screenshot_resolution():
    '''
    获取PC设备屏幕截图的分辨率
    :return: 分辨率，形如 (2880, 1800)
    '''

    global screenshot_resolution
    if screenshot_resolution[0] == 0:
        pic_path = screenshot()
        img = cv2.imread(pic_path)
        screenshot_resolution = (img.shape[1], img.shape[0])
        os.remove(pic_path)
    return screenshot_resolution

def template_pic_full_name(name):
    '''
    将 模板截图简称 拼接成 模板截图全称（不含扩展类型）
    :param name: 模板截图简称
    :return: 模板截图全称（不含扩展类型），模板截图全称 = 模板截图简称_system()_屏幕截图分辨率宽x屏幕截图分辨率高，形如 name => {name}_mac_2880x1800
    '''

    return name + '_' + system() + '_' + str(get_screenshot_resolution()[0]) + 'x' + str(get_screenshot_resolution()[1])

def custom_sort(item):
    '''
    优先按y排序，y相同时按x排序
    :param item: ((x, y), threshold)
    :return:
    '''

    return (item[0][1], item[0][0])
def exist_pic(name, pic_full_path, threshold=None, sub_path=None, subfolder='', preview=False, priority_index=0, filter_same=False, sort_rule=SortRule.THRESHOLD_REVERSE):
    '''
    OpenCV识别一张图片中模板截图命中的所有区域
    :param name: 模板截图简称。模板截图全称 = 模板截图简称_system()_屏幕截图分辨率宽x屏幕截图分辨率高，模板截图全称 形如 {name}_mac_2880x1800，支持3种扩展类型（.png, .jpg, .jpeg）、选其一即可
    :param pic_full_path: 图片的完整路径
    :param threshold: 图片模板匹配时的相似度阈值，范围为(0,1)，越接近1表示相似度要求越高，默认为global_var.threshold
    :param sub_path: 模板截图存放路径，默认为{global_var.root_path}/template_pic，如果subfolder为空串''的话，则模板截图的完整路径形如 {global_var.root_path}/template_pic/{name}_mac_2880x1800.png
    :param subfolder: 模板截图存放的子文件夹路径，默认为空串''，可用于将模板截图按开发者名字或所属业务模块进行分类管理、以实现模板截图之间的隔离。当不为空串''时，比如subfolder为'xincheng/im'时，则模板截图的完整路径形如 {global_var.root_path}/template_pic/xincheng/im/{name}_mac_2880x1800.png
    :param preview: 是否对模板截图的所有命中区域进行红色描边预览（用于开发脚本时的调试，实际脚本运行测试时要将preview改成False）
    :param priority_index: 在命中区域集合中选择要交互的那个命中区域下标，默认为0、表示默认交互第1个命中区域。但在这里的作用为：0表示用模板截图进行高性能的单目标匹配，非0表示用模板截图进行多目标匹配。
    :param filter_same: OpenCV多目标匹配时，filter_same为True可过滤掉重复命中区域
    :param sort_rule: OpenCV多目标匹配时，命中区的排序规则
    :return:
    [bool, # 模板截图是否有命中区域
        [ # 命中区域集合（命中区域会按实际相似度actual_threshold进行倒序排列，所以一般情况下建议使用命中区域1）
            [ # 命中区域1
                [centerX,centerY],
                [left_topX,left_topY],
                [mid_topX,mid_topY],
                [right_topX,right_topY],
                [right_midX,right_midY],
                [right_bottomX,right_bottomY],
                [mid_bottomX,mid_bottomY],
                [left_bottomX,left_bottomY],
                [left_midX,left_midY],
                actual_threshold # 该区域的实际相似度
            ],
            [ # 命中区域2
                [centerX,centerY],
                [left_topX,left_topY],
                [mid_topX,mid_topY],
                [right_topX,right_topY],
                [right_midX,right_midY],
                [right_bottomX,right_bottomY],
                [mid_bottomX,mid_bottomY],
                [left_bottomX,left_bottomY],
                [left_midX,left_midY],
                actual_threshold # 该区域的实际相似度
            ],
            …… # 命中区域n
        ]
    ]

    [left_topX,left_topY]*******************[mid_topX,mid_topY]*******************[right_topX,right_topY]
    *****************************************************************************************************
    *****************************************************************************************************
    *****************************************************************************************************
    *****************************************************************************************************
    *****************************************************************************************************
    [left_midX,left_midY]********************[centerX,centerY]********************[right_midX,right_midY]
    *****************************************************************************************************
    *****************************************************************************************************
    *****************************************************************************************************
    *****************************************************************************************************
    *****************************************************************************************************
    [left_bottomX,left_bottomY]**********[mid_bottomX,mid_bottomY]**********[right_bottomX,right_bottomY]
    '''

    if threshold is None:
        threshold = global_var.threshold

    template_pic_full_path = ''

    if sub_path is None:
        sub_path = os.path.join(global_var.root_path, 'template_pic')
    # 创建template_pic文件夹
    os.makedirs(sub_path, exist_ok=True)
    template_pic_full_path = sub_path

    if len(subfolder) > 0:
        subfolder_path = os.path.join(sub_path, subfolder)
        # 创建subfolder文件夹
        os.makedirs(subfolder_path, exist_ok=True)
        template_pic_full_path = subfolder_path

    for suffix in ['.png', '.jpg', '.jpeg']:
        # 拼接模板截图的完整路径
        temp_path = os.path.join(template_pic_full_path, template_pic_full_name(name) + suffix)
        if os.path.exists(temp_path):
            template_pic_full_path = temp_path
            break

    img = cv2.imread(pic_full_path)
    template_img = cv2.imread(template_pic_full_path)
    if template_img is None:
        temp_path_prefix, temp_path_extension = os.path.splitext(temp_path)
        assert False, f"缺失该分辨率下元素定位的模板素材：{temp_path_prefix}"
    height, width, c = template_img.shape
    res = cv2.matchTemplate(img, template_img, cv2.TM_CCOEFF_NORMED)
    matched_points = []
    # if priority_index == 0: # 单目标匹配，优化性能
    #     minValue, maxValue, minLoc, maxLoc = cv2.minMaxLoc(res)
    #     if maxValue > threshold:
    #         matched_points.append((maxLoc, maxValue))
    # else: # 多目标匹配
    #     # 双重嵌套效率太低
    #     for y in range(len(res)):
    #         for x in range(len(res[y])):
    #             if res[y][x] > threshold:
    #                 matched_points.append(((x, y), res[y][x]))

    # 向量化操作，匹配一次多目标耗时1秒内
    indices = np.argwhere(res > threshold)
    for idx in indices:
        matched_points.append(((idx[1], idx[0]), res[idx[0]][idx[1]]))
    sorted_points = sorted(matched_points, key=lambda z: z[1], reverse=True)

    if filter_same:
        filter_points = []
        filter_index = 0
        side_points = []
        for point in sorted_points:
            x = point[0][0]
            y = point[0][1]
            if filter_index == 0:
                filter_points.append(point)
                side_points.append({
                    'x_max': x,
                    'x_min': x,
                    'y_max': y,
                    'y_min': y
                })
            else:
                new_point = True
                for side in side_points:
                    x_max = side['x_max']
                    x_min = side['x_min']
                    y_max = side['y_max']
                    y_min = side['y_min']
                    if x > x_max + 1 or x < x_min - 1 or y > y_max + 1 or y < y_min - 1:
                        pass
                    else:
                        new_point = False
                        if x > x_max:
                            side['x_max'] = x
                        if x < x_min:
                            side['x_min'] = x
                        if y > y_max:
                            side['y_max'] = y
                        if y < y_min:
                            side['y_min'] = y
                if new_point:
                    filter_points.append(point)
                    side_points.append({
                        'x_max': x,
                        'x_min': x,
                        'y_max': y,
                        'y_min': y
                    })
            filter_index += 1
        sorted_points = filter_points

    if sort_rule == SortRule.THRESHOLD_REVERSE:
        pass
    elif sort_rule == SortRule.Y_X:
        sorted_points = sorted(sorted_points, key=custom_sort)

    final_points = [] # [[[中心点X,中心点Y],[左上X,左上Y],[中上X,中上Y],……顺时针,实际相似度],[]]
    for point in sorted_points:
        x = point[0][0]
        y = point[0][1]
        final_point = [
            [x + width / 2, y + height / 2], # [中心点X,中心点Y]
            [x, y],                          # [左上X,左上Y]
            [x + width / 2, y],              # [中上X,中上Y]
            [x + width, y],                  # [右上X,右上Y]
            [x + width, y + height / 2],     # [右中X,右中Y]
            [x + width, y + height],         # [右下X,右下Y]
            [x + width / 2, y + height],     # [中下X,中下Y]
            [x, y + height],                 # [左下X,左下Y]
            [x, y + height / 2],             # [左中X,左中Y]
            point[1]
        ]
        final_points.append(final_point)

        if preview:
            cv2.rectangle(img, (int(final_point[1][0]), int(final_point[1][1])), (int(final_point[5][0]), int(final_point[5][1])), (0, 0, 255), 2)

    if preview:
        cv2.imshow('img', img)
        cv2.waitKey()
        cv2.destroyAllWindows()

    return [len(final_points) > 0, final_points]

def exist_res_offset(exist_res, offset_x=0, offset_y=0, priority_index=0, act_position=Position.CENTER):
    '''
    篡改exist_res数据，实现交互点的offset偏移，单位像素
    :param exist_res: 来自exist_pic或exist_text的接口结果，或完全手动构造也可以
    :param offset_x: 横向偏移量，正为右，负为左，默认为0不偏移
    :param offset_y: 纵向偏移量，正为下，负为上，默认为0不偏移
    :param priority_index: 要篡改的命中区域下标，默认为0、表示默认篡改第1个命中区域
    :param act_position: 要篡改的交互点位，默认为中心点，其他点位详见Position枚举
    :return: new_exist_res，对exist_res深拷贝后篡改的数据
    '''

    new_exist_res = copy.deepcopy(exist_res)
    point = new_exist_res[1][priority_index][act_position.value]
    new_exist_res[1][priority_index][act_position.value] = [int(point[0]) + offset_x, int(point[1]) + offset_y]
    return new_exist_res

def exist_res_filter_by_region(exist_res, left_x = None, right_x = None, top_y = None, bottom_y = None):
    '''
    扫描局部区域内是否有命中的元素
    :param exist_res: 全屏的exist_res
    :param left_x: 左边界
    :param right_x: 右边界
    :param top_y: 上边界
    :param bottom_y: 下边界
    :return: 边界内的exist_res
    '''

    width, height = get_screenshot_resolution()
    if left_x is None:
        left_x = 0
    if right_x is None:
        right_x = width
    if top_y is None:
        top_y = 0
    if bottom_y is None:
        bottom_y = height

    points_list = []
    for points in exist_res[1]:
        center_x = points[0][0]
        center_y = points[0][1]
        if center_x >= left_x and center_x <= right_x and center_y >= top_y and center_y <= bottom_y:
            points_list.append(points)
    return [len(points_list) > 0, points_list]

def act_text(text, pic_full_path, equal_filter=False, act_position=Position.CENTER, priority_index=0, act_mode=ActMode.LEFT_CLICK, filter_special_chars=False):
    '''
    基于接口exist_text的结果，对命中区域进行交互。因为是直接进行交互的接口，所以潜台词就是能命中区域，故如果没有命中区域的话、DTClientAutotest会直接assert断言失败
    :param text: 目标文字
    :param pic_full_path: 图片的完整路径
    :param equal_filter: 是否过滤出与目标文字完全相等的命中区域。比如当OCR识别出的ocr_text集合为['12abc34','2abc3','abc34']，目标文字text为'2abc3': 当equal_filter为False时，可以命中['12abc34','2abc3']；当equal_filter为True时，只能命中['2abc3']
    :param act_position: 与命中区域进行交互的点位，默认为中心点，其他点位详见Position枚举
    :param priority_index: 在命中区域集合中选择要交互的那个命中区域下标，默认为0、表示默认交互第1个命中区域
    :param act_mode: 与命中区域进行交互的交互模式，默认为左单击，其他交互模式详见ActMode枚举
    :param filter_special_chars: 是否干掉 除了 "字母（大小写）、数字（阿拉伯）、汉字" 之外 的字符
    :return: [exist_res, act_res]，其中exist_res来自exist_text的接口结果，act_res来自act_point的接口结果
    '''

    exist_res = exist_text(text=text, pic_full_path=pic_full_path, equal_filter=equal_filter, preview=False, filter_special_chars=filter_special_chars)
    assert exist_res[0], 'OCR识别不到目标文字, text='+text+', pic_full_path='+pic_full_path+', equal_filter='+str(equal_filter)+', preview=False'
    act_res = act_point(exist_res=exist_res, act_position=act_position, priority_index=priority_index, act_mode=act_mode)
    return [exist_res, act_res]

def act_pic(name, pic_full_path, threshold=None, sub_path=None, subfolder='', act_position=Position.CENTER, priority_index=0, act_mode=ActMode.LEFT_CLICK, filter_same=False, sort_rule=SortRule.THRESHOLD_REVERSE):
    '''
    基于接口exist_pic的结果，对命中区域进行交互。因为是直接进行交互的接口，所以潜台词就是能命中区域，故如果没有命中区域的话、DTClientAutotest会直接assert断言失败
    :param name: 模板截图简称。模板截图全称 = 模板截图简称_system()_屏幕截图分辨率宽x屏幕截图分辨率高，模板截图全称 形如 {name}_mac_2880x1800，支持3种扩展类型（.png, .jpg, .jpeg）、选其一即可
    :param pic_full_path: 图片的完整路径
    :param threshold: 图片模板匹配时的相似度阈值，范围为(0,1)，越接近1表示相似度要求越高，默认为global_var.threshold
    :param sub_path: 模板截图存放路径，默认为{global_var.root_path}/template_pic，如果subfolder为空串''的话，则模板截图的完整路径形如 {global_var.root_path}/template_pic/{name}_mac_2880x1800.png
    :param subfolder: 模板截图存放的子文件夹路径，默认为空串''，可用于将模板截图按开发者名字或所属业务模块进行分类管理、以实现模板截图之间的隔离。当不为空串''时，比如subfolder为'xincheng/im'时，则模板截图的完整路径形如 {global_var.root_path}/template_pic/xincheng/im/{name}_mac_2880x1800.png
    :param act_position: 与命中区域进行交互的点位，默认为中心点，其他点位详见Position枚举
    :param priority_index: 在命中区域集合中选择要交互的那个命中区域下标，默认为0、表示默认交互第1个命中区域
    :param act_mode: 与命中区域进行交互的交互模式，默认为左单击，其他交互模式详见ActMode枚举
    :param filter_same: OpenCV多目标匹配时，filter_same为True可过滤掉重复命中区域
    :param sort_rule: OpenCV多目标匹配时，命中区的排序规则
    :return: [exist_res, act_res]，其中exist_res来自exist_pic的接口结果，act_res来自act_point的接口结果
    '''

    if threshold is None:
        threshold = global_var.threshold
    if sub_path is None:
        sub_path = os.path.join(global_var.root_path, 'template_pic')

    exist_res = exist_pic(name=name, pic_full_path=pic_full_path, threshold=threshold, sub_path=sub_path, subfolder=subfolder, preview=False, priority_index=priority_index, filter_same=filter_same, sort_rule=sort_rule)
    assert exist_res[0], 'OpenCV识别不到目标区域, name='+name+', pic_full_path='+pic_full_path+', threshold='+str(threshold)+', sub_path='+sub_path+', subfolder='+subfolder+', preview=False'
    act_res = act_point(exist_res=exist_res, act_position=act_position, priority_index=priority_index, act_mode=act_mode)
    return [exist_res, act_res]

def get_scale():
    '''
    像素比例转化
    :return: 转化后的像素比例
    '''

    if 'win' == system():
        scale = 1.0
    elif 'mac' == system():
        scale = 2.0
    if get_uuid() in global_var.uuid_resolution_scale_dict: # 特殊设备
        scale = global_var.uuid_resolution_scale_dict[get_uuid()]
    return scale

def act_point(exist_res, act_position=Position.CENTER, priority_index=0, act_mode=ActMode.LEFT_CLICK):
    '''
    执行交互，act_text和act_pic内部均调用了act_point来执行交互，另外act_point还可以用于"坐标点增加偏移量"的交互和"绝对坐标"的交互、不仅限于命中区域的9个点位交互、进一步增加了交互位置的灵活性
    :param exist_res: 来自exist_text或exist_pic接口的结果；也可以在exist_text或exist_pic接口的结果基础上增加交互偏移量，形如point(x,y) => point(x+offsetX,y+offsetY)；甚至可以直接自定义一个全新的point(newX,newY)
    :param act_position: 与命中区域进行交互的点位，默认为中心点，其他点位详见Position枚举
    :param priority_index: 在命中区域集合中选择要交互的那个命中区域下标，默认为0、表示默认交互第1个命中区域
    :param act_mode: 与命中区域进行交互的交互模式，默认为左单击，其他交互模式详见ActMode枚举
    :return: 经过分辨率比例转化后实际交互的坐标点[x, y]
    '''

    assert exist_res[0] and len(exist_res[1]) > 0, 'exist_res数据异常 或 可交互点位集合为空'
    assert priority_index >=0 and priority_index + 1 <= len(exist_res[1]), 'priority_index越界了, len(exist_res[1]) = ' + str(len(exist_res[1])) + ', priority_index = ' + str(priority_index)

    # 要交互的点，单位像素
    point = exist_res[1][priority_index][act_position.value]

    x = point[0] / get_scale()
    y = point[1] / get_scale()

    # 按交互模式执行交互
    if act_mode == ActMode.LEFT_CLICK: # 左单击
        # pyautogui.click(x, y)

        # 解决pyautogui.click有时点了没反应的问题
        pyautogui.moveTo(x, y)
        pyautogui.mouseDown()
        pyautogui.mouseUp()
    elif act_mode == ActMode.RIGHT_CLICK: # 右单击
        pyautogui.click(x, y, button='right')
    elif act_mode == ActMode.DOUBLE_LEFT_CLICK: # 左双击
        control = mouse.Controller()
        control.position = (x, y)
        time.sleep(1) # 这里不能太快，否则无法双击成功
        control.click(mouse.Button.left, 2)
    elif act_mode == ActMode.MOVE_ON: # 移动到
        pyautogui.moveTo(x, y)

    return [x, y]

def loop_exist_pic(name, threshold=None, sub_path=None, subfolder='', before=None, timeout=None, interval=None, after=None, priority_index=0, filter_same=False, sort_rule=SortRule.THRESHOLD_REVERSE):
    '''
    轮询OpenCV识别一张图片中模板截图命中的所有区域，内部自动完成PC端屏幕截图和删除、截图无需外部传入
    :param name: 模板截图简称。模板截图全称 = 模板截图简称_system()_屏幕截图分辨率宽x屏幕截图分辨率高，模板截图全称 形如 {name}_mac_2880x1800，支持3种扩展类型（.png, .jpg, .jpeg）、选其一即可
    :param threshold: 图片模板匹配时的相似度阈值，范围为(0,1)，越接近1表示相似度要求越高，默认为global_var.threshold
    :param sub_path: 模板截图存放路径，默认为{global_var.root_path}/template_pic，如果subfolder为空串''的话，则模板截图的完整路径形如 {global_var.root_path}/template_pic/{name}_mac_2880x1800.png
    :param subfolder: 模板截图存放的子文件夹路径，默认为空串''，可用于将模板截图按开发者名字或所属业务模块进行分类管理、以实现模板截图之间的隔离。当不为空串''时，比如subfolder为'xincheng/im'时，则模板截图的完整路径形如 {global_var.root_path}/template_pic/xincheng/im/{name}_mac_2880x1800.png
    :param before: 第一次轮询前等待的秒数，默认为{global_var.loop_exist_pic_before}
    :param timeout: 轮询的最大超时秒数，默认为{global_var.loop_exist_pic_timeout}
    :param interval: 在未轮询超时的情况下，且未轮询到目标区域时的轮询间隔秒数，默认为{global_var.loop_exist_pic_interval}
    :param after: 在未轮询超时的情况下，且轮询到目标区域后等待的秒数，默认为{global_var.loop_exist_pic_after}
    :param priority_index: 在命中区域集合中选择要交互的那个命中区域下标，默认为0、表示默认交互第1个命中区域。但在这里的作用为：0表示用模板截图进行高性能的单目标匹配，非0表示用模板截图进行多目标匹配。
    :param filter_same: OpenCV多目标匹配时，filter_same为True可过滤掉重复命中区域
    :param sort_rule: OpenCV多目标匹配时，命中区的排序规则
    :return: exist_res，来自exist_pic的接口结果
    '''

    if threshold is None:
        threshold = global_var.threshold
    if sub_path is None:
        sub_path = os.path.join(global_var.root_path, 'template_pic')
    if before is None:
        before = global_var.loop_exist_pic_before
    if timeout is None:
        timeout = global_var.loop_exist_pic_timeout
    if interval is None:
        interval = global_var.loop_exist_pic_interval
    if after is None:
        after = global_var.loop_exist_pic_after

    time.sleep(before) # 在轮询开始前等待before秒

    start_time = time.time() # 开始轮询的时间戳
    while True:
        pic_full_path = screenshot() # 截图
        exist_res = exist_pic(name=name, pic_full_path=pic_full_path, threshold=threshold, sub_path=sub_path, subfolder=subfolder, preview=False, priority_index=priority_index, filter_same=filter_same, sort_rule=sort_rule)
        if os.path.exists(pic_full_path):
            os.remove(pic_full_path) # 清理截图
        end_time = time.time() # 轮询后的时间戳
        duration = end_time - start_time # 耗时
        if duration > timeout: # 已超时
            return exist_res # 无论是否轮询到目标元素，直接结束
        else: # 还未超时
            if exist_res[0]: # 已轮询到目标元素
                time.sleep(after) # 在轮询到目标元素后等待after秒
                return exist_res # 轮询到目标元素，返回结果
            else: # 未轮询到目标元素，继续轮询
                time.sleep(interval) # 轮询间隔interval秒

def loop_exist_pic_list(pic_config_list: List[Dict], timeout=None):
    '''
    多素材交替式轮询查找命中区。命中一个素材即停止（建议这些素材的出现是互斥的）；或达到超时上限了也会停止。
    :param pic_config_list: 模板截图素材组
    :param timeout: 超时上限。当timeout为None时，有默认的超时上限（len(pic_config_list) * 3）；也可自定义透传进来。
    :return: 当命中一个素材时，返回{'index': index, 'exist_res': exist_res}，index为命中的素材在pic_config_list中的下标、从0开始；当超时了，固定返回{'index': -1, 'exist_res': None}
    '''

    # 参数合法性检测
    assert type(pic_config_list) == list, 'pic_config_list必须为list类型'
    if len(pic_config_list) == 0:
        assert False, 'pic_config_list不能为空数组[]'
    for pic_config in pic_config_list:
        assert type(pic_config) == dict, 'pic_config必须为dict类型'
        assert 'name' in pic_config, 'name是pic_config中必传的key'

    start_time = time.time()
    while True:
        pic_full_path = screenshot()

        index = -1
        for pic_config in pic_config_list:
            index += 1
            name = pic_config['name']
            threshold = pic_config['threshold'] if 'threshold' in pic_config else None
            sub_path = pic_config['sub_path'] if 'sub_path' in pic_config else None
            subfolder = pic_config['subfolder'] if 'subfolder' in pic_config else ''
            priority_index = pic_config['priority_index'] if 'priority_index' in pic_config else 0
            filter_same = pic_config['filter_same'] if 'filter_same' in pic_config else False
            sort_rule = pic_config['sort_rule'] if 'sort_rule' in pic_config else SortRule.THRESHOLD_REVERSE
            exist_res = exist_pic(name=name, pic_full_path=pic_full_path, threshold=threshold, sub_path=sub_path, subfolder=subfolder, preview=False, priority_index=priority_index, filter_same=filter_same, sort_rule=sort_rule)
            if exist_res[0]:
                os.remove(pic_full_path)
                return {'index': index, 'exist_res': exist_res}

        os.remove(pic_full_path)
        duration = time.time() - start_time
        # 默认为预估所有素材循环3次左右，也可外部透传进来自定义超时时间（单位：秒）
        real_timeout = len(pic_config_list) * 3 if timeout is None else timeout
        if duration > real_timeout:
            return {'index': -1, 'exist_res': None}

def loop_exist_text(text, equal_filter=False, before=None, timeout=None, interval=None, after=None, rm_screenshot=True, filter_special_chars=False):
    '''
    轮询OCR识别一张图片中目标文字命中的所有区域，内部自动完成PC端屏幕截图和删除、截图无需外部传入
    :param text: 目标文字
    :param equal_filter: 是否过滤出与目标文字完全相等的命中区域。比如当OCR识别出的ocr_text集合为['12abc34','2abc3','abc34']，目标文字text为'2abc3': 当equal_filter为False时，可以命中['12abc34','2abc3']；当equal_filter为True时，只能命中['2abc3']
    :param before: 第一次轮询前等待的秒数，默认为{global_var.loop_exist_text_before}
    :param timeout: 轮询的最大超时秒数，默认为{global_var.loop_exist_text_timeout}
    :param interval: 在未轮询超时的情况下，且未轮询到目标区域时的轮询间隔秒数，默认为{global_var.loop_exist_text_interval}
    :param after: 在未轮询超时的情况下，且轮询到目标区域后等待的秒数，默认为{global_var.loop_exist_text_after}
    :param rm_screenshot: 内部参数、外部不要使用、默认值为True
    :param filter_special_chars: 是否干掉 除了 "字母（大小写）、数字（阿拉伯）、汉字" 之外 的字符
    :return: exist_res，来自exist_text的接口结果
    '''

    if before is None:
        before = global_var.loop_exist_text_before
    if timeout is None:
        timeout = global_var.loop_exist_text_timeout
    if interval is None:
        interval = global_var.loop_exist_text_interval
    if after is None:
        after = global_var.loop_exist_text_after

    time.sleep(before)  # 在轮询开始前等待before秒

    start_time = time.time()  # 开始轮询的时间戳
    while True:
        pic_full_path = screenshot()  # 截图
        exist_res = exist_text(text=text, pic_full_path=pic_full_path, equal_filter=equal_filter, preview=False, filter_special_chars=filter_special_chars)
        end_time = time.time()  # 轮询后的时间戳
        duration = end_time - start_time # 耗时
        if duration > timeout: # 已超时
            if exist_res[0] and not rm_screenshot:
                exist_res.append(pic_full_path)
            else:
                os.remove(pic_full_path)  # 清理截图
            return exist_res  # 无论是否轮询到目标元素，直接结束
        else: # 还未超时
            if exist_res[0]: # 已轮询到目标元素
                time.sleep(after)  # 在轮询到目标元素后等待after秒
                if rm_screenshot:
                    os.remove(pic_full_path)  # 清理截图
                else:
                    exist_res.append(pic_full_path)
                return exist_res  # 轮询到目标元素，返回结果
            else: # 未轮询到目标元素，继续轮询
                os.remove(pic_full_path)  # 清理截图
                time.sleep(interval) # 轮询间隔interval秒

def create_pic_cache_for_text(base_pic_full_path, left_top_point, right_bottom_point, pic_cache_full_path):
    '''
    对一张图片中的局部区域完成截图（内部接口，服务于loop_exist_text_by_pic_cache接口）
    :param base_pic_full_path: 图片的完整路径
    :param left_top_point: 想要截取的局部区域的左上角坐标 [left_topX, left_topY]
    :param right_bottom_point: 想要截取的局部区域的右下角坐标 [right_bottomX, right_bottomY]
    :param pic_cache_full_path: 存放局部区域截图的完整路径
    :return:
    '''

    pic_cache_sub_path = os.path.dirname(pic_cache_full_path)
    os.makedirs(pic_cache_sub_path, exist_ok=True) # 确保缓存图所在的文件夹均已创建

    base_pic_img = cv2.imread(base_pic_full_path)
    pic_cache_img = base_pic_img[int(left_top_point[1]):int(right_bottom_point[1]), int(left_top_point[0]):int(right_bottom_point[0])]
    cv2.imwrite(pic_cache_full_path, pic_cache_img)

def get_md5_of_str(string):
    '''
    获取一段字符串的md5值
    :param string: 传入的字符串
    :return: 字符串的md5值
    '''

    hash_object = hashlib.md5()
    hash_object.update(string.encode('utf-8'))
    return hash_object.hexdigest()

def create_default_pic_cache_name_from_inspect_stack(skip_stack_level_for_cache=0):
    '''
    SDK内部接口，外部不要使用，利用切片获取本次调用堆栈，来定位并拼接外部调用ocr缓存式接口的唯一性信息、自动建立外部脚本中的ocr与缓存图的映射关系
    :param skip_stack_level_for_cache: 函数封装时如果缓存接口入参传了变量，则需要对调用堆栈层级进行跳跃来生成正确的缓存名
    :return: 唯一性映射关系的md5值
    '''

    inspect_stack = inspect.stack()
    target_i = None
    index = -1
    for i in inspect_stack:
        index = index + 1
        if 'mac' == system():
            if 'DTClientAutotest/pc/core.py' not in i[1]: # 第一个不含框架内的外部调用就是脚本中的py路径
                target_i = i
                break
        elif 'win' == system():
            if 'DTClientAutotest\\pc\\core.py' not in i[1]:
                target_i = i
                break
    target_i = inspect_stack[index + skip_stack_level_for_cache]
    # py路径::def函数名::调用code
    pic_cache_name_info = target_i[1] + '::' + target_i[3] + '::' + ''.join(target_i[4])
    return get_md5_of_str(pic_cache_name_info)

def loop_exist_text_by_pic_cache(text, pic_cache_name=None, equal_filter=False, before_for_text=None, timeout_for_text=None, interval_for_text=None, after_for_text=None, threshold=None, sub_path=None, subfolder='default', before_for_pic=None, timeout_for_pic=None, interval_for_pic=None, after_for_pic=None, priority_index=0, skip_stack_level_for_cache=0, filter_special_chars=False, filter_same=False, sort_rule=SortRule.THRESHOLD_REVERSE):
    '''
    缓存式轮询OCR识别一张图片中目标文字命中的所有区域。有图片缓存则走loop_exist_pic，没图片缓存则走loop_exist_text且在目标文字命中区域后对第下标为priority_index的命中区域进行截图缓存
    :param text: 目标文字
    :param pic_cache_name: 缓存截图简称，与目标文字建立映射关系。缓存截图全称 = 缓存截图简称_system()_屏幕截图分辨率宽x屏幕截图分辨率高，缓存截图全称 形如 {pic_cache_name}_mac_2880x1800，扩展类型固定为 .png，这里ocr缓存映射的pic_cache_name默认值为'py路径::def函数名::调用code'的md5值，来自接口create_default_pic_cache_name_from_inspect_stack()的结果
    :param equal_filter: 是否过滤出与目标文字完全相等的命中区域。比如当OCR识别出的ocr_text集合为['12abc34','2abc3','abc34']，目标文字text为'2abc3': 当equal_filter为False时，可以命中['12abc34','2abc3']；当equal_filter为True时，只能命中['2abc3']
    :param before_for_text: 第一次轮询前等待的秒数，默认为{global_var.loop_exist_text_before}，透传给loop_exist_text接口
    :param timeout_for_text: 轮询的最大超时秒数，默认为{global_var.loop_exist_text_timeout}，透传给loop_exist_text接口
    :param interval_for_text: 在未轮询超时的情况下，且未轮询到目标区域时的轮询间隔秒数，默认为{global_var.loop_exist_text_interval}，透传给loop_exist_text接口
    :param after_for_text: 在未轮询超时的情况下，且轮询到目标区域后等待的秒数，默认为{global_var.loop_exist_text_after}，透传给loop_exist_text接口
    :param threshold: 图片模板匹配时的相似度阈值，范围为(0,1)，越接近1表示相似度要求越高，默认为global_var.threshold
    :param sub_path: 缓存截图存放路径，默认为{global_var.root_path}/pic_cache_for_text，如果subfolder为空串''的话，则缓存截图的完整路径形如 {global_var.root_path}/pic_cache_for_text/{pic_cache_name}_mac_2880x1800.png
    :param subfolder: 缓存截图存放的子文件夹路径，默认为default，可用于将缓存截图按开发者名字或所属业务模块进行分类管理、以实现缓存截图之间的隔离。当不为空串''时，比如subfolder为'xincheng/im'时，则缓存截图的完整路径形如 {global_var.root_path}/pic_cache_for_text/xincheng/im/{pic_cache_name}_mac_2880x1800.png
    :param before_for_pic: 第一次轮询前等待的秒数，默认为{global_var.loop_exist_pic_before}，透传给loop_exist_pic接口
    :param timeout_for_pic: 轮询的最大超时秒数，默认为{global_var.loop_exist_pic_timeout}，透传给loop_exist_pic接口
    :param interval_for_pic: 在未轮询超时的情况下，且未轮询到目标区域时的轮询间隔秒数，默认为{global_var.loop_exist_pic_interval}，透传给loop_exist_pic接口
    :param after_for_pic: 在未轮询超时的情况下，且轮询到目标区域后等待的秒数，默认为{global_var.loop_exist_pic_after}，透传给loop_exist_pic接口
    :param priority_index: 在命中区域集合中选择要交互的那个命中区域下标，默认为0、表示默认交互第1个命中区域。但在这里的作用为：0表示用模板截图进行高性能的单目标匹配，非0表示用模板截图进行多目标匹配。
    :param skip_stack_level_for_cache: 函数封装时如果缓存接口入参传了变量，则需要对调用堆栈层级进行跳跃来生成正确的缓存名
    :param filter_special_chars: 是否干掉 除了 "字母（大小写）、数字（阿拉伯）、汉字" 之外 的字符
    :param filter_same: OpenCV多目标匹配时，filter_same为True可过滤掉重复命中区域
    :param sort_rule: OpenCV多目标匹配时，命中区的排序规则
    :return: exist_res，走图片缓存时来自exist_pic的接口结果，不走图片缓存时来自exist_text的接口结果
    '''

    if pic_cache_name is None:
        pic_cache_name = create_default_pic_cache_name_from_inspect_stack(skip_stack_level_for_cache=skip_stack_level_for_cache)

    if before_for_text is None:
        before_for_text = global_var.loop_exist_text_before
    if timeout_for_text is None:
        timeout_for_text = global_var.loop_exist_text_timeout
    if interval_for_text is None:
        interval_for_text = global_var.loop_exist_text_interval
    if after_for_text is None:
        after_for_text = global_var.loop_exist_text_after

    if threshold is None:
        threshold = global_var.cache_threshold
    if sub_path is None:
        sub_path = os.path.join(global_var.root_path, 'pic_cache_for_text')
    if before_for_pic is None:
        before_for_pic = global_var.loop_exist_pic_before
    if timeout_for_pic is None:
        timeout_for_pic = global_var.loop_exist_pic_timeout
    if interval_for_pic is None:
        interval_for_pic = global_var.loop_exist_pic_interval
    if after_for_pic is None:
        after_for_pic = global_var.loop_exist_pic_after

    # 拼接缓存图完整路径
    pic_cache_full_path = os.path.join(sub_path, subfolder, template_pic_full_name(pic_cache_name) + '.png')
    if os.path.exists(pic_cache_full_path): # 有缓存
        # 走缓存为的就是快，所以要priority_index写死为0，走图像的高性能单目标匹配
        exist_res = loop_exist_pic(name=pic_cache_name, threshold=threshold, sub_path=sub_path, subfolder=subfolder, before=before_for_pic, timeout=timeout_for_pic, interval=interval_for_pic, after=after_for_pic, priority_index=0, filter_same=filter_same, sort_rule=sort_rule)
        if exist_res[0]:
            return exist_res
        else: # 如果文字缓存图匹配不到元素，则删除文字缓存图
            os.remove(pic_cache_full_path)

    # 没文字缓存图 或 有缓存但没匹配到则进行OCR重试
    exist_res = loop_exist_text(text=text, equal_filter=equal_filter, before=before_for_text, timeout=timeout_for_text, interval=interval_for_text, after=after_for_text, rm_screenshot=False, filter_special_chars=filter_special_chars)
    if exist_res[0]: # 匹配到了
        # 生成文字缓存图（对应priority_index）
        create_pic_cache_for_text(base_pic_full_path=exist_res[2], left_top_point=exist_res[1][priority_index][1], right_bottom_point=exist_res[1][priority_index][5], pic_cache_full_path=pic_cache_full_path)
        # 删除残留截图
        os.remove(exist_res[2])
    return exist_res

def loop_act_pic(name, threshold=None, sub_path=None, subfolder='', before=None, timeout=None, interval=None, after=None, act_position=Position.CENTER, priority_index=0, act_mode=ActMode.LEFT_CLICK, filter_same=False, sort_rule=SortRule.THRESHOLD_REVERSE):
    '''
    在loop_exist_pic接口轮询结果的基础上，增加act_point进行交互，内部会断言存在命中区域
    :param name: 模板截图简称。模板截图全称 = 模板截图简称_system()_屏幕截图分辨率宽x屏幕截图分辨率高，模板截图全称 形如 {name}_mac_2880x1800，支持3种扩展类型（.png, .jpg, .jpeg）、选其一即可
    :param threshold: 图片模板匹配时的相似度阈值，范围为(0,1)，越接近1表示相似度要求越高，默认为global_var.threshold
    :param sub_path: 模板截图存放路径，默认为{global_var.root_path}/template_pic，如果subfolder为空串''的话，则模板截图的完整路径形如 {global_var.root_path}/template_pic/{name}_mac_2880x1800.png
    :param subfolder: 模板截图存放的子文件夹路径，默认为空串''，可用于将模板截图按开发者名字或所属业务模块进行分类管理、以实现模板截图之间的隔离。当不为空串''时，比如subfolder为'xincheng/im'时，则模板截图的完整路径形如 {global_var.root_path}/template_pic/xincheng/im/{name}_mac_2880x1800.png
    :param before: 第一次轮询前等待的秒数，默认为{global_var.loop_exist_pic_before}
    :param timeout: 轮询的最大超时秒数，默认为{global_var.loop_exist_pic_timeout}
    :param interval: 在未轮询超时的情况下，且未轮询到目标区域时的轮询间隔秒数，默认为{global_var.loop_exist_pic_interval}
    :param after: 在未轮询超时的情况下，且轮询到目标区域后等待的秒数，默认为{global_var.loop_exist_pic_after}
    :param act_position: 与命中区域进行交互的点位，默认为中心点，其他点位详见Position枚举
    :param priority_index: 在命中区域集合中选择要交互的那个命中区域下标，默认为0、表示默认交互第1个命中区域
    :param act_mode: 与命中区域进行交互的交互模式，默认为左单击，其他交互模式详见ActMode枚举
    :param filter_same: OpenCV多目标匹配时，filter_same为True可过滤掉重复命中区域
    :param sort_rule: OpenCV多目标匹配时，命中区的排序规则
    :return: [exist_res, act_res]，其中exist_res来自exist_pic的接口结果，act_res来自act_point的接口结果
    '''

    if threshold is None:
        threshold = global_var.threshold
    if sub_path is None:
        sub_path = os.path.join(global_var.root_path, 'template_pic')
    if before is None:
        before = global_var.loop_exist_pic_before
    if timeout is None:
        timeout = global_var.loop_exist_pic_timeout
    if interval is None:
        interval = global_var.loop_exist_pic_interval
    if after is None:
        after = global_var.loop_exist_pic_after

    exist_res = loop_exist_pic(name=name, threshold=threshold, sub_path=sub_path, subfolder=subfolder, before=before, timeout=timeout, interval=interval, after=after, priority_index=priority_index, filter_same=filter_same, sort_rule=sort_rule)
    assert exist_res[0], '轮询OpenCV识别不到目标区域, name='+name+', threshold='+str(threshold)+', sub_path='+sub_path+', subfolder='+subfolder+', before='+str(before)+', timeout='+str(timeout)+', interval='+str(interval)+', after='+str(after)
    act_res = act_point(exist_res=exist_res, act_position=act_position, priority_index=priority_index, act_mode=act_mode)
    return [exist_res, act_res]

def loop_act_text(text, equal_filter=False, before=None, timeout=None, interval=None, after=None, act_position=Position.CENTER, priority_index=0, act_mode=ActMode.LEFT_CLICK, filter_special_chars=False):
    '''
    在loop_exist_text接口轮询结果的基础上，增加act_point进行交互，内部会断言存在命中区域
    :param text: 目标文字
    :param equal_filter: 是否过滤出与目标文字完全相等的命中区域。比如当OCR识别出的ocr_text集合为['12abc34','2abc3','abc34']，目标文字text为'2abc3': 当equal_filter为False时，可以命中['12abc34','2abc3']；当equal_filter为True时，只能命中['2abc3']
    :param before: 第一次轮询前等待的秒数，默认为{global_var.loop_exist_text_before}
    :param timeout: 轮询的最大超时秒数，默认为{global_var.loop_exist_text_timeout}
    :param interval: 在未轮询超时的情况下，且未轮询到目标区域时的轮询间隔秒数，默认为{global_var.loop_exist_text_interval}
    :param after: 在未轮询超时的情况下，且轮询到目标区域后等待的秒数，默认为{global_var.loop_exist_text_after}
    :param act_position: 与命中区域进行交互的点位，默认为中心点，其他点位详见Position枚举
    :param priority_index: 在命中区域集合中选择要交互的那个命中区域下标，默认为0、表示默认交互第1个命中区域
    :param act_mode: 与命中区域进行交互的交互模式，默认为左单击，其他交互模式详见ActMode枚举
    :param filter_special_chars: 是否干掉 除了 "字母（大小写）、数字（阿拉伯）、汉字" 之外 的字符
    :return: [exist_res, act_res]，其中exist_res来自exist_text的接口结果，act_res来自act_point的接口结果
    '''

    if before is None:
        before = global_var.loop_exist_text_before
    if timeout is None:
        timeout = global_var.loop_exist_text_timeout
    if interval is None:
        interval = global_var.loop_exist_text_interval
    if after is None:
        after = global_var.loop_exist_text_after

    exist_res = loop_exist_text(text=text, equal_filter=equal_filter, before=before, timeout=timeout, interval=interval, after=after, rm_screenshot=True, filter_special_chars=filter_special_chars)
    assert exist_res[0], '轮询OCR识别不到目标文字, text='+text+', equal_filter='+str(equal_filter)+', before='+str(before)+', timeout='+str(timeout)+', interval='+str(interval)+', after='+str(after)+', rm_screenshot=True'
    act_res = act_point(exist_res=exist_res, act_position=act_position, priority_index=priority_index, act_mode=act_mode)
    return [exist_res, act_res]

def loop_act_text_by_pic_cache(text, pic_cache_name=None, equal_filter=False, before_for_text=None, timeout_for_text=None, interval_for_text=None, after_for_text=None, threshold=None, sub_path=None, subfolder='default', before_for_pic=None, timeout_for_pic=None, interval_for_pic=None, after_for_pic=None, act_position=Position.CENTER, priority_index=0, act_mode=ActMode.LEFT_CLICK, skip_stack_level_for_cache=0, filter_special_chars=False, filter_same=False, sort_rule=SortRule.THRESHOLD_REVERSE):
    '''
    先使用loop_exist_text_by_pic_cache接口进行元素轮询，如果有命中区域、则使用act_point接口进行交互；如果没有命中区域且刚才没走缓存、则直接抛找不到目标文字的异常；如果没有命中区域且刚才走了缓存、则会不走缓存再重试且干掉缓存图
    :param text: 目标文字
    :param pic_cache_name: 缓存截图简称，与目标文字建立映射关系。缓存截图全称 = 缓存截图简称_system()_屏幕截图分辨率宽x屏幕截图分辨率高，缓存截图全称 形如 {pic_cache_name}_mac_2880x1800，扩展类型固定为 .png，这里ocr缓存映射的pic_cache_name默认值为'py路径::def函数名::调用code'的md5值，来自接口create_default_pic_cache_name_from_inspect_stack()的结果
    :param equal_filter: 是否过滤出与目标文字完全相等的命中区域。比如当OCR识别出的ocr_text集合为['12abc34','2abc3','abc34']，目标文字text为'2abc3': 当equal_filter为False时，可以命中['12abc34','2abc3']；当equal_filter为True时，只能命中['2abc3']
    :param before_for_text: 第一次轮询前等待的秒数，默认为{global_var.loop_exist_text_before}，透传给loop_exist_text接口
    :param timeout_for_text: 轮询的最大超时秒数，默认为{global_var.loop_exist_text_timeout}，透传给loop_exist_text接口
    :param interval_for_text: 在未轮询超时的情况下，且未轮询到目标区域时的轮询间隔秒数，默认为{global_var.loop_exist_text_interval}，透传给loop_exist_text接口
    :param after_for_text: 在未轮询超时的情况下，且轮询到目标区域后等待的秒数，默认为{global_var.loop_exist_text_after}，透传给loop_exist_text接口
    :param threshold: 图片模板匹配时的相似度阈值，范围为(0,1)，越接近1表示相似度要求越高，默认为global_var.threshold
    :param sub_path: 缓存截图存放路径，默认为{global_var.root_path}/pic_cache_for_text，如果subfolder为空串''的话，则缓存截图的完整路径形如 {global_var.root_path}/pic_cache_for_text/{pic_cache_name}_mac_2880x1800.png
    :param subfolder: 缓存截图存放的子文件夹路径，默认为default，可用于将缓存截图按开发者名字或所属业务模块进行分类管理、以实现缓存截图之间的隔离。当不为空串''时，比如subfolder为'xincheng/im'时，则缓存截图的完整路径形如 {global_var.root_path}/pic_cache_for_text/xincheng/im/{pic_cache_name}_mac_2880x1800.png
    :param before_for_pic: 第一次轮询前等待的秒数，默认为{global_var.loop_exist_pic_before}，透传给loop_exist_pic接口
    :param timeout_for_pic: 轮询的最大超时秒数，默认为{global_var.loop_exist_pic_timeout}，透传给loop_exist_pic接口
    :param interval_for_pic: 在未轮询超时的情况下，且未轮询到目标区域时的轮询间隔秒数，默认为{global_var.loop_exist_pic_interval}，透传给loop_exist_pic接口
    :param after_for_pic: 在未轮询超时的情况下，且轮询到目标区域后等待的秒数，默认为{global_var.loop_exist_pic_after}，透传给loop_exist_pic接口
    :param act_position: 与命中区域进行交互的点位，默认为中心点，其他点位详见Position枚举
    :param priority_index: 在命中区域集合中选择要交互的那个命中区域下标，默认为0、表示默认交互第1个命中区域
    :param act_mode: 与命中区域进行交互的交互模式，默认为左单击，其他交互模式详见ActMode枚举
    :param skip_stack_level_for_cache: 函数封装时如果缓存接口入参传了变量，则需要对调用堆栈层级进行跳跃来生成正确的缓存名
    :param filter_special_chars: 是否干掉 除了 "字母（大小写）、数字（阿拉伯）、汉字" 之外 的字符
    :param filter_same: OpenCV多目标匹配时，filter_same为True可过滤掉重复命中区域
    :param sort_rule: OpenCV多目标匹配时，命中区的排序规则
    :return: [exist_res, act_res]. 其中exist_res走图片缓存时来自exist_pic的接口结果，不走图片缓存时来自exist_text的接口结果；act_res来自act_point的接口结果
    '''

    if pic_cache_name is None:
        pic_cache_name = create_default_pic_cache_name_from_inspect_stack(skip_stack_level_for_cache=skip_stack_level_for_cache)

    if before_for_text is None:
        before_for_text = global_var.loop_exist_text_before
    if timeout_for_text is None:
        timeout_for_text = global_var.loop_exist_text_timeout
    if interval_for_text is None:
        interval_for_text = global_var.loop_exist_text_interval
    if after_for_text is None:
        after_for_text = global_var.loop_exist_text_after

    if threshold is None:
        threshold = global_var.cache_threshold
    if sub_path is None:
        sub_path = os.path.join(global_var.root_path, 'pic_cache_for_text')
    if before_for_pic is None:
        before_for_pic = global_var.loop_exist_pic_before
    if timeout_for_pic is None:
        timeout_for_pic = global_var.loop_exist_pic_timeout
    if interval_for_pic is None:
        interval_for_pic = global_var.loop_exist_pic_interval
    if after_for_pic is None:
        after_for_pic = global_var.loop_exist_pic_after

    exist_res = loop_exist_text_by_pic_cache(text=text, pic_cache_name=pic_cache_name, equal_filter=equal_filter, before_for_text=before_for_text, timeout_for_text=timeout_for_text, interval_for_text=interval_for_text, after_for_text=after_for_text, threshold=threshold, sub_path=sub_path, subfolder=subfolder, before_for_pic=before_for_pic, timeout_for_pic=timeout_for_pic, interval_for_pic=interval_for_pic, after_for_pic=after_for_pic, priority_index=priority_index, filter_special_chars=filter_special_chars, filter_same=filter_same, sort_rule=sort_rule)
    assert exist_res[0], '缓存式轮询OCR识别不到目标文字, text='+text+', pic_cache_name='+pic_cache_name+', equal_filter='+str(equal_filter)+', before_for_text='+str(before_for_text)+', timeout_for_text='+str(timeout_for_text)+', interval_for_text='+str(interval_for_text)+', after_for_text='+str(after_for_text)+', threshold='+str(threshold)+', sub_path='+sub_path+', subfolder='+subfolder+', before_for_pic='+str(before_for_pic)+', timeout_for_pic='+str(timeout_for_pic)+', interval_for_pic='+str(interval_for_pic)+', after_for_pic='+str(after_for_pic)
    if len(exist_res) == 2: # 刚才走的是缓存图，则只有一个高性能的命中区，避免越界
        priority_index = 0
    act_res = act_point(exist_res=exist_res, act_position=act_position, priority_index=priority_index, act_mode=act_mode)
    return [exist_res, act_res]

def loop_clear_alert(pic_config_list: List[Dict], timeout=None, repeat=None):
    '''
    多素材交替式轮询消除弹窗（以类似埋点的思路进行精准消窗）。
    :param pic_config_list: 需要采集在特定操作路径上出现过的特定弹窗素材组。允许弹窗素材只取自一种系统，即框架会自动检测是否存在与当前测试机匹配的"系统_分辨率"素材，如果没有则跳过（比如你只采集了win的弹窗素材，但对应的mac并不会有这种弹窗；或者你还未触发出mac的弹窗、导致你目前只能采集到win的弹窗）。
    :param timeout: 用户可透传进来的最大超时，默认为10（单位 秒）；需要注意的是，无论这里的timeout是多少，框架都会确保对pic_config_list里的弹窗素材至少轮询2次。
    :param repeat: 表示最多需要连续点击消除几个弹窗，默认为1（单位 个）。解释：比如你可能会遇到点完一个弹窗后，立马又会出现第二个弹窗需要你进行连续点击消除；或者界面上会同时出现两个弹窗需要你进行连续两次点击才能消完。当遇到这些情况时，repeat就传2，如果数量更多就以此类推传3/4/…
    :return:
    '''

    # 参数合法性检测
    assert type(pic_config_list) == list, 'pic_config_list必须为list类型'
    if len(pic_config_list) == 0:
        assert False, 'pic_config_list不能为空数组[]'
    for pic_config in pic_config_list:
        assert type(pic_config) == dict, 'pic_config必须为dict类型'
        assert 'name' in pic_config, 'name是pic_config中必传的key'

    # 参数默认值
    if timeout is None:
        timeout = 10
    if repeat is None:
        repeat = 1

    # 过滤出只适用于当前测试机的素材
    exist_pic_config_list = []
    for i, pic_config in enumerate(pic_config_list):
        # 取值
        name = pic_config['name']
        sub_path = pic_config['sub_path'] if 'sub_path' in pic_config else None
        subfolder = pic_config['subfolder'] if 'subfolder' in pic_config else ''

        # 拼接素材图完整路径
        template_pic_full_path = ''
        if sub_path is None:
            sub_path = os.path.join(global_var.root_path, 'template_pic')
        os.makedirs(sub_path, exist_ok=True)
        template_pic_full_path = sub_path
        if len(subfolder) > 0:
            subfolder_path = os.path.join(sub_path, subfolder)
            os.makedirs(subfolder_path, exist_ok=True)
            template_pic_full_path = subfolder_path
        exist_name = False # 标记是否存在与当前测试机匹配的"系统_分辨率"素材
        for suffix in ['.png', '.jpg', '.jpeg']:
            temp_path = os.path.join(template_pic_full_path, template_pic_full_name(name) + suffix)
            if os.path.exists(temp_path):
                exist_name = True
                template_pic_full_path = temp_path
                break
        if exist_name:
            exist_pic_config_list.append(pic_config)

    # 如果没有符合当前设备的弹窗素材，就不用轮询了、直接结束
    if len(exist_pic_config_list) == 0:
        return

    # 内部函数，控制repeat次数
    def inner_loop_clear_alert(exist_pic_config_list, timeout):
        start_time = time.time() # 开始轮询的时间
        inner_loop_count = 0 # 内循环次数（即完整的遍历一次素材组的次数，兜底2次）
        while True: # 开始轮询
            pic_full_path = screenshot()

            for i, pic_config in enumerate(exist_pic_config_list):
                name = pic_config['name']
                threshold = pic_config['threshold'] if 'threshold' in pic_config else None
                sub_path = pic_config['sub_path'] if 'sub_path' in pic_config else None
                subfolder = pic_config['subfolder'] if 'subfolder' in pic_config else ''
                act_position = pic_config['act_position'] if 'act_position' in pic_config else Position.CENTER
                priority_index = pic_config['priority_index'] if 'priority_index' in pic_config else 0
                act_mode = pic_config['act_mode'] if 'act_mode' in pic_config else ActMode.LEFT_CLICK
                filter_same = pic_config['filter_same'] if 'filter_same' in pic_config else False
                sort_rule = pic_config['sort_rule'] if 'sort_rule' in pic_config else SortRule.THRESHOLD_REVERSE
                exist_res = exist_pic(name=name, pic_full_path=pic_full_path, threshold=threshold, sub_path=sub_path, subfolder=subfolder, preview=False, priority_index=priority_index, filter_same=filter_same, sort_rule=sort_rule)
                if exist_res[0]:
                    os.remove(pic_full_path)
                    return act_point(exist_res=exist_res, act_position=act_position, priority_index=priority_index, act_mode=act_mode)

            inner_loop_count += 1
            os.remove(pic_full_path)
            duration = time.time() - start_time
            if duration > timeout and inner_loop_count >= 2:
                return None

    find_alert = False # 只记录是否找到过弹窗
    # 连续消除可能存在的repeat个弹窗
    for _ in range(repeat):
        res = inner_loop_clear_alert(exist_pic_config_list=exist_pic_config_list, timeout=timeout)
        if res is None: # 如果1个弹窗都没，就没必要再循环进行弹窗连消了
            break
        else:
            find_alert = True
    return find_alert