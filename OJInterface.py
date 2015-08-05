#coding=utf-8
import sys
assert sys.version[0]!='2', 'Please Use Python3'

import urllib.request
import urllib.parse
import bs4
import time
import socket
import base64


class Accepted(Exception):
    pass

class Error(Exception):
    def __init__(self,s):
        self.s=s
    def __str__(self):
        return self.s
    def __repr__(self):
        return self.s

WA,TLE,MLE,RE,OLE=0,1,2,3,4


class POJ:
    default_var='''{
    "username":"",
    "password":"",
    "problem":1000
}'''
    
    _status={
        'Waiting':-3,
        'Compiling':-2,
        'Running & Judging':-1,
        'Accepted':0,
        'Wrong Answer':1,
        'Time Limit Exceeded':2,
        'Memory Limit Exceeded':3,
        'Runtime Error':4,
        'Output Limit Exceeded':5,
        'Compile Error':6,
        'Presentation Error':7,
    }
    _standard=[None,WA,TLE,MLE,RE,OLE]
    _last_submit=0
    _FUCK_POJ={
        'User-Agent':'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/45.0.2414.0 Safari/537.36',
        'Referer':'http://poj.org/status',
        'Accept-Language':'zh-CN,zh;q=0.8,en;q=0.6',
        'Content-Type':'application/x-www-form-urlencoded',
    }
    
    def __init__(self,log,config):
        self.username,self.password,self.problem=\
            config['username'],config['password'],config['problem']
        self.log=log
        log('正在以 %s 登录... '%self.username)
        
        cookie=urllib.request.HTTPCookieProcessor()
        self.opener=urllib.request.build_opener(cookie)
        
        result=self.opener.open(urllib.request.Request(
            url='http://poj.org/login',
            data=urllib.parse.urlencode({
                'user_id1':self.username,
                'password1':self.password,
                'B1':'login',
                'url':'/',
            }).encode(),
            headers=self._FUCK_POJ
        )).read()
        if b'Log Out</a>' not in result:
            log(result)
            raise Error('登录失败.')
        else:
            log('登录成功.\n')

    def _submit(self,source):
        delta=self._last_submit+3-time.time()+.1
        if delta>0:
            self.log('提交前延时 %.3f 秒... '%delta)
            time.sleep(delta)
        
        self.log('正在提交... ')
        result=self.opener.open(urllib.request.Request(
            url='http://poj.org/submit',
            data=urllib.parse.urlencode({
                'problem_id':self.problem,
                'language':'4',
                'source':base64.b64encode(source.encode()),
                'submit':'Submit',
                'encoded':'1',
            }).encode(),
            headers=self._FUCK_POJ
        )).read()
        if b'Problem Status List</font>' not in result:
            try:
                response=bs4.BeautifulSoup(result)
                delay=float(response.find('font',attrs={'size':'5'}).text\
                    .partition('ms')[0].rpartition(' ')[2])
                raise Error('需要延迟 %s 毫秒,建议稍后再试.'%delay)
            except:
                self.log(result)
                raise Error('提交失败')
        else:
            self._last_submit=time.time()
            self.log('提交成功\n')

    def _query(self):
        self.log('查询中... ')
        response=bs4.BeautifulSoup(self.opener.open(urllib.request.Request(
            url='http://poj.org/status?problem_id={p}&user_id={u}&language=4'\
                .format(p=self.problem,u=self.username),
            headers=self._FUCK_POJ)).read(),'html5lib')
        try:
            return self._status[response.find(attrs={'class':'in'})\
                    .nextSibling.nextSibling.find('font').text.strip()]
        except:
            try:
                delay=float(response.find('font',attrs={'size':'5'}).text\
                    .partition('ms')[0].rpartition(' ')[2])
                raise Error('需要延迟 %s 毫秒,建议稍后再试.'%delay)
            except:
                self.log('HTML是:\n')
                self.log(str(response))
                raise Error('查询失败.')

    def update(self,source):
        self._submit(source)
        time.sleep(1)
        try:
            for _ in range(20):
                time.sleep(1.6)
                result=self._query()
                if result==0:
                    raise Accepted()
                elif result==self._status['Compile Error']:
                    raise Error('编译错误')
                elif result==self._status['Presentation Error']:
                    self.log('格式错误,视为结果错误. ')
                    return self._standard[self._status['Wrong Answer']]
                elif result>0:
                    self.log(self._standard[result])
                    return self._standard[result]
            raise Error('超时')
        finally:
            try:
                self.log('结果是 %s\n'%result)
            except:
                pass


