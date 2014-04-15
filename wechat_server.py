#/usr/bin/env python
# -*- coding: utf-8 -*-
import tornado.ioloop
import tornado.web
import tornado.template
import tornado.httpserver
from bs4 import BeautifulSoup as bs4
import time
from datetime import datetime
import hashlib

text_tmp = """
           <xml>
               <ToUserName><![CDATA[%s]]></ToUserName>
               <FromUserName><![CDATA[%s]]></FromUserName>
               <CreateTime>%s</CreateTime>
               <MsgType><![CDATA[text]]></MsgType>
               <Content><![CDATA[%s]]></Content>
               <FuncFlag>0</FuncFlag>
           </xml>
            """
img_tmp="""
        <xml>
        <ToUserName><![CDATA[%s]]></ToUserName>
        <FromUserName><![CDATA[%s]]></FromUserName>
        <CreateTime>%s</CreateTime>
        <MsgType><![CDATA[image]]></MsgType>
        <Image>
        <MediaId><![CDATA[%s]]></MediaId>
        </Image>
        </xml>
        """
item_tmp = """
    <item>
        <Title><![CDATA[%s]]></Title>
        <Description><![CDATA[%s]]></Description>
        <PicUrl><![CDATA[%s]]></PicUrl>
        <Url><![CDATA[%s]]></Url>
    </item>
           """
news_tmp = """
<xml>
    <ToUserName><![CDATA[%s]]></ToUserName>
    <FromUserName><![CDATA[%s]]></FromUserName>
    <CreateTime>%s</CreateTime>
    <MsgType><![CDATA[news]]></MsgType>
    <Content><![CDATA[]]></Content>
    <ArticleCount>%s</ArticleCount>
    <Articles>
    %s
    </Articles>
</xml>
           """


class BaseRequest(object):
    """
    微信公共号父类
    """
    def __init__(self,hander):
        self.con = hander

    def dispetch(self):
        """
        分发请求
        """
        self.userid = self.con.userid
        self.createtime = self.con.createtime
        self.msgtype = self.con.msgtype
        self.myid = self.con.myid
        self.msgid = getattr(self.con,'msgid','')
        if self.msgtype == 'text':
            self.wxtext = self.con.wxtext
            self.get_text()
        elif self.msgtype == 'location':
            self.location_x = self.con.location_x
            self.location_y = self.con.location_y
            self.location_scale = self.con.location_scale
            self.location_lable = self.con.location_lable
            self.get_location()
        elif self.msgtype == 'image':
            self.picurl = self.con.picurl
            self.get_image()
        elif self.msgtype == 'voice':
            self.mediaid = self.con.mediaid
            self.format = self.con.format
            self.get_voice()
        elif self.msgtype == 'video':
            self.mediaid = self.con.mediaid
            self.thumbmediaid = self.con.thumbmediaid
            self.get_video()
        elif self.msgtype == 'event':
            self.event = self.con.event
            self.event_key = self.con.event_key
            if self.event == 'subscribe':
                self.get_subscribe()
            elif self.event == 'unsubscribe':
                self.get_unsubscribe()
            else:
                self.get_event()

    def get_text(self):
        """
        收到文字消息
        """
        pass

    def get_location(self):
        """
        收到地理位置
        """
        pass

    def get_image(self):
        pass

    def get_voice(self):
        pass

    def get_video(self):
        pass

    def get_event(self):
        """
        得到自定义菜单事件
        """
        pass

    def get_subscribe(self):
        """
        获得用户订阅
        """
        pass

    def get_unsubscribe(self):
        """
        用户取消订阅
        """
        pass

    def new_artical(self):
        self.con.new_artical()

    def send_text(self,text):
        """
        回复文字消息
        """
        self.con.send_text(text)
    def send_artical(self,title,desc,picurl,url):
        """
        回复文章
        """
        self.con.send_artical(title,desc,picurl,url)
    def send_artical_list(self,item_info_list):
        """
        回复多篇文章
        """
        self.con.send_artical_list(item_info_list)

