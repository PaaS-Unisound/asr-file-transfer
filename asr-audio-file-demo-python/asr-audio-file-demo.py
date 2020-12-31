# coding:utf-8
import sys
#import imp
from importlib import reload
#imp.reload(sys)
#sys.setdefaultencoding('utf-8')
import json
import time,datetime
import requests
import hashlib
import urllib.request, urllib.parse, urllib.error
import os
import codecs
import logging
import uuid

ts=str(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()))
log='log'
if not os.path.exists(log):
    os.makedirs(log)

#logging.basicConfig(filename=log+'/logger_'+ts+'.log', level=print)

setName='utTest'
#测试语音list
testaudioslist='unisound.wav'
#并发数，可配置多线程并发测试
threadN=1
#单语音重复测试次数，例如：设置为N，则表示语音A会连续测试N次
times=1

#线程启动间隔
t_interval=1.2


url_yzs='http://af-asr.hivoice.cn'

#转写服务接口
url_yzs_append_upload_init=url_yzs+'/utservice/v2/trans/append_upload/init'
url_yzs_append_upload_upload=url_yzs+'/utservice/v2/trans/append_upload/upload'
url_yzs_append_upload_status=url_yzs+'/utservice/v2/trans/append_upload/status'
url_yzs_transcribe=url_yzs+'/utservice/v2/trans/transcribe'
url_yzs_text=url_yzs+'/utservice/v2/trans/text'

url_yzs_hot_data_upload = url_yzs+"/utservice/v2/trans/hot_data_upload"
url_yzs_hot_data_del = url_yzs+"/utservice/v2/trans/hot_data_del"

#接口参数
userid='unisound-python-demo'
domain='finance'
appkey='************************'
secret='************************'
#是否使用热词
usehotdata="true"
#语音格式
audiotype='wav'



#热词文件
recifile='./reci.txt'
file1='audio/unisound.wav'


#运行时变量
taskresult=''
timeresult=''

runtime_all=0
runitems_all=0
timestamp=0


textresults='./textresults'
if not os.path.exists(textresults):
    os.makedirs(textresults)

#userid签名
def makeuseridparams(appkey, userid):
    timestamp = get_timestamp();
    param_dict = {'appkey': appkey,
                  'timestamp': str(timestamp),
                  "userid": userid
                  }
    param_dict['signature'] = get_signature(param_dict)
    return param_dict

#taskid签名
def maketaskidparams(appkey, task_id):
    timestamp = get_timestamp();
    param_dict = {
        'task_id': task_id,
        'appkey': appkey,
        'timestamp': str(timestamp),
    }
    param_dict['signature'] = get_signature(param_dict)
    return param_dict

#upload接口签名
def makeappenduploaduploadparams(appkey, userid,task_id,md5,audiotype):
    print("makeappenduploaduploadparams start")
    timestamp = get_timestamp();
    print("makeappenduploaduploadparams timestamp",timestamp)
    param_dict = {
        'userid': userid,
        'task_id': task_id,
        'md5': md5,
        'audiotype': audiotype,
        'appkey': appkey,
        'timestamp': str(timestamp)
    }
    print("makeappenduploaduploadparams param_dict",param_dict)
    param_dict['signature'] = get_signature(param_dict)
    return param_dict

#transcrible接口签名
def maketranscribeparams(appkey,userid,task_id,audiotype,domain,md5,use_hot_data="false",):
    timestamp = get_timestamp();
    print("maketranscribeparams timestamp",timestamp)
    param_dict = {'userid': userid,
                  'task_id': task_id,
                  'audiotype': audiotype,
                  'domain': domain,
                  'use_hot_data': use_hot_data,
                  'md5': md5,
                  'appkey': appkey,
                  'timestamp': str(timestamp),
                  'punction': "beauty",
                  'callbackurl': ""
                  }
    param_dict['signature'] = get_signature(param_dict)
    return param_dict


#初始化上传
def append_upload_init(userid,appkey):
    try:
        url = url_yzs_append_upload_init
        param_dict = makeuseridparams(appkey, userid)
        r = send_get(url, param_dict)
        print("append_upload_init result 001",r)
        return r
    except Exception as e:
        print(e)
        return None

