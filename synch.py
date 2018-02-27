#-*-coding:utf8-*-
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

#TODO ADD DELDIR AND MKDIR

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

class app(object):
    global DIR #coding error we will fix this later.

    def __init__(self):
    #these are declared early to make code clearer
        self.contents=[]
        self.filedic = {}
        self.diclist=[]
        self.DIRECTORY    = ""
        self.switch= False #this switch is used for code to wait to sycnh
        self.switch_2 = False #this switch is use for code to wait to get dir info
        self.switch_3 = False #this switch is for get_cmd
        self.switch_4 = False #this is going to be use in get_cmd as well
        self.switch_5 = False #used in get func
        self.switch_6 = False # used in push func
        self.ip = None
        self.port = None
        self.script_mode = False
       


    def tel(self,data):
        return(bytes(data, "UTF-8"))
    
    def menu(self):
        print("\n\t1)Be a Server\n\t2)Client Mode\n\t3)Delete Config(If exists).\n\t4)Delete Server Config\n\t5)Run Predefined")
        
        while 1:
            choice = input("\t>>")
            
            if choice in ["1", "2", "3", "4", "5"]:
                
                if choice == "1" or choice == "2" or choice == "5":
                    return(int(choice))
                
                if choice == "3":
                    if not first_run:
                        return int(choice)
                    
                    else:
                        print("\tNo config file found")
                if choice == "4":
                    if not server.first_run:
                        return int(choice)
                        
                    else:
                        print("\tNo config file found")
                
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
        self.switch_6 = True
            
    def bcount(self, number):
        gig = 0#Gigabyte
        mib = 0#Megabyte
        kib = 0#Kilobyte
        b = number#byte
        #this section is going to be coded in a really dumb way sorry for this will fixed in next commits
        gib = b/(1024**3)
        mib = b/(1024**2)
        kib = b/1024

        if int(gig) == 0:
            if int(mib) == 0:
                if int(kib) == 0:
                    return str(b) + " bytes"
                return self.floatize(str(kib)) + " kB"
            return self.floatize(str(mib)) + " mB"
        return self.floatize(str(gib)) + " gB"
        
    def floatize(self, value):
        splitted = value.split(".")
        q = splitted[0]
        f = splitted[1]
        if len(f)>1:
            f = "".join(f[:2])
            return q+","+f
        return q+","+f
        

    def local_synch(self, DIR):
        self.local_contents = os.listdir(DIR)
        self.local_filedic = {}
        self.local_dirlist = []
        
        for i in self.local_contents:
            if os.path.isfile(DIR+i):
                size = os.path.getsize(DIR+i) 
                self.local_filedic[i]= size
            
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
        response = json.loads(socket_object.recv(1024).decode("utf-8"))
        if response["data"] == "succes":
            print("contacted to server transfer is starting.")
            dosya = open(DIR+filename, "wb")
            data = True
            socket_object.send(self.tel(json.dumps({"tag":"info", "data":"ready"})))
            
            while data:
                try:
                    data = socket_object.recv(1024)
                    dosya.write(data)
                except ValueError:
                    pass
            
            dosya.close()
            del(socket_object)
            print("Get for {} completed saved in disk".format(filename))
        
        else:
            print("File was not found")
        self.switch_5 = True
            
    def get_dir(self):

        s.send(self.tel(json.dumps({"tag":"get_dir"})))

    def listen(self):
        while 1:
            try:
                recv = s.recv(1024**2).decode("utf-8")
                recv = json.loads(recv)
            except ValueError:
                print("connection down")
                break
            
            if recv["tag"] == "dir":
                self.DIRECTORY = recv["data"]
                self.switch_2 = True
            
            if recv["tag"] == "dir_info":
                if recv["data"] == "succes":
                    print("succesfully changed directory")
                
                else:
                    print("failed to change directory")
                s.send(self.tel(json.dumps({"tag":"sync"})))
            
            if recv["tag"] == "contents":
                self.contents = recv["data"]
                self.filedic = {}
                self.diclist = []
                for i in self.contents:
                    if self.contents[i]["type"] == "file":
                        self.contents[i]["easysize"] = self.bcount(self.contents[i]["size"])
                        self.filedic[i] = self.contents[i] 
                    
                    else:
                        self.diclist.append(i)
                self.switch = True

    def cmd(self):
        global DIR
#------------------------------
        self.helptext ="ls    displays server's contents\ncd [path]   changes dir\nget [filename]    gets a file from server\npush [filename]    pushes a file to server\nlls    displays local contents\nlcd [path]   changes local dir\ngetall    gets all files from current server dir\npushall    pushes all files in local dir to server\nsynch    synches local dir and server dir"
