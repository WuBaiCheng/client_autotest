import os

'''
项目根目录完整路径，可重设
默认为本global_var.py文件所在文件夹的完整路径 os.path.dirname(__file__)

形如：
/Users/wubocheng/Desktop/DTClientAutotest/DTClientAutotest
/Library/Frameworks/Python.framework/Versions/3.9/lib/python3.9/site-packages/DTClientAutotest

DTClientAutotest会根据root_path来创建一些默认的文件夹，如：
存放截图的文件夹 screenshot
存放模板截图的文件夹 template_pic
存放OCR识别的文字缓存图的文件夹 pic_cache_for_text
'''
root_path = os.path.dirname(__file__)

'''
分辨率尺寸与绝对尺寸存在换算比例scale，默认情况下win都是1、mac都是2

举个例子：
通过接口exist_text或exist_pic最终都是为了拿到一个要交互的点point(x,y)，
而这个point里的x和y都是基于分辨率的尺寸计算出来的。
而实际进行交互用的是绝对尺寸，即win用的是point(x,y)、mac用的是point(x/2,y/2). 
但存在一些特殊情况，比如MacBook Air的scale就不是2而是1，
所以需要通过uuid_resolution_scale_dict字典来描述这些特殊PC设备的uuid和scale的映射关系，
形如{'1c36bb14890a':1, '7ed9bb7f5b80':2}

当然如果某台PC设备的uuid没描述在这个字典里的话、那DTClientAutotest就会按默认策略来：
即这台PC设备系统是win的话scale就为1、这台PC设备系统是mac的话scale就为2
'''
uuid_resolution_scale_dict = {}

'''
只杀标准钉、不杀阿里钉的PC设备uuid白名单列表，默认为空数组
'''
skip_aliding_uuids = []

# OpenCV模板匹配相关全局变量
threshold = 0.7 # 图片模板匹配时的相似度阈值，范围为(0,1)，越接近1表示相似度要求越高
cache_threshold = 0.91 # 全局默认的缓存图相似度阈值
loop_exist_pic_before = 0 # 第一次轮询前等待的秒数（仅对OpenCV模板匹配生效）
loop_exist_pic_timeout = 10 # 轮询的最大超时秒数（仅对OpenCV模板匹配生效）
loop_exist_pic_interval = 0 # 在未轮询超时的情况下，且未轮询到目标区域时的轮询间隔秒数（仅对OpenCV模板匹配生效）
loop_exist_pic_after = 0 # 在未轮询超时的情况下，且轮询到目标区域后等待的秒数（仅对OpenCV模板匹配生效）

# OCR文字识别相关全局变量
loop_exist_text_before = 0 # 第一次轮询前等待的秒数（仅对OCR文字识别生效）
loop_exist_text_timeout = 35 # 轮询的最大超时秒数（仅对OCR文字识别生效）
loop_exist_text_interval = 0 # 在未轮询超时的情况下，且未轮询到目标区域时的轮询间隔秒数（仅对OCR文字识别生效）
loop_exist_text_after = 0 # 在未轮询超时的情况下，且轮询到目标区域后等待的秒数（仅对OCR文字识别生效）

######################################################################################################

# 移动端系统，'android' / 'ios'
mobile_system = None
# 移动端udid
mobile_udid = None
# 移动端待启动APP包名
mobile_package = None