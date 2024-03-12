import os, sys
import multiprocessing
import traceback

import importlib.util as imputil
from types import SimpleNamespace

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
        self.ps = multiprocessing.Process(target=self.wrap_code, args=(self.stdout, self.stderr))

        self.ps.start()
        self.log.read_log(self.ps, self.stdout, self.stderr, self.script_status)
        print(f"Process '{self.infoBox.target_file}' started...")

    def stop_code(self):
        print("stop_code signaled")
        if self.ps is not None:
            self.script_status.set()
            self.stderr.put(("ValueError: Script terminated by user"))
            self.ps.terminate()

    def wrap_code(self, q_out, q_err):
        path = self.infoBox.scripts_path+self.infoBox.target_file
        paras = self.para_dict.get_paras()

        os.chdir(self.infoBox.scripts_path)
        loggging_q = _QueueWriter(q_out)
        sys.stdout = loggging_q

        try:
            spec = imputil.spec_from_file_location(
                'user_script',
                path
            )
            script = imputil.module_from_spec(spec)

            script.hyper_paras = SimpleNamespace(**paras)
            spec.loader.exec_module(script)
        except Exception as e:
            print("An error occurs, see the error log")
            err_str = "\n".join(traceback.format_exception_only(e))
            err_str += f"{'':-^50}\n"
            err_str += "Traceback:\n"
            err_str += "\n".join(traceback.format_tb(e.__traceback__)[3:])
            q_err.put(err_str)

        self.script_status.set()

    def on_view_connected(self, nr_of_instances, nr_of_connections):
        print("View connected:", nr_of_instances, nr_of_connections)

    def on_view_disconnected(self, nr_of_instances, nr_of_connections):
        print("View disconnected:", nr_of_instances, nr_of_connections)
        if nr_of_instances == 0:
            print("No more frontends connected, exit now")
            sys.exit(0)