#------------------------------        
        self.tr_helptext = "ls    sunucudaki dosyalari listeler\ncd [yol]    sunucunun calistigi dizini degistirir\nget [dosya adi]   sunucudan dosya ceker\npush [dosya adi]    sunucuya dosya yukler\nlls    yerel dosyalari listeler\nlcd [yol]   yerel calisma dizinini degistirir\ngetall    sunucu calisma dizinindeki tum dosyalari yerel dizine aktarir\npushall    yerel calisma dizinindeki tum dosyalari sunucuya aktarir\nsynch    yerel dizindeki ve sunucu dizinindeki dosyalari esler"
#------------------------------        
        
        if not self.script_mode:
            print("\tCommands:\nhelp\ntrhelp\nls\ngetall\npushall\nget\npush\ncd\nlls\nlcd\nsynch")
        while 1:
            if not self.script_mode:
                self.get_cmd = input(">>")
            
            else:
                while not self.switch_4:
                    pass
                self.switch_4 = False
                if type(self.get_cmd) == list:
                    self.get_cmd = " ".join(self.get_cmd)

            if self.get_cmd == "trhelp":
                print(self.tr_helptext)
            
            if "lcd" in self.get_cmd: #stands for local cd
                
                try:
                    dirchange = self.get_cmd.split(" ")
                    dirchange = " ".join(dirchange[1:])
                    
                    if not dirchange[-1] == "/":
                        dirchange += "/"
                    
                    if "".join(dirchange[:2]) == "./":
                        dirchange = "".join(dirchange[2:])
                        dirchange = DIR + dirchange
                    
                    try:
                        os.listdir(dirchange)
                        DIR =dirchange
                        print("local dir is changed as {}".format(DIR))
                    
                    except OSError:
                        print("lcd failed")
                
                except IndexError:
                    print("usage: lcd [path]")    
                        
            if self.get_cmd == "help":
                print(self.helptext)
            
            if self.get_cmd == "pushall":
                self.local_synch(DIR)
                for i in self.local_filedic:
                    self.switch_6 = False
                    self.push(i)
                    while not self.switch_6:
                        pass
            
            if "synch" in self.get_cmd :
                synchmode = "normal"
                if not self.get_cmd == "synch":
                    arg = self.get_cmd.split(" ")[1]
                    if arg in ["push", "pull", "abort"]:
                        synchmode = arg
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
                
                for i in self.local_filedic:
                   inp = "normal"
                   try:
                       if not self.local_filedic[i]==self.filedic[i]["size"]:
                           if synchmode == "abort":
                               continue
                           if synchmode == "normal":
                               print("Detected dismatched file:{}\nselect an option push/pull/abort".format(i))
                               while 1:
                                   inp = input(">>")
                                   if inp in ["push", "pull", "abort"]:
                                       break
                                       
                           if inp == "push" or synchmode == "push":
                               self.switch_6 = False
                               self.push(i)
                               while not self.switch_6:
                                   pass
                               pushed.append(i)
                               push_count += 1
                               continue
                               
                           if inp == "pull" or synchmode == "pull":
                               self.switch_5 = False
                               self.get(i)
                               while not self.switch_5:
                                   pass
                               pulled.append(i)
                               pull_count += 1
                               continue
                               
                           if inp == "abort":                          
                               continue
                
                   except KeyError:
                        self.switch_6 = False
                        self.push(i)
                        while not self.switch_6:
                            pass
                        pushed.append(i)
                        push_count +=1
                        
                self.local_synch(DIR)
                self.switch=False
                s.send(self.tel(json.dumps({"tag":"sync"})))
                while not self.switch:
                    pass
                
                
                for i in self.filedic:
                    if not i in self.local_filedic:
                        self.switch_5 = False
                        self.get(i)
                        while not self.switch_5:
                            pass
                        pulled.append(i)
                        pull_count +=1
                        
                print("synch completed")
                print("Pushed {} object(s) in total:".format(push_count))
                
                for i in pushed:
                    print("> {}".format(i))
                
                print("Pulled {} object(s) in total:".format(pull_count))
                
                for i in pulled:
                    print("< {}".format(i))
                	
            if self.get_cmd == "lls":   #stands for local ls
                print("PRINTING LOCAL DIR")
                self.local_synch(DIR)
                
                for i in self.local_dirlist:
                    print("> "+i)
                
                for i in self.local_filedic:
                    num = 30-len(i)
                    if num<0:
                        num = 10
                    print("- "+i+num*" "+self.bcount(self.local_filedic[i]))
                
            if self.get_cmd == "pushall":
                #this will require some work
                pass
            
            if self.get_cmd == "getall":
                self.switch = False               
                s.send(self.tel(json.dumps({"tag":"sync"})))
                
                while not self.switch: #this makes code to wait for renewing file data
                    pass
                
                for i in self.filedic:
                    self.switch_5 = False
                    self.get(i)
                    while not self.switch_5:
                        pass
            
            if "cd" in self.get_cmd:
                if not self.get_cmd == "cd":
                    
                    if  not "lcd" in self.get_cmd:
                        try:
                            self.get_cmd = self.get_cmd.split(" ")
                            directory = " ".join(self.get_cmd[1:])
                            s.send(self.tel(json.dumps({"tag":"cd", "data":directory})))
                            continue
                        except IndexError:
                            print("usage: cd [path]")

                if self.get_cmd == "cd":
                    s.send(self.tel(json.dumps({"tag":"cd", "data":""})))
            
            if self.get_cmd == "ls":
                self.switch = False
                s.send(self.tel(json.dumps({"tag":"sync"})))          
                
                while not self.switch:
                    pass
                
                for i in self.diclist:
                    print("> "+i)
                
                for i in self.filedic:
                    num = 30-len(i)
                    if num < 0:
                        num = 10
                    print("- "+ i +num*" "+self.filedic[i]["easysize"])
                    
            elif self.get_cmd.split(" ")[0] == "get":
                if not self.get_cmd == "getall":
                    
                    try:
                        self.get_cmd = self.get_cmd.split(" ")
                        
                        if len(self.get_cmd) >2:
                            name = " ".join(self.get_cmd[1:])
                        
                        else:
                            name = self.get_cmd[1]
                        self.switch_5 = False
                        self.get(name)
                        while not self.switch_5:
                            pass
                    
                    except IndexError:
                        print("wrong usage of get use\nget [filename] instead")
                    
            elif self.get_cmd.split(" ")[0] == "push":
                if not self.get_cmd == "pushall":
                    
                    try:
                        self.get_cmd = self.get_cmd.split(" ")
                        name = " ".join(self.get_cmd[1:])
                        self.switch_6 = False
                        self.push(name)
                        while not self.switch_6:
                            pass
                    
                    except IndexError:
                        print("wrong use of push use\npush [filename] instead")
            self.switch_3 = True
               