#整个文件上传
def append_upload_upload_byfile(userid,task_id,appkey,audiotype,file):
    try:
        md5 = getFileMd5(file)
        if not os.path.exists(file):
            print('file is not existed !')
        url = url_yzs_append_upload_upload
        print("append_upload_upload_byfile ",url)
        param_dict=makeappenduploaduploadparams(appkey, userid,task_id,md5,audiotype)
        r = send_post_file(url, param_dict,file)
        return r
    except Exception as e:
        print(e)
        return None

# 分段上传
def append_upload_upload_byChunk(userid, task_id, appkey, audiotype, file):
    try:
        url = url_yzs_append_upload_upload
        buffersize = 9600
        f = open(file, 'rb')
        r =None
        while True:
            b = f.read(buffersize)
            if not b:
                break
            md5=getDataMd5(b)
            param_dict = makeappenduploaduploadparams(appkey, userid, task_id, md5, audiotype)
            r=send_post_binary(url, param_dict, b)
            param_dict.clear()
        f.close()
        return r
    except Exception as e:
        print(e)
        return None

#获取上传文件状态
def append_upload_status(task_id,appkey):
    try:
        url = url_yzs_append_upload_status
        param_dict = maketaskidparams(appkey, task_id)
        r = send_get(url, param_dict)
        return r
    except Exception as e:
        print(e)
        return None

#开始转写
def start_tran(appkey,userid,task_id,audiotype,domain,tf,use_hot_data="false",):
    try:
        md5 = getFileMd5(tf)
        print('file is ',tf,'md5 is ',md5)
        url = url_yzs_transcribe
        param_dict=maketranscribeparams(appkey,userid,task_id,audiotype,domain,md5,use_hot_data)
        r = send_get(url, param_dict)
        return  r
    except Exception as e:
        print(str(e))
        return None

#获取转写状态或文本结果
def getText(appkey, task_id):
    try:
        url = url_yzs_text
        param_dict = maketaskidparams(appkey, task_id)
        r = send_get(url, param_dict)
        return r
    except Exception as e:
        print(e)
        return None

#通用函数--参数签名算法
def get_signature(param_dict):
    s = ""
    keys = sorted(param_dict)
    for key in keys:
        s += param_dict[key]
    s=secret+s+secret
    signature = hashlib.sha1(s.encode('utf-8')).hexdigest().upper()
    print ("get_signature end ",signature)
    return signature

def get_timestamp():
    return int(round(time.time()))

#post带签名
def send_post(url, params_with_sign):
    url_withParam=url+'?'+urllib.parse.urlencode(params_with_sign)
    req=requests.post(url_withParam)
    return req.content

#post文件带签名
def send_post_file(url, params_with_sign,file):
    print("send_post_file begin")
    url_withParam=url+'?'+urllib.parse.urlencode(params_with_sign)
    print("send_post_file ",url_withParam)
    with open(file, 'rb') as f:
        req=requests.post(url_withParam, data=f)
        return req.content
#post二进制数据带签名
def send_post_binary(url, params_with_sign,buffer):
    url_withParam=url+'?'+urllib.parse.urlencode(params_with_sign)
    HEADERS = {'Content-Type': 'application/octet-stream;charset=utf-8'}
    print(url_withParam)
    req=requests.post(url_withParam, data=buffer)
    return req.content
#get接口带签名
def send_get(url, params_with_sign):
    url_withParam=url+'?'+urllib.parse.urlencode(params_with_sign)
    req=requests.get(url_withParam)
    return req.content


#解析返回结果--errorcode
def geterrorcode(r):
    retJson = json.loads(r)
    return retJson['error_code']

#解析返回结果--taskid
def gettaskid(r):
    retJson = json.loads(r)
    if retJson['error_code'] == 0:
        return retJson['task_id']
    return None

#解析返回结果--status
def getStatus(r):
    if r is None:
        return None
    retJson = json.loads(r)
    if 'status' in retJson:
        print (retJson['status'])
        return retJson['status']

def is_json(myjson):
    try:
        json_object = json.loads(myjson)
    except ValueError as e:
      return False
    return True

