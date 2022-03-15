import subprocess
import os.path
import sys
import time



pythonInterpreter = sys.executable
folder = os.path.dirname(__file__)


def python(prog,*args):
    cmd = []
    
    if sys.platform == "win32":
        #https://stackoverflow.com/questions/19308415/execute-terminal-command-from-python-in-new-terminal-window
        cmd += ["start"]
    elif sys.platform == "linux":
        cmd += ["xterm","-e"]
        #cmd=[]
    else:
        print("Get a real computer, please")
        sys.exit(1)

    cmd += [pythonInterpreter,prog]
    cmd += args
    
    print(" ".join(cmd))
    S = subprocess.Popen( cmd )
    return S
    
    
#start the server
S = python("slobberserver.py")

#wait for server to come up
time.sleep(1)

#start the clients
#three AI plus a human

A1 = python("slobberclient.py", "ai", "Alice", "ws://localhost:2022")
A2 = python("slobberclient.py", "ai", "Bob", "ws://localhost:2022")
A3 = python("slobberclient.py", "ai", "Carol", "ws://localhost:2022")
A4 = python("slobberclient.py", "human", "Hugh", "ws://localhost:2022")

S.wait()
A1.wait()
A2.wait()
A3.wait()
A4.wait()