class predefined(object):

    def loadfile(self, filename):
        try:
            with open(local_dir+filename, "r") as dosya:
                self.data = dosya.read()
                return True

        except IOError:
            return False

    def parse(self):
        self.lines = self.data.split("\n")
        self.result = {}
        self.command_list = []

        for i in self.lines:
            tokens = i.split(" ")
            if tokens[0] == "connect":
                self.result["connect"] = tokens[1]

            elif tokens[0] == "dir":
                self.result["dir"] = tokens[1]

            else:
                if not i == "":
                    self.command_list.append(i)

        self.result["cmd"] = self.command_list
        return self.result




def main():
    global config, DIR
    run = app()
    menu_output = run.menu()
    
    if  menu_output == 1:
        server.main()
    
    elif menu_output == 2:
        if first_run:
            print("\tPlease define client directory\n\texample: /home")
            
            while 1:
                girdi = input("\t>>")
                
                if not girdi[-1] == "/":
                    girdi += "/"
                
                try:
                    os.listdir(girdi)
                    break
                
                except OSError:
                    print("\tPlease enter a valid dir")
            
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
                          "port":port,
                          "dir":girdi}
                with open(local_dir+"config.conf", "w") as dosya:
                    json.dump(config, dosya)
        
        else:
            ip = config["ip"]
            port = config["port"]
            girdi = config["dir"]
        DIR= girdi
        run.ip = ip
        run.port = port
        try:
            run.connect() 
        except socket.error:
            print("\tCan't find server")
            sys.exit()
        s.send(run.tel(json.dumps({"tag":"sync"})))
        t = Thread(target=run.cmd)
        t.start()
        
    elif menu_output == 3:
        os.remove(config_file)
        print("\n\tconfig file has deleted")
        sys.exit()
        
    elif menu_output == 4:
        os.remove(local_dir + "servconf.conf")
        print("\n\tserver config has deleted")
        sys.exit()

    elif menu_output == 5:
        func = predefined()
        if func.loadfile("predefined.func"):
            command_list = func.parse()
            run.script_mode = True
            try:
                ipandport = command_list["connect"]
            except KeyError:
                print("Couldnt find any connect info in predefined.func please define it as:\nconnect 192.168.1.1:1221")
                sys.exit()
            ipandport = ipandport.split(":")

            run.ip = ipandport[0]
            run.port = int(ipandport[1])
            try:
                DIR = command_list["dir"]
            except KeyError:
                print("Couldnt find any dir info define it as:\ndir /home/")
                sys.exit()
            try:
                run.connect()
            except socket.error:
                print("\tCan't find server")
                sys.exit()

            s.send(run.tel(json.dumps({"tag":"sync"})))
            t = Thread(target=run.cmd)
            t.start()

            commands = command_list["cmd"]
            command_list_count = 0
            for i in commands:
                command_list_count += 1

            run_count = 0
            for cmd in commands:
                print("AUTO SCRIPT >>"+cmd)
                run.switch_3 = False
                run.switch_4 = False
                run.get_cmd = cmd
                run.switch_4 = True
                while not run.switch_3:
                    pass
            print("predefined script ended with succes")
            os._exit(0)

        else:
            print("\tNo predefined file found.")

if __name__=="__main__":
    main()
