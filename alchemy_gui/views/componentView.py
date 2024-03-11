from pyhtmlgui import PyHtmlView, ObservableDictView
from keyword import iskeyword

def _is_valide_variable_name(name):
    return name.isidentifier() and not iskeyword(name)

class HyperParaDictView(PyHtmlView):
    TEMPLATE_FILE = "HyperParaView.tmpl"

    def __init__(self, subject, parent, **kwargs):
        super().__init__(subject, parent, **kwargs)
        self.dictView = ObservableDictView(subject.HyperParas, self, HyperItemView, dom_element="tbody")

    def add_hyper_para(self):
        js = f'return [document.getElementById("hyper_para").value,' + f'document.getElementById("hyper_para_type").value];'

        def get_result(res):
            first_instance = res[0]["value"]
            print(f'add para {first_instance[0]}')

            name = first_instance[0]
            d_type = first_instance[1]

            if not _is_valide_variable_name(name):
                self.call_javascript('alert', args=[f"Name {name} is not a valid variable name"])
                return

            if d_type == "int":
                value = 0
            elif d_type == "float":
                value = 0.0
            elif d_type == "string":
                value = ""
            else:
                self.call_javascript('alert', args=["Type {d_type} not supported"])
                return

            try:
                self.subject.add_hyper_para(name, value, d_type)
                self.subject.notify_observers()
            except Exception as e:
                self.call_javascript('alert', args=[f"Error: {e}"])

        result = self.eval_javascript(js)
        result._callback = get_result
    
    def remove_hyper_para(self, key):
        print(f'para {key} is removed')
        self.subject.remove_hyper_para(key)

    def save_paras(self):
        self.subject.save_paras()
        self.call_javascript('alert', args=["Paras saved"])

class HyperItemView(PyHtmlView):
    DOM_ELEMENT = "tr"
    TEMPLATE_STR = '''
    <td>{{pyview.element_key()}}</td>
    <td>{{pyview.subject.d_type}}</td>
    <td>{{pyview.subject.value}}</td>
    <td><input type="{{pyview.subject.method}}" id={{pyview.element_key()}}_input></td>
    <td>
        <button onclick='pyview.set_value();'>Set</button> 
        <button onclick='pyview.subject.reset();'>Reset</button> 
        <button onclick='pyview.parent.parent.remove_hyper_para("{{pyview.element_key()}}");'>Remove</button> 
    </td>
    '''

    def set_value(self):
        js = f'return document.getElementById("{self.element_key()}_input").value;'

        def get_result(res):
            try:
                self.subject.set(res[0]['value'])
            except Exception as e:
                self.call_javascript('alert', args=[f"Error: {e}"])

        result = self.eval_javascript(js)
        result._callback = get_result

class InfoView(PyHtmlView):
    TEMPLATE_FILE = "infoView.tmpl"

    def retrieve_info(self, id:str):
        js = f'return document.getElementById("{id}").value;'

        def get_result(res):
            self.subject.set(res[0]['value'])

        result = self.eval_javascript(js)
        result._callback = get_result

    def run(self, id:str):
        js = f'return document.getElementById("{id}").value;'

        def get_result(res):
            self.subject.set(res[0]['value'])

        result = self.eval_javascript(js)
        result._callback = get_result

    def terminate(self, id:str):
        js = f'return document.getElementById("{id}").value;'

class LogView(PyHtmlView):
    TEMPLATE_FILE = "logView.tmpl"

    def read_log(self):
        if self.parent.subject.ps is None:
            self.eval_javascript('alert', args=["No script is running!"])
        else:
            self.subject.read_log(self.parent.subject.ps)