#-*-coding:utf8;-*-
import socket, server, json,time, os, sys
from threading import Thread

local_dir = os.path.dirname(os.path.realpath(__file__))+"/" #dir of code file 
try:
    config_file = local_dir+"config.conf"
    with open(config_file, "r") as dosya:
        config = json.load(dosya)
    first_run = False
            
except IOError:
    first_run = True

#TODO:YOU CAN STILL DELETE NON EXISTING CONFIG DO THE  ./ FOR CD AND LCD  AND FILE PRINT FILE SIZES


#TEMPROARY
DIR = "/sdcard/deneme/"
#TEMP

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

class app(object):

    def __init__(self):
    #these are declared early to make code clearer
        self.contents=[]
        self.filelist=[]
        self.diclist=[]
        self.DIRECTORY    = ""
        self.switch= False #this switch is used for code to wait to sycnh
        self.switch_2 = False #this switch is use for code to wait to get dir info
        self.ip = None
        self.port = None
    
    def tel(self,data):
        return(bytes(data, "UTF-8"))
    
    def menu(self):
        print("\t1)Be a Server\n\t2)Client Mode\n\t3)Delete Config(If exists).")
        while 1:
            choice = input("\t>>")
            if choice in ["1", "2", "3"]:
                if choice == "3":
                    if not first_run:
                        return int(choice)
                    else:
                        print("\n\tNo config file found")
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
        self.switch_2 = False
        self.get_dir()
        while not self.switch_2:
            pass
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
            
    def local_synch(self, DIR):
        self.local_contents = os.listdir(DIR)
        self.local_filelist = []
        self.local_dirlist = []
        for i in self.local_contents:
            if os.path.isfile(DIR+i):
                self.local_filelist.append(i)
            else:
                self.local_dirlist.append(i)
        
        
    def get(self, filename):
        self.switch_2 = False
        self.get_dir()
        while not self.switch_2:
            pass
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
                self.switch_2 = True
            
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
                self.switch = True

                
    def cmd(self):
        self.helptext ="ls    displays server's contents\nget [filename]    gets a file from server\npush [filename]    pushes a file to server\ncd [dirname]   changes dir\nlls    displays local contents\nlcd    changes local dir\ngetall    gets all files from current server dir\npushall    pushes all files in local dir to server\nsynch    synches local dir and server dir"
        print("\tCommands:\nhelp\nls\ngetall\npushall\nget\npush\ncd\nlls\nlcd\nsynch")
        
        while 1:
            get_cmd = input(">>")
            
            if "lcd" in get_cmd: #stands for local cd
                global DIR
                if not get_cmd == "lcd":
                    dirchange = get_cmd.split(" ")
                    dirchange = dirchange[1]
                    if not dirchange[-1] == "/":
                        dirchange += "/"
                    print("local dir is changed as {}".format(dirchange))
                    try:
                        os.listdir(dirchange)
                        DIR = dirchange
                        
                    except OSError:
                        print("lcd failed")
                else:
                    print("usage lcd [path]")
                        
                    
       
                    
            
            if get_cmd == "help":
                print(self.helptext)
            
            if get_cmd == "pushall":
                self.local_synch(DIR)
                for i in self.local_filelist:
                    self.push(i)
            
            if get_cmd == "synch":
                pushed = []
                pulled = []
                push_count = 0
                pull_count=0
                self.local_synch(DIR)
                self.switch = False
                s.send(self.tel(json.dumps({"tag":"sync"})))
                while not self.switch:
                    pass
                print("synch started")
                for i in self.local_filelist:
                    if not i in self.filelist:
                        self.push(i)
                        pushed.append(i)
                        push_count +=1
                for i in self.filelist:
                    if not i in self.local_filelist:
                        self.get(i)
                        pulled.append(i)
                        pull_count +=1
                        
                print("synch completed")
                print("Pushed {} object(s) in total:".format(push_count))
                for i in pushed:
                    print("> {}".format(i))
                print("Pulled {} object(s) in total:".format(pull_count))
                for i in pulled:
                    print("< {}".format(i))
                	
            
            if get_cmd == "lls":   #stands for local ls
                print("PRINTING LOCAL DIR")
                self.local_synch(DIR)
                for i in self.local_dirlist:
                    print("> "+i)
                for i in self.local_filelist:
                    print("- "+i)
                
            
            if get_cmd == "pushall":
                #this will require some work
                pass
            
            if get_cmd == "getall":
                self.switch = False               
                s.send(self.tel(json.dumps({"tag":"sync"})))
                while not self.switch: #this makes code to wait for renewing file data
                    pass
                for i in self.filelist:
                    self.get(i)
                
            
            if "cd" in get_cmd:
                if not get_cmd == "cd":
                    if  not "lcd" in get_cmd:
                        get_cmd = get_cmd.split(" ")
                        directory = " ".join(get_cmd[1:])
                        s.send(self.tel(json.dumps({"tag":"cd", "data":directory})))
                    
                if get_cmd == "cd":
                    s.send(self.tel(json.dumps({"tag":"cd", "data":""})))
            
            if get_cmd == "ls":
                self.switch = False
                s.send(self.tel(json.dumps({"tag":"sync"})))          
                while not self.switch:
                    pass
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
    menu_output = run.menu()
    if  menu_output == 1:
        server.main()
    elif menu_output == 2:
        if first_run:
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
            print("\n\twould you want to save\n\tthis data ?\n\ty or n")
            while 1:
                choice = input("\t>>")
                if choice in ["y", "n"]:
                    break
            if choice == "y":
                config = {"ip":ip, 
                                "port":port}
                with open(local_dir+"config.conf", "w") as dosya:
                    json.dump(config, dosya)
        else:
            global config
            ip = config["ip"]
            port = config["port"]
        run.ip = ip
        run.port = port
        run.connect()
        s.send(run.tel(json.dumps({"tag":"sync"})))
        t = Thread(target=run.cmd)
        t.start()
        
    elif menu_output == 3:
        os.remove(config_file)
        print("\n\tconfig file has deleted")
        sys.exit()

        

if __name__=="__main__":
    main()


