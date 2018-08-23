#!/usr/bin/env python

import subprocess
import sys
import os
import getpass
from argparse import ArgumentParser

def install(package): #installs packages if they are not installed
    try:
        lib = __import__(package)
    except:
        print package + " is not installed. Installing now..."
        subprocess.call([sys.executable, "-m", "pip", "install", package])
    finally:
        globals()[package] = __import__(package)

def scpTransfer(server, usern, passw, src, dest): #does file transfer
    install('paramiko') # installs package if it doenst exist
    import paramiko
    import os
    import socket
    ssh = paramiko.SSHClient() #creates ssh client
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    try:
        ssh.connect(server, username=usern, 
            password=passw) #connects to server
        sftp = ssh.open_sftp() #opens sftp connection
        sftp.chdir(dest) #sets destination for file transfer
        for file in os.listdir(src): #transfers files 1 by 1 from src
            try:
                print(sftp.stat(dest+file))
                print(file + " exists in " + dest)
            except IOError:
                print("Copying " + file + " to " + dest)
                cwd = os.getcwd() # save current dir 
                os.chdir(src) 
                try:
                    sftp.put(file, dest + file) #copies file 
                except socket.error: # a bug exists with paramiko where you may need to copy file again
                    ssh.connect(server, username=usern, 
                        password=passw)
                    sftp = ssh.open_sftp() 
                    sftp.put(file, dest + file) 
                finally:
                    os.chdir(cwd) 
            finally:
                ssh.close() #closes ssh connection
    except paramiko.SSHException:
        print("Connection Error. Try again.")

def runCmd(cmds, server, usern, passw):
    install('paramiko') 
    import paramiko
    ssh = paramiko.SSHClient() 
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    try:
        ssh.connect(server, username=usern, 
            password=passw) 
        for cmd in cmds: # runs all commands in cmds array
            print(usern + "@" + server + ": " + cmd)
            stdin, stdout, stderr = ssh.exec_command(cmd) # execute cmd
            while not stdout.channel.exit_status_ready(): # waits for commands to complete
                pass
            # if stdout.readlines():
            #     print stdout.readlines()
        ssh.close() 
    except paramiko.SSHException:
        print("Connection Error. Try again.")


parser = ArgumentParser()
parser.add_argument('--force', action='store_true')
args = parser.parse_args() #saves into bool called args.force

username = raw_input("Username: ")
password = getpass.getpass("Password: ") #gets pass securely
cwd = os.getcwd()
path = cwd.replace(os.sep, '/') #replace \ with /
source = path + '/setup_files/'
destination = '/home/' + username + '/'
setupCommands = [
    'chmod +x setup.sh',
    "sed -i -e 's/\\r$//' setup.sh",
]
print("Enter IP of instance " + str(i+1))
instance = raw_input()
instance = instance.replace(' ','') #remove whitespace
scpTransfer(instance, username, 
    password, source, destination) 

runCmd(setupCommands, instance, username, password)

clusterCommands = [
        'docker exec container_3400 bash -c "\
        cd /usr/local/bin; \
        apt-get --assume-yes update; \
        apt-get --assume-yes upgrade;"'
    ]  
runCmd(clusterCommands, server, username, password) 