class TestApp(BaseRequest):
    """
    公共号实例，一个公共号一个实例，只需要实现需要的功能就行,具体接受的消息类型见父类
    """
    def get_text(self):
        """
        当测试app收到微信的文字消息时,do something 
        """
        if self.wxtext == '1':
            #如果收到 '1'
            self.send_text('1')#回复1

    def get_location(self):
        """
        收到地理位置消息
        """
        self.send_artical('test','test','http://a.jpg','http://qq.com')

    def get_subscribe(self):
        self.send_text(u'欢迎订阅')
        

    def get_event(self):
        if self.event_key == 'key1':
            self.send_text('1')#回复1
        elif self.event_key == 'key2':
            self.send_text('1')#回复1

class WeChatHandler(tornado.web.RequestHandler):
    """
    微信父类
    """
    def prepare(self):
        self.app_list = {
                'gh_c941312d18f7':{'handler':TestApp,'token':'test_token'},
            }
        print '\n\n>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>'
        print 'request:',self.request
        print 'body:',self.request.body
        print '>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>'
        if self.request.method == 'POST':
            soup = bs4(self.request.body,'xml')
            self.userid  = soup.FromUserName.string
            self.createtime = soup.CreateTime.string
            self.msgtype = soup.MsgType.string
            self.myid = soup.ToUserName.string
            if soup.MsgId:
                self.msgid = soup.MsgId.string
            if self.msgtype == 'text':
                self.wxtext = soup.Content.string
            elif self.msgtype == 'location':
                self.location_x = float(soup.Location_X.string)
                self.location_y = float(soup.Location_Y.string)
                self.location_scale = soup.Scalestring
                self.location_lable = soup.Label.string
            elif self.msgtype == 'image':
                self.picurl = soup.PicUrl.string
            elif self.msgtype == 'event':
                self.event = soup.Event.string
                self.event_key = soup.EventKey.string
            elif self.msgtype == "voice":
                self.mediaid = soup.MediaId.string
                self.format = soup.Format.string
            elif self.msgtype == "video":
                self.mediaid = soup.MediaId.string
                self.thumbmediaid = soup.ThumbMediaId.string
        else:
            logging.info('request:%s'%self.request)

    def get(self):
        """
        验证服务器
        """
        logging.info('arguments:%s'%str(self.get_arguments('echostr','')))
        self.finish(self.get_argument('echostr',''))

    def post(self):
        """
        接收微信消息
        """
        appclass = self.app_list[self.myid]['handler']#根据ToUserName加载对应的app
        self.app_token = self.app_list[self.myid]['token'] 

        if self.check_signature():
            appobject = appclass(self)
            appobject.dispetch()
        else:
            self.finish('fuck')

    def new_artical(self,title,desc,picurl,url):
        """
        生成文章xml
        """
        res = item_tmp%(title,desc,picurl,url)
        return res
    
    def send_text(self,text):
        """
        回复消息
        """
        line = text_tmp%(self.userid,self.myid,int(time.time()),text)
        self.finish(line)

    def send_artical(self,title,desc,picurl,url):
        """
        发送单篇文章
        """
        item_info = self.new_artical(title,desc,picurl,url) 
        artical_list = news_tmp%(self.userid,self.myid,int(time.time()),1,item_info)
        self.finish(artical_list)

    def send_artical_list(self,item_info_list):
        """
        发送多篇文章
        """
        item_content = ''.join([self.new_artical(*item) for item in item_info_list])
        artical_list = news_tmp%(self.userid,self.myid,int(time.time()),len(item_info_list),item_content)
        self.finish(artical_list)

    def check_signature(self):
        """
        验证消息是否来自微信
        """
        timestamp = self.get_argument('timestamp')
        nonce = self.get_argument('nonce')
        signature = self.get_argument('signature')
        a = [self.app_token,timestamp,nonce]
        code = hashlib.sha1(''.join(sorted(a))).hexdigest()
        if code == signature:
            return True

        

class Application(tornado.web.Application):
    def __init__(self):
        app_settings={
            'debug':True,
        }
        handlers = [
            (r'/',WeChatHandler),
        ]
        tornado.web.Application.__init__(self,handlers,**app_settings)

if __name__ == '__main__':
    http_server = tornado.httpserver.HTTPServer(request_callback=Application())
    http_server.listen(80)
    tornado.ioloop.IOLoop.instance().start()
