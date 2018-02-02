#-*-coding:utf8;-*-
import socket, server, json,time
from threading import Thread

#TODO: ADD MULTI FILE UPLOADING OR DOWNLOADING AND FILE PRINT FILE SIZES

#TEMPROARY
DIR = "/sdcard/deneme/"
#TEMP

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

class app(object):

    def __init__(self):
        self.contents=[]
        self.filelist=[]
        self.diclist=[]
        self.DIRECTORY    = ""
        self.ip = None
        self.port = None
    
    def tel(self,data):
        return(bytes(data, "UTF-8"))
    
    def menu(self):
        print("\t1)Be a Server\n\t2)Client Mode")
        while 1:
            choice = input("\t>>")
            if choice in ["1", "2"]:
                return int(choice)
                
    def definer(self):
        self.listen_thread = Thread(target=self.listen)
        self.listen_thread.start()
    
    def connect(self):
        s.connect((self.ip, self.port))
        print("\tConnection was succesful")
        self.listen_thread = Thread(target = self.listen)
        self.listen_thread.start()  
        
    def push(self, filename):
        self.get_dir()
        try:
            dosya = open(DIR+filename, "rb")
            so = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            so.connect((self.ip, self.port))
            so.send(self.tel(json.dumps({"dir":self.DIRECTORY,"tag":"push", "data":filename})))
            print("push request sent for {}".format(filename))
            if json.loads(so.recv(1024).decode("utf-8"))["data"] == "ready":
                print("push is starting")
                veri = True
                while veri:
                    veri = dosya.read()
                    so.send(veri)
                print("succesfully pushed {}".format(filename))
            dosya.close()
            so.close()
        except IOError:
            print("couldnt find {}".format(filename))
        
    def get(self, filename):
        self.get_dir()
        #we define a second socket object due to a good file transfer(otherwise it doesnt cut the transfer)
        socket_object = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        socket_object.connect((self.ip, self.port))
        socket_object.send(self.tel(json.dumps({"dir":self.DIRECTORY, "tag":"get", "data":filename})))
        print("Send get for {} waiting for response".format(filename))
        if json.loads(socket_object.recv(1024).decode("utf-8"))["data"] == "succes":
            print("contacted to server transfer is starting.")
            dosya = open(DIR+filename, "wb")
            data = True
            socket_object.send(self.tel(json.dumps({"tag":"info", "data":"ready"})))
            while data:
                data = socket_object.recv(1024)
                dosya.write(data)
            dosya.close()
            del(socket_object)
            print("Get for {} completed saved in disk".format(filename))
        else:
            print("File was not found")       
            
    def get_dir(self):
        s.send(self.tel(json.dumps({"tag":"get_dir"})))
        
    def listen(self):
        while 1:
            recv = s.recv(1024).decode("utf-8")                
            recv = json.loads(recv)
            
            if recv["tag"] == "dir":
                self.DIRECTORY = recv["data"]
            
            if recv["tag"] == "dir_info":
                if recv["data"] == "succes":
                    print("current directory changed succesfully")
                else:
                    print("couldnt change directory")
            
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
        print("\tCommands:\nls\ngetall\npushall\nget\npush\ncd")
        
        while 1:
            get_cmd = input(">>")
            
            if get_cmd == "pushall":
                #this will require some work
                pass
            
            if get_cmd == "getall":
                s.send(self.tel(json.dumps({"tag":"sync"})))
                for i in self.filelist:
                    self.get(i)
                
            
            if "cd" in get_cmd:
                if not get_cmd == "cd":
                    get_cmd = get_cmd.split(" ")
                    directory = " ".join(get_cmd[1:])
                    s.send(self.tel(json.dumps({"tag":"cd", "data":directory})))
                    
                else:
                    s.send(self.tel(json.dumps({"tag":"cd", "data":""})))
            
            if get_cmd == "ls":
                s.send(self.tel(json.dumps({"tag":"sync"})))
                for i in self.diclist:
                    print("> "+i)
                for i in self.filelist:
                    print("- "+i)
                    
                    
            elif "get" in get_cmd:
                if not get_cmd == "getall":
                    try:
                        get_cmd = get_cmd.split(" ")
                        if len(get_cmd) >2:
                            name = " ".join(get_cmd[1:])
                        else:
                            name = get_cmd[1]
                        self.get(name)
                    except IndexError:
                        print("wrong usage of get use\nget [filename] instead")
                    
                    
            elif "push" in get_cmd:
                if not get_cmd == "pushall":
                    try:
                        get_cmd = get_cmd.split(" ")
                        name = " ".join(get_cmd[1:])
                        self.push(name)
                    except IndexError:
                        print("wrong use of push use\npush [filename] instead")
                    
        
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
        s.send(run.tel(json.dumps({"tag":"sync"})))
        t = Thread(target=run.cmd)
        t.start()
        

if __name__=="__main__":
    main()


