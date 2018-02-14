#-*-coding:utf8-*-
import socket, os,json,time, sys
from threading import Thread
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

local_dir = os.path.dirname(os.path.realpath(__file__))+"/" #dir of code file 

try:
    with open(local_dir+"servconf.conf", "r") as dosya:
        config = json.load(dosya)
    first_run = False

except IOError:
    first_run = True

class server(object):
    def __init__(self, ip, port):
        self.ip = ip
        self.port = port
        self.clients = []
        self.content_dic = {}
        self.threadpool=[]
        self.ROOT = ""
        self.binder()

    def binder(self):
        s.bind((self.ip, self.port))
        s.listen(4)

    def create_thread(self, count):
        for i in range(count):
            thr = Thread(target=self.accept)
            thr.start()
            self.threadpool.append(thr)

    def sync_contents(self, DIR):
        self.contents = os.listdir(DIR)
        self.content_dic = {}
        for i in self.contents:
            if os.path.isfile(DIR+i):
                size = os.path.getsize(DIR+i)
                tip = "file"
                self.content_dic[i]={"type":tip,
                                     "size":size}
            else:
                tip = "dir"
                self.content_dic[i]={"type":tip,
                                     "size":None}

    def tel(self,value):
        return bytes(value, "UTF-8")

    def sync(self,c, DIR):
        self.sync_contents(DIR)
        c.send(self.tel(json.dumps({"tag":"contents","data":self.content_dic})))

    def accept(self):
        c, addr = s.accept()
        self.clients.append(c)
        print(addr[0],"has just connected")
        DIR = self.ROOT
        directory = ""
        while 1:
            try:
                received = c.recv(1024).decode("utf-8")
                received = json.loads(received)

                if received["tag"] == "push":
                    filename = received["data"]
                    dosya = open(DIR+received["dir"]+filename, "wb")
                    c.send(self.tel(json.dumps({"tag":"info", "data":"ready"})))
                    data = True

                    while data:
                        data = c.recv(1024)
                        dosya.write(data)
                    dosya.close()
                    print("push completed")

                if received["tag"] == "sync":
                    self.sync(c, DIR)

                if received["tag"] == "get_dir":
                    c.send(self.tel(json.dumps({"tag":"dir", "data":directory})))

                if received["tag"] == "cd":
                    directory = received["data"]

                    if not directory == "":
                        if not directory[-1] == "/":
                            directory += "/"

                        if "".join(directory[:2]) == "./":
                            directory = DIR + "".join(directory[2:])

                        try:
                            os.listdir(self.ROOT+directory)
                            DIR = self.ROOT+directory
                            c.send(self.tel(json.dumps({"tag":"dir_info", "data":"succes"})))

                        except OSError:
                            c.send(self.tel(json.dumps({"tag":"dir_info", "data":"fail"})))

                    else:
                        directory = ""
                        DIR = self.ROOT
                        c.send(self.tel(json.dumps({"tag":"dir_info", "data":"succes"})))

                if received["tag"] == "get":
                    try:
                        dosya = open(DIR+received["dir"]+received["data"], "rb")
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

                    except IOError:
                        print("couldnt find file")
                        c.send(self.tel(json.dumps({"tag":"info","data":"fail"})))

            except json.decoder.JSONDecodeError:
                print("user {} has disconnected".format(addr[0]))
                self.create_thread(1)
                break
            except OSError:
                print("user {} has  disconnected".format(addr[0]))
                self.create_thread(1)
                break


def main():
    global serv, config
    if first_run:
        print("\n\tPlease enter server dir\n\texample: /home")

        while 1:
            girdi = input("\t>>")

            if not girdi[-1] == "/":
                girdi += "/"

            try:
                os.listdir(girdi)
                break

            except OSError:
                print("\n\tPlease enter a valid dir")
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

            except IndexError:
                print("\twrong entry")
        print("\n\twould you want to save these datas?\n\t y or n")

        while 1:
            inp = input("\n\t>>")

            if inp in ["y", "n"]:
                break

        if inp == "y":
            config = {"ip":ip,
                      "port":port,
                      "dir":girdi}
            with open(local_dir+"servconf.conf", "w") as dosya:
                json.dump(config, dosya)

    else:
        ip = config["ip"]
        port = config["port"]
        girdi = config["dir"]

    serv = server(ip, port)
    serv.ROOT = girdi
    serv.create_thread(32)
    print("listening for connections")

if __name__ == "__main__":
    main()
