#-*-coding:utf8;-*-
import socket, server, json,time
from threading import Thread

#TEMPROARY
DIR = "/sdcard/deneme/"
#TEMP

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

class app(object):

    def __init__(self):
        self.contents=[]
        self.filelist=[]
        self.diclist=[]
        self.ip = None
        self.port = None
        self.switch = True
        self.switch_2 = False
    
    def tel(self,data):
        return(bytes(data, "UTF-8"))
    
    def menu(self):
        print("\t1)Be a Server\n\t2)Client Mode")
        while 1:
            choice = input("\t>>")
            if choice in ["1", "2"]:
                return int(choice)
                
    def definer(self):
        self.switch = True
        self.listen_thread = Thread(target=self.listen)
        self.listen_thread.start()
    
    def connect(self):
        s.connect((self.ip, self.port))
        print("\tConnection was succesful")
        self.listen_thread = Thread(target = self.listen)
        self.listen_thread.start()  
        
    def get(self, filename):
        self.switch=False
        s.send(self.tel(json.dumps({"tag":"get", "data":filename})))
        print("Send get for {} waiting for response".format(filename))
        self.listen_thread.join()
        if self.switch_2:
            dosya = open(DIR+filename, "wb")
            data = True
            a=1
            while data:
                data = s.recv(1024)
                #this sentence is reducing performance and is going to be changed afterwards
                if data == self.tel("gg"):
                     break
                dosya.write(data)
            dosya.close()
            print("Get for {} completed saved in disk".format(filename))
        else:
            print("File was not found")       
        self.definer()
        self.switch_2 = False
        
    def listen(self):
        while self.switch:
            recv = s.recv(1024).decode("utf-8")                
            recv = json.loads(recv)
            if recv["tag"] == "info":
                if recv["data"] == "succes":
                    self.switch_2 = True
            if recv["tag"] == "contents":
                self.contents = recv["data"]
                self.filelist = []
                self.diclist = []
                for i in self.contents:
                    if self.contents[i] == "file":
                        self.filelist.append(i)
                    else:
                        self.diclist.append(i)

                
    def cmd(self):
        print("\tCommands:\nls\nkill\nget\npush\ncd")
        while 1:
            get_cmd = input(">>")
            if get_cmd == "ls":
                s.send(self.tel(json.dumps({"tag":"sync"})))
                for i in self.diclist:
                    print("> "+i)
                for i in self.filelist:
                    print("- "+i)
            elif "get" in get_cmd:
                try:
                    get_cmd = get_cmd.split(" ")
                    if len(get_cmd) >2:
                        name = " ".join(get_cmd[1:])
                    else:
                        name = get_cmd[1]
                    self.get(name)
                except IndexError:
                    print("wrong usage of get use\nget [filename] instead")
                    
        
def main():
    run = app()
    if run.menu() == 1:
        server.main()
    else:
        print("\n\tPlease enter ip and port\n\texample: localhost:1221")
        while 1:
            data = input("\t>>")
            try:
                data = data.split(":")
                ip = data[0]
                try:
                    port =data[1]
                    port =int(port)
                    break
                except ValueError:
                    print("\tinvalid port")
            except Exception as e:
                print("\tinvalid data")
        run.ip = ip
        run.port = port
        run.connect()
        t = Thread(target=run.cmd)
        t.start()
        

if __name__=="__main__":
    main()


