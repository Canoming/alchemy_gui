import os, json
import uuid
import threading, traceback

from markupsafe import Markup
from pyhtmlgui import Observable, ObservableDict

class InfoBox(Observable):
    def __init__(self, scripts_path):
        super().__init__()
        self.target_file = 'None'

        self.scripts_path = scripts_path

        self.set()
    
    def _fetch_scripts(self):
        f = []
        for (dirpath, dirnames, filenames) in os.walk(self.scripts_path):
            f.extend(filenames)
            break
        return list(filter(lambda x: x.endswith('.py'), f))

    def get_str(self):
       return  Markup(self._scripts)

    def set(self, value:str =None):
        self.files = self._fetch_scripts()

        if value is None:
            value = self.files[0]

        self.target_file = value
        print(f'set to {value}')
        self.notify_observers()

        self._scripts = ""
        for file in self.files:
            if file == self.target_file:
                self._scripts += f"""
                <option value="{file}" selected>{file}</option>
                """
            else:
                self._scripts += f"""
                <option value="{file}">{file}</option>
            """
        self.notify_observers()

    def reset(self):
        self.set('empty info')

class HyperPara(Observable):
    def __init__(self, default=None, d_type="int"):
        super().__init__()

        self.d_type = d_type
        if self.d_type not in self.supported_types():
            raise ValueError(f"Type {d_type} not supported")

        self.set_default(default)
        self._set_input_method()

    def set(self, value):
        self.value = self._cast(value)
        self.notify_observers()

    def set_default(self, value):
        self.default = self._cast(value)
        self.reset()

    def reset(self):
        self.set(self.default)

    @staticmethod
    def supported_types():
        return ["int", "float", "string"]

    def _cast(self, value):
        try:
            if self.d_type == "int":
                return int(value)
            elif self.d_type == "float":
                return float(value)
            elif self.d_type == "string":
                return str(value)
        except:
            raise ValueError(f"Could not cast {value} to {self.d_type}")

    def _set_input_method(self):
        if self.d_type == "int":
            self.method = "number"
        elif self.d_type == "float":
            self.method = "number"
        elif self.d_type == "string":
            self.method = "text"

class HyperParaDict(Observable):
    def __init__(self, path : str):
        super().__init__()
        self.HyperParas = ObservableDict()

        self.path = path
        self.file_name = os.path.join(self.path, 'paras.json')

        self.read_paras()

    def remove_hyper_para(self, name : str):
        print(f'remove parameter: {name}...')
        del self.HyperParas[name]

    def add_hyper_para(self, name = None, value = 0, type : str = "int"):
        if name is None or name == "":
            name = ("%s" % uuid.uuid4()).split("-")[0]
        self.HyperParas[name] = HyperPara(value, type)

    def get_paras(self):
        paras = {}

        for para in self.HyperParas:
            paras[para] = self.HyperParas[para].value

        return paras

    def save_paras(self):
        paras = self.get_paras()
        print('save parameters...')

        if not os.path.exists(self.file_name):
            os.mknod(self.file_name)
        with open(self.file_name, 'w') as f:
            json.dump(paras, f)

    def read_paras(self):
        if not os.path.exists(self.file_name):
            return

        with open(self.file_name, 'r') as f:
            paras = json.load(f)

        for para in paras:
            self.add_hyper_para(para, paras[para], self._type_of(paras[para]))
        self.notify_observers()

    @staticmethod
    def _type_of(value):
        if type(value) == int:
            return 'int'
        elif type(value) == float:
            return 'float'
        elif type(value) == str:
            return 'string'
        else:
            return 'unsupported'

class Logs(Observable):
    def __init__(self):
        super().__init__()

        self.log = "Not running."
        self.err = ""

    def read_log(self, ps, q_out, q_err, status):

        self.ps = ps
        self.stdout = q_out
        self.stderr = q_err
        self.status = status
        self._t_log = threading.Thread(name="logging", target=self._loop_log)
        self._t_err = threading.Thread(name="err", target=self._loop_err)
        self._t_log.start()
        self._t_err.start()

    def stop_log(self):
        self._t_log.join()

    def _loop_log(self):
        self.log = ""
        self.notify_observers()
        print('collecting stdout...')

        while True:
            try:
                output = self.stdout.get(timeout=1)
            except:
                output = None
            if output:
                self.log += output
                self.notify_observers()
            if self.stdout.qsize() == 0 and self.stderr.qsize() == 0 and self.status.is_set():
                self.ps.terminate()
                self.ps.join()
                self.log += "\n" + f"{'script terminated':-^50}"
                print(f"Process finished")
                self.notify_observers()
                break

        return self.ps.is_alive()

    def _loop_err(self):
        self.err = ""
        self.notify_observers()

        while True:
            try:
                output : str = self.stderr.get(timeout=1)
            except:
                output = None
            if output:
                print(output)
                self.err += output
                self.notify_observers()
            if not self.ps.is_alive():
                break