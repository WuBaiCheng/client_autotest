from pc.common.test_base import *

class TestDemo(TestBase):
    '''
    class必须以Test开头
    '''

    def setup(self):
        '''
        每个case执行前执行的函数
        :return:
        '''

        super().setup()
        time.sleep(5)

    def teardown(self):
        '''
        每个case执行后执行的函数
        :return:
        '''

        super().teardown()

    @case_info(case_name='测试case', platform='win', module_name='测试模块', author='351723', aone_id='00000000', account=['99044445253'], priority='P0')
    def test_00000000(self):
        '''
        case必须以test开头
        :return:
        '''

        # wu todo: 注意运行case时，在将PyCharm最小化后，不能再用鼠标再点击桌面、否则会无法自动化
        pc.loop_act_pic('search', subfolder='xin_cheng/demo')
        pc.loop_act_text_by_pic_cache('命令提示符') # wu todo: 分辨率过大的电脑，OCR有时不太识别的出小字、建议少用