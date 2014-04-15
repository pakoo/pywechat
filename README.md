python 微信公共号框架 支持多账号

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

