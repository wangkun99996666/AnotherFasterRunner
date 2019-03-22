# !/usr/bin/python3
# -*- coding: utf-8 -*-

# @Author:梨花菜
# @File: ding_message.py 
# @Time : 2018/12/21 15:11
# @Email: lihuacai168@gmail.com
# @Software: PyCharm
from dingtalkchatbot.chatbot import DingtalkChatbot
import time

class DingMessage:
    """
    调用钉钉机器人发送测试结果
    """

    def __init__(self, run_type):
        self.run_type = run_type
        if run_type == 'auto':
            webhook = 'https://oapi.dingtalk.com/robot/send?access_token=998422738ca7d32f8641e9369da7f1b5545aa09c8fcec5ae17324e609c5d1af0'
        elif run_type == 'deploy':
            webhook = 'https://oapi.dingtalk.com/robot/send?access_token=16c4dbf613c5f1f288bbf695c1997ad41d37ad580d94ff1a0b7ceae6797bbc70'
        self.robot = DingtalkChatbot(webhook)

    def send_ding_msg(self,summary):
        """
        sum['details'][0]['records']
        name = sum['details'][0]['records'][0]['name']
        status = sum['details'][0]['records'][0]['status']
        url = sum['details'][0]['records'][0]['meta_data']['request']['url']
        expect = sum['details'][0]['records'][0]['meta_data']['validators'][0]['expect']
        check_value = sum['details'][0]['records'][0]['meta_data']['validators'][0]['check_value']

        :param summary:
        :return:
        """
        # summary['stat'] = {'testsRun': 2, 'failures': 1, 'errors': 0, 'skipped': 0, 'expectedFailures': 0, 'unexpectedSuccesses': 0,'successes': 1}
        rows_count = summary['stat']['testsRun']
        pass_count = summary['stat']['successes']
        fail_count = summary['stat']['failures']
        skip_row = summary['stat']['skipped']
        # base_url = summary['details'][0]['base_url']
        try:
            base_url = summary['details'][0]['in_out']['in']['report_url']
        except KeyError:
            base_url = summary['details'][0]['base_url']
        env_name = '测试' if 'test' in base_url else '生产'
        case_suite_name = summary['details'][0]['name'] # 用例集名称
        start_at = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(summary['time']['start_at']))
        duration = '%.2fs' %summary['time']['duration']
        receive_msg_mobiles = [18666126234, 13763312220, 15989041619, 18665742877, 13512756535]  # 接收钉钉消息的列表

        # 已执行的条数
        executed = rows_count
        title = '''自动化测试报告: \n开始执行时间:{2} \n消耗时间:{3} \n环境:{0} \nHOST:{1} \n用例集:{4}'''.format(env_name, base_url, start_at, duration,case_suite_name)
        # 通过率
        pass_rate = '{:.2%}'.format(pass_count / executed)

        # 失败率
        fail_rate = '{:.2%}'.format(fail_count / executed)

        # fail_count_list[0] {"name": name, "url": url, expect":[],"check_value":[]}
        fail_count_list = []

        # 失败详情
        if fail_count == 0:
            fail_detail = ''

        else:
            details = summary['details']
            print(details)
            for detail in details:
                for record in detail['records']:
                    print(record['meta_data']['validators'])
                    if record['status'] != 'failure':
                        continue
                    else:
                        url_fail = record['meta_data']['request']['url'].replace(base_url,"")
                        case_name = record['name']
                        expect = []
                        check_value = []
                        for validator in record['meta_data']['validators']:
                            expect.append(validator['expect'])
                            check_value.append(validator['check_value'])
                        # fail_count_list.append({'case_name': case_name, 'url': url_fail, 'expect':expect, 'check_value':check_value})
                        fail_count_list.append({'case_name': case_name, 'url': url_fail})

            fail_detail  = '失败的接口是:\n'
            for i in fail_count_list:
                # s = '用例名:{0} PATH:{1}\n 期望值:{2}\n 返回结果:{3} \n'.format(i["case_name"], i["url"], i["expect"], i["check_value"])
                s = '用例名:{0}\n PATH:{1}\n  \n'.format(i["case_name"], i["url"])
                fail_detail += s

        msg = '''{0}
总用例{1}共条,执行了{2}条,跳过{3}条.
通过{4}条,通过率{5}.
失败{6}条,失败率{7}.
{8}'''.format(title, rows_count, executed, skip_row, pass_count, pass_rate, fail_count, fail_rate,fail_detail)

        if fail_count == 0:
            if self.run_type == 'deploy':
                print("deploy_success")
            elif self.run_type == 'auto':
                self.robot.send_text(msg, at_mobiles=receive_msg_mobiles)
        else:
            if self.run_type == 'deploy':
                self.robot.send_text(msg, is_at_all=True)
            elif self.run_type == 'auto':
                self.robot.send_text(msg, at_mobiles=receive_msg_mobiles)


if __name__ == '__main__':
    robot = DingMessage()
    summary = {'stat':{'testsRun': 2, 'failures': 0, 'errors': 0, 'skipped': 0, 'expectedFailures': 0,
                       'unexpectedSuccesses': 0, 'successes': 1}}
    robot.send_ding_msg(summary)
