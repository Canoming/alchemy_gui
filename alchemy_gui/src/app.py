import os
import sys
import multiprocessing

from pyhtmlgui import Observable
from .components import InfoBox, HyperParaDict, Logs

class _QueueWriter:
    def __init__(self,queue):
        self.q = queue

    def write(self,msg):
        self.q.put(msg)

    def flush(self):
        sys.__stdout__.flush()

class PlayGround(Observable):
    def __init__(self, work_dir):
        super().__init__()
        self.infoBox = InfoBox(work_dir)
        self.para_dict = HyperParaDict(work_dir)
        self.log = Logs()

        self.ps = None
        self.stdout = None

    def run_code(self):

        if self.ps is not None:
            if self.ps.is_alive():
                print("There is a script still running")
                return
            else:
                self.ps = None
                self.log.ps = None
                self.log.status.clear()

        self.script_status = multiprocessing.Event()
        self.stdout = multiprocessing.Queue()
        self.stderr = multiprocessing.Queue()
        self.ps = multiprocessing.Process(target=self.code_wrapper, args=(self.stdout, self.stderr))

        self.ps.start()

        self.log.read_log(self.ps, self.stdout, self.stderr, self.script_status)

    def stop_code(self):
        print("stop_code signaled")
        if self.ps is not None:
            self.script_status.set()
            self.stderr.put(ValueError("Script terminated by user"))
            self.ps.terminate()

    def code_wrapper(self, q_out, q_err):
        print(f"Process '{self.infoBox.target_file}' started...")
        path = self.infoBox.scripts_path+self.infoBox.target_file
        paras = self.para_dict.get_paras()

        code = ""
        with open(path, 'r') as f:
            code += f.read()

        os.chdir(self.infoBox.scripts_path)
        loggging_q = _QueueWriter(q_out)
        sys.stdout = loggging_q

        try:
            exec(code,paras)
        except Exception as e:
            print("An error occurs, see the error log")
            q_err.put(e)
        self.script_status.set()


    def on_view_connected(self, nr_of_instances, nr_of_connections):
        print("View connected:", nr_of_instances, nr_of_connections)

    def on_view_disconnected(self, nr_of_instances, nr_of_connections):
        print("View disconnected:", nr_of_instances, nr_of_connections)
        if nr_of_instances == 0:
            print("No more frontends connected, exit now")
            sys.exit(0)
