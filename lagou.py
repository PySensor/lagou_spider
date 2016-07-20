# coding:utf-8
import requests
from urllib import parse
import json
from bs4 import BeautifulSoup
import time
import random

s = requests.session()


class Lagou():
    def __init__(self, city, job):
        self.city = city
        self.job = job

    def get_detail_url(self, positionId):
        detail_url = 'http://www.lagou.com/jobs/' + str(positionId) + '.html'
        return detail_url

    def Get_PageNum(self):
        job_url = 'http://www.lagou.com/jobs/list_' + self.job + '?px=new&city=' + self.city + '#order'
        job_headers = {
            'Host': 'www.lagou.com',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Accept': 'Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Referer': 'http://www.lagou.com/jobs/list_' + parse.quote(self.job) +
                       '?labelWords=&fromSearch=true&suginput=',
            'Accept-Encoding': 'gzip, deflate, sdch',
            'Accept-Language': 'ja,zh-CN;q=0.8,zh;q=0.6',
            'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) '
                       'AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'
        }
        html = s.get(job_url, headers=job_headers).content
        html = html.decode('utf-8')
        soup = BeautifulSoup(html, 'html5lib')
        page_num = soup.find('span', attrs={'class': 'span totalNum'}).getText()
        return page_num

    def Get_Data(self, page_num):
        datas = []
        data_url = 'http://www.lagou.com/jobs/positionAjax.json?px=new&city=' + self.city + '&needAddtionalResult=false'
        data_headers = {
            'Host': 'www.lagou.com',
            'Connection': 'keep-alive',
            'Origin': 'http://www.lagou.com',
            'X-Anit-Forge-Code': '0',
            'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
            'Accept': 'application/json, text/javascript, */*; q=0.01',
            'X-Requested-With': 'XMLHttpRequest',
            'X-Anit-Forge-Token': 'None',
            'Referer': 'http://www.lagou.com/jobs/list_' + parse.quote(self.job) +
                       '?labelWords=&fromSearch=true&suginput=',
            'Accept-Encoding': 'gzip, deflate',
            'Accept-Language': 'ja,zh-CN;q=0.8,zh;q=0.6',
            'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) '
                       'AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'
                    }
        print('正在抓取信息，共%d页,请稍等....' % int(page_num))
        for i in range(1, int(page_num)+1):
            page_number = i
            print('正在抓取第%d页....' % page_number)
            data_params = {
                'first': 'false',
                'pn': str(page_number),
                'kd': self.job,
                }
            html = s.post(data_url, headers=data_headers, params=data_params).content
            html = html.decode('utf-8')
            content_json = json.loads(html)
            content = content_json['content']['positionResult']['result']
            datas.append(content)
            wait_time = random.randint(9, 15)
            time.sleep(wait_time)
            print('抓取完成.')
        return datas

    def analysis_data(self, data):
        content_key = ['职位id', '招聘职位', '发布时间', '薪资', '公司简称', '公司全称', '公司类型', '公司位置',
                       '位置标识', '融资情况', '公司规模', '工作经验', '学历要求', '公司特点', '岗位优势']
        content_value = ['positionId', 'positionName', 'createTime',  'salary', 'companyShortName', 'companyFullName',
                         'industryField', 'district', 'businessZones', 'financeStage', 'companySize', 'workYear',
                         'education', 'companyLabelList', 'positionAdvantage']
        detail_id = 1
        detail_url_list = []
        with open('%s_%s.txt' % (self.city, self.job), 'wt') as f:
            for item in data:
                for detail in item:
                    f.write('第%d个信息....\n' % detail_id)
                    for e, value in enumerate(content_value):
                        f.write('{}-> {}\n'.format(content_key[e], detail[value]))
                    detail_url = 'http://www.lagou.com/jobs/' + str(detail['positionId']) + '.html'
                    detail_url_list.append(detail_url)
                    detail_id += 1
                    f.write('-'*70)
                    f.write('\n')
        f.close()
        print('共有%d个信息' % len(detail_url_list))
        return detail_url_list

    def Get_Job_detail(self, url_list):
        detail_headers = {
            'Host': 'www.lagou.com',
            'Connection': 'keep-alive',
            'X-Anit-Forge-Token': '0',
            'X-Anit-Forge-Code': '0',
            'Referer': 'http://www.lagou.com/jobs/list_' + parse.quote(self.job) + '?labelWords=&fromSearch=true&suginput=',
            'Accept': '*/*',
            'Accept-Encoding': 'gzip, deflate, sdch',
            'Accept-Language': 'ja,zh-CN;q=0.8,zh;q=0.6',
            'X-Requested-With': 'XMLHttpRequest',
            'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) '
                       'AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'
        }
        while True:
            job_detail = input('请输入你感兴趣的职位顺序编号以查看招聘内容, 输入q为退出: ')
            if job_detail == 'q':
                break
            elif int(job_detail) > len(url_list) or int(job_detail) <= 0:
                print("输入的编号有误,请重新输入")
                continue
            require_html = s.get(url_list[int(job_detail)-1], headers=detail_headers).content
            require_html = require_html.decode('utf-8')
            soup = BeautifulSoup(require_html, 'html5lib')
            detail_content = soup.find('dd', attrs={'class': 'job_bt'}).getText()
            print(detail_content)


def main():
    start_time = time.time()
    city = input('input the city where you want to go: ')
    job = input('input the job param which you want: ')

    lagou = Lagou(city, job)

    page_num = lagou.Get_PageNum()

    job_data = lagou.Get_Data(page_num=page_num)

    all_job = lagou.analysis_data(data=job_data)
    all_job
    end_time = time.time()
    run_time = end_time - start_time
    print('查询完成，用时%d秒...' % run_time)
    lagou.Get_Job_detail(all_job)

if __name__ == '__main__':
    main()