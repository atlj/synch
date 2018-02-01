#-*-coding:utf8;-*-
import socket, os,json,time
from threading import Thread
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

#------TEMPRORARY------
#                                             #
DIR = "/sdcard/home/"           #
#                                             #
#------TEMPRORARY------

os.system("clear")
class server(object):
    def __init__(self, ip, port):
        self.ip = ip
        self.port = port
        self.clients = []
        self.content_dic = {}
        self.threadpool=[]
        self.binder()
        
    def binder(self):
        s.bind((self.ip, self.port))
        s.listen(4)
        
    def create_thread(self, count):
        for i in range(count):
            thr = Thread(target=self.accept)
            thr.start()
            self.threadpool.append(thr)
        
    def sync_contents(self):
        self.contents = os.listdir(DIR)
        self.content_dic = {}
        for i in self.contents:
            if os.path.isfile(DIR+i):
                tip = "file"
            else:
                tip = "dir"
            self.content_dic[i]=tip
        

    def tel(self,value):
        return bytes(value, "UTF-8")
        

    def sync(self,c):
        self.sync_contents()
        c.send(self.tel(json.dumps({"tag":"contents","data":self.content_dic})))

    def accept(self):
        c, addr = s.accept()
        self.clients.append(c)
        print(addr,"has just connected")
        while 1:
            try:
                received = c.recv(1024).decode("utf-8")
                received = json.loads(received)
                if received["tag"] == "push":
                    filename = received["data"]
                    dosya = open(DIR+filename, "wb")
                    c.send(self.tel(json.dumps({"tag":"info", "data":"ready"})))
                    data = True
                    while data:
                        data = c.recv(1024)
                        dosya.write(data)
                    dosya.close()
                    print("push completed")
                if received["tag"] == "sync":
                    self.sync(c)
                if received["tag"] == "get":
                    try:
                        dosya = open(DIR+received["data"], "rb")
                        c.send(self.tel(json.dumps({"tag":"info","data":"succes"})))
                        if json.loads(c.recv(1024).decode("utf-8"))["data"] == "ready":
                            print("get with", addr, "started")
                            l = dosya.read(1024)
                            while l:
                                c.send(l)
                                l = dosya.read(1024)
                            print("get complete")
                            dosya.close
                            c.close()
                    except Exception as e:
                        print("couldnt find file")
                        c.send(self.tel(json.dumps({"tag":"info","data":"fail"})))
            except Exception as e:
                print("user {} has disconnected".format(addr))  
                self.create_thread(1)
                break       

                
def main():
    global serv
    print("\n\tPlease enter ip and port\n\texample: localhost:1221\n")
    while 1:
        adress = input("\t>>")
        try:
            ip = adress.split(":")[0]
            port = adress.split(":")[1]   
            try:
                port = int(port)
                break
            except ValueError:
                print("\tport is not valid")
        except Exception as e:
            print("\twrong entry")
        
                    
    serv = server(ip, port)
    serv.create_thread(32)    
    print("listening for connections")



if __name__ == "__main__":
    main()