#解析返回结果--asr识别结果
def getasrtxt(r):
    asrresult=''
    cnt_index=0
    if r is None:
        return None
    if is_json(r):
        retJson = json.loads(r)
        if 'results' in retJson:
            ja=retJson['results']
            cnt_index=len(ja)
            for i in ja:
                asrresult+=i['text']
                
    return asrresult,cnt_index

#解析识别结果--asr识别结果以及index
def getasrtxtwithindex(r):
    asrresult_d={}
    cnt_index=0
    if r is None:
        return None
    if is_json(r):
        retJson = json.loads(r)
        if 'results' in retJson:
            ja=retJson['results']
            for i in ja:
                asrresult_d[str(i['index'])]=i['text']
                cnt_index+=1
    return asrresult_d

#追写文件
def addtxt(f,t):
    fileObject = open(f, 'a+')
    fileObject.write(t)
    fileObject.close()

#保存文件
def saveTxt(f,t):
    fileObject = open(f, 'a+')
    fileObject.write(t)
    fileObject.close()



#上传文件函数完整过程
def append_upload(tf):
    result = append_upload_init(userid, appkey)
    print("append_upload result ",result)
    if result is None or geterrorcode(result)!=0:
        print('task_id Failed : ')
        return
    task_id=gettaskid(result)
    print("append_upload task_id ",task_id)
    result=append_upload_upload_byfile(userid,task_id , appkey,audiotype, tf)
    print("append_upload result ",result)
    if result is None or geterrorcode(result)!=0:
        print("upload file is Failed!",task_id)
        return
    task_id = gettaskid(result)
    result=append_upload_status(task_id, appkey)
    
    if result is None or geterrorcode(result)!=0:
        return
    return task_id

#保存识别结果
def writetaskresult(info):
    f = codecs.open(os.path.join(textresults,'text_'+str(time.time())), "a+", 'utf-8')
    f.writelines(info)
    f.close()

#按照taskid，开始转写语音
def dotransbytaskid(task_id_0,tf):
    text_result=''
    if task_id_0 is None:
        return None
    start_result = start_tran(appkey, userid, task_id_0, audiotype, domain,tf)
    print("dotransbytaskid start_result ",start_result)
    if start_result is None or geterrorcode(start_result)!=0:
        return None
    task_id_tmp=gettaskid(start_result)
    if task_id_tmp is None:
        writetaskresult(task_id_0 + " " + start_result+'\n')
        return None
    run = 1
    while run:
        time.sleep(5)
        text_result = getText(appkey, task_id_tmp)
        print("while getText ",text_result)
        #print text_result
        error_code=geterrorcode(text_result)
        if error_code is None or error_code!=0:
            print(text_result)
            return None
        status = getStatus(text_result)
        if status is not None and status == "done":
            run = 0
    return text_result

#完整转写服务，包括上传语音，转写语音，获取识别结果
def dotrans(tf):
    print('============dotrans start!!!')
    t0 = time.time()
    task_id = append_upload(tf)
    if task_id is None:
        return None
    runtime_upload=int((time.time() - t0)*1000)
    
    t1=time.time()
    text_result=dotransbytaskid(task_id,tf)
    runtime_trans=int((time.time() - t1)*1000)
    
    if text_result is None:
        print('task_id Failed : ',task_id,text_result)
    print(tf+'task_id : '+task_id+' upload_time:'+str(runtime_upload)+'ms trans_time :'+str(runtime_trans)+'ms')
    writetaskresult(bytes.decode(text_result))
    print('============dotrans done!!!'+task_id)
    return tf,task_id,runtime_upload,runtime_trans,text_result


#计算数据块MD5
def getDataMd5(buffer):
    myhash = hashlib.md5()
    myhash.update(buffer)
    return myhash.hexdigest()

#计算文件md5
def getFileMd5(filename):
    if not os.path.isfile(filename):
        return
    myhash = hashlib.md5()
    f = open(filename,'rb')
    while True:
        b = f.read(1024*1024)
        if not b :
            break
        myhash.update(b)
    f.close()
    return myhash.hexdigest()

if __name__ == '__main__':
    dotrans(file1)

