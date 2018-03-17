#encoding=utf-8
import os
import json
import sys
import queue
import socket
import threading
import smtplib
import pickle
from email.mime.text import MIMEText
from email.header import Header
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
from html.parser import HTMLParser

class email_sender:
    def __init__(self):
        self.connect()
    def connect(self):
        self.server=smtplib.SMTP("smtp-mail.outlook.com", 587)    
        self.server.starttls()
        self.server.login("lsy_send_kindle@outlook.com","LSYsendkindle")
    def send(self,des,path,name):
        message = MIMEMultipart()
        with open(path, 'rb') as f:
            mime = MIMEBase('application', 'octet-stream', filename=name)
            mime.add_header('Content-Disposition', 'attachment', filename=name)
            mime.add_header('Content-ID', '<0>')
            mime.add_header('X-Attachment-Id', '0')
            mime.set_payload(f.read())
            encoders.encode_base64(mime)
            message.attach(mime)
        while True:
            try: 
                self.server.sendmail("lsy_send_kindle@outlook.com", [des], message.as_string())
                break
            except:
                print("reconnecting")
                self.connect()


class loop(threading.Thread):
    runing=True
    q=queue.Queue()
    send=email_sender()
    max_cha=2250
    def run(self):
        print("start run")
        while True:
            data=None
            try:
                data=self.q.get(True,1)
            except queue.Empty:
                if not self.runing:
                    break
                pass
            else:
                print(data[0]+"start")
                f=os.popen("ebook-convert /opt/owllook/owllook.recipe /tmp/%s.mobi --no-inline-toc --mobi-file-type new --output-profile kindle_voyage"%data[0],"w")
                f.write(json.dumps(data[:-1]))
                f.close()
                print(data[0]+"end")
                self.send.send(data[-1],"/tmp/%s.mobi"%data[0],data[0]+".mobi")
                print(data[0]+"send")
    def stop(self):
        self.runing=False
        self.join()
    def add(self,title,links,address):
        count=0
        n=len(links)
        while n>count*self.max_cha:
            self.q.put(("%s第%d卷"%(title,count+1),links[count*self.max_cha:min((count+1)*self.max_cha,n)],address))
            count=count+1

class areader(HTMLParser):
    chapters=[]
    cha=None
    title=None
    def handle_starttag(self, tag, attrs):
        if tag=="a":
            for at in attrs:
                if(at[0]=='href'):
                    self.cha=at[1]
    def handle_endtag(self, tag):
        if tag=="a":
            self.chapters.append((self.title,self.cha))

    def handle_data(self, data):
        self.title=data

s=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
s.bind(('127.0.0.1', 31419))
s.listen(5)
l=loop()
l.start()
while True:
    # 接受一个新连接:
    sock, addr = s.accept()
    print("recve1")
    l.add(*pickle.loads(sock.recv(10000000)))
    print("recve2")
    sock.close()
#a=areader()
#a.feed("<a href='qqq'></a><a href='ddd'></a>")
#for i in a.chas:
#    print(i)