class Hust:
    default_var='''{
"username":"",
"password":"",
"problem":1000,
"url":"http://hustoj.sinaapp.com"
}'''
    
    _last_submit=0
    
    def __init__(self,log,config):
        self.username,self.password,self.problem,self.url=\
            config['username'],config['password'],config['problem'],config['url']
        self.log=log
        if self.url.endswith('/'):
            self.url=self.url[:-1]
        if '://' not in self.url:
            self.url='http://'+self.url
        log('正在以 %s 登录... '%self.username)
        
        cookie=urllib.request.HTTPCookieProcessor()
        self.opener=urllib.request.build_opener(cookie)
        
        result=self.opener.open(urllib.request.Request(
            url='%s/login.php'%self.url,
            data=urllib.parse.urlencode({
                'user_id':self.username,
                'password':self.password,
                'submit':'Submit',
            }).encode(),
        )).read()
        if b'history.go(-2);' not in result:
            log(result)
            raise Error('登录失败.')
        else:
            #set language
            self.opener.open(urllib.request.Request(
                url='%s/setlang.php?lang=cn'%self.url,
            ))
            log('登录成功.\n')

    def _submit(self,source):
        delta=self._last_submit+10-time.time()+.05
        if delta>0:
            self.log('提交前延时 %.3f 秒...'%delta)
            time.sleep(delta)
        
        self.log('正在提交... ')
        result=self.opener.open(urllib.request.Request(
            url='%s/submit.php'%self.url,
            data=urllib.parse.urlencode({
                'id':self.problem,
                'language':'1',
                'source':source,
            }).encode(),
        )).read()
        if b'<form id=simform action="status.php" method="get">' not in result:
            self.log(result)
            raise Error('提交失败.')
        else:
            self._last_submit=time.time()
            self.log('提交成功.\n')

    def _query(self):
        def _proc(s):
            if '编译错' in s:
                raise Error('Compile Error')
            elif '答案错' in s:
                return WA
            elif '格式' in s:
                self.log('Presentation Error')
                return WA
            elif '时间' in s:
                return TLE
            elif '内存' in s:
                return MLE
            elif '输出' in s:
                return OLE
            elif '正确' in s:
                raise Accepted()
            elif '运行错' in s:
                return RE
            elif ('等' in s) or ('中' in s) or ('运行并' in s):
                return -1
            else:
                self.log(s)
                raise Error('不被识别的状态')
        
        self.log('查询中... ')
        response=bs4.BeautifulSoup(self.opener.open(urllib.request.Request(
            url='{url}/status.php?problem_id={p}&user_id={u}&language=1&jresult=-1'\
                .format(url=self.url,p=self.problem,u=self.username),
            )).read(),'html5lib')
        try:
            return _proc(response.findAll('tbody')[-1].\
                find(lambda x:x.name=='tr' and ((not x.has_attr('class')) or x['class']!=['toprow']))\
                .findAll('td')[3].text)
        except Exception as e:
            if isinstance(e,(Error,Accepted)):
                raise
            else:
                self.log('HTML是:')
                self.log(str(response))
                raise Error('查询失败.')

    def update(self,source):
        self._submit(source)
        for _ in range(40):
            time.sleep(1)
            result=self._query()
            if result>=0:
                self.log('结果是 %s\n'%result)
                return result
        raise Error('超时')


class Sock:
    default_var='''{
"host":"127.0.0.1",
"port":0,
"cls":50
}'''
    
    def __init__(self,log,config):
        self.port=int(config['port'])
        self.host=config['host']
        self.cls=config.get('cls',50)
        self.log=log
        log('请在 %s 上绑定 %d 端口\n'%(self.host,self.port))
        try:
            s=socket.socket()
            s.connect((self.host,self.port))
            s.send(b'[SocketOJ Connected]\n')
        except Exception as e:
            log(e)
            raise Error('连接远端失败')
        else:
            self.s=s

    def update(self,source):
        try:
            self.log('正在发送代码... ')
            self.s.send(b'\n'*self.cls)
            self.s.send(b'[PLEASE JUDGE]\n')
            self.s.send(source.encode())
            self.log('已发送，请在远端输入结果... ')
            while True:
                self.s.send(b'\n[WA,TLE,MLE,RE,OLE,AC,ERR]: ')
                result=self.s.recv(4096).decode('utf-8',errors='ignore').rstrip()
                if result.upper()=='AC':
                    raise Accepted()
                elif result.upper().startswith('ERR'):
                    raise Error(result[3:].lstrip())
                elif result.upper() in ['WA','TLE','MLE','RE','OLE']:
                    self.log('结果是 %s\n'%result.upper())
                    return eval(result.upper())
                else:
                    self.s.send(b'Unsupported Result.')
        except Exception as e:
            if not isinstance(e,(Error,Accepted)):
                self.log(e)
                raise Error('数据传输失败')
            else:
                raise


valid_ojs={
    'POJ':POJ,
    'HustOJ':Hust,
    'SocketOJ':Sock,
}

