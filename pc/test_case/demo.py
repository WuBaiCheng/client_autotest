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

        pass