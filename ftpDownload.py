 
from ftplib import FTP
import os,sys,string,datetime,time
import traceback
import socket
 
class MYFTP:
    def __init__(self,localdir, hostaddr, username, password, remotedir, port=21):
        self.hostaddr = hostaddr
        self.username = username
        self.password = password
        self.remotedir  = remotedir
        self.port     = port
        self.ftp      = FTP()
        self.file_list = []
 
        self.localdir = localdir
        self.local_files = []
        self.remote_files = []
        self.update_files = []
        self.appendFiles = []
        # self.ftp.set_debuglevel(2)
    def __del__(self):
        self.ftp.close()
        # self.ftp.set_debuglevel(0)
    def login(self):
        ftp = self.ftp
        try: 
            timeout = 300
            socket.setdefaulttimeout(timeout)
            ftp.set_pasv(True)
            ftp.connect(self.hostaddr, self.port)
            ftp.login(self.username, self.password)
            ftp.voidcmd('TYPE I')
        except Exception:
            print traceback.format_exc()
            print "error"
        try:
            ftp.cwd(self.remotedir)
        except(Exception):
            print traceback.format_exc()
            print "error"
    def logout(self):
        self.ftp.close()
    def getFile(self, dir):
        filelist = []
        if not os.path.isdir(dir):
            filelist.append(dir)
            return filelist

        list = os.listdir(dir)
        if len(list) == 0:
            filelist.append(dir)
            return filelist
        
        for line in list:
            tmpdir = os.path.join(dir, line)
            if os.path.isdir(tmpdir):
                tmpfiles = self.getFile(tmpdir)
                filelist.extend(tmpfiles)
            else:
                filelist.append(tmpdir)
        return filelist
    
    def get_localFileList(self):
        try:
            filelist = []
            list = os.listdir(self.localdir)
            for line in list:
                dir = os.path.join(self.localdir, line)
                files = self.getFile(dir)
                filelist.extend(files)
        except Exception,e:
            print e
 
    def getRemoteFile(self, dir):
        filelist = []
        try:
            self.ftp.cwd(dir)
        except:
            filelist.append(dir)
            return filelist

        # list = self.ftp.nlst()
		tmp = []
		self.ftp.dir(tmp.append)
		list = [f.split()[-1] for f in tmp]
        if len(list) == 2:	# with '.' & '..'
            #filelist.append(dir)
            return filelist

        for line in list:
			if line == '.' or line == '..':
				continue
            tmpdir = os.path.join(dir, line)
            files = self.getRemoteFile(tmpdir)
            filelist.extend(files)
        return filelist
    
    def get_remoteFileList(self):
        try:
			self.remote_files = self.getRemoteFile(self.remotedir)
        except:
            print traceback.format_exc()

    def get_updateFile(self):
        try:
            for file in self.remote_files:
                dir = os.path.join(self.localdir, file)
                # dir = self.localdir + file
                flag = os.path.exists(dir)
                if not flag:
                    self.update_files.append(file)
        except:
            print traceback.format_exc()

    def update_file(self):
        try:
            for remotefile in self.update_files:
                #file = self.localdir + remotefile
                file = os.path.join(self.localdir, remotefile)
                #if not os.path.isfile(file):
                #    try:
                #        print 'make dir: ', file
                #        os.makedirs(file)
                #    except:
                #        print traceback.format_exc()
                #else:
                if True:
                    pos = file.rfind("\\")
                    dir = file[:pos]
                    try:
                        print 'down file: ', file
                        if not os.path.exists(dir):
                            os.makedirs(dir)
                        self.download_file(file, remotefile)
                    except:
                        print traceback.format_exc()
        except:
            print traceback.format_exc()
    
    def download_file(self, localfile, remotefile):
        file_handler = open(localfile, 'wb')
        self.ftp.retrbinary('RETR '+remotefile, file_handler.write)
        file_handler.close()
    
    def clean_file(self):
        self.remote_files = []
        self.update_files = []
        
if __name__ == '__main__':
    try:
        host = "127.0.0.1"
        port = 21
        username = ""
        password = ""
        server_dir = "/home/down/snmpd/bignat_ipvs"
        local_dir = "/test"
        while True:
            f = MYFTP(local_dir ,host, username, password, server_dir, port)
            f.login()
            f.get_remoteFileList()
            f.get_updateFile()
            f.update_file()
            f.clean_file()
            f.logout()
            time.sleep(10)
    except:
        print traceback.format_exc()
