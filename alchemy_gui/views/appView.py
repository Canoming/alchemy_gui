from pyhtmlgui import PyHtmlView

from .componentView import InfoView, HyperParaDictView, LogView

class AppView(PyHtmlView):
    TEMPLATE_FILE = "appView.tmpl"

    def __init__(self, subject, parent, **kwargs):
        super().__init__(subject, parent, **kwargs)
        self.infoView = InfoView(subject=subject.infoBox, parent=self)
        self.hyperParaView = HyperParaDictView(subject=subject.para_dict, parent=self)
        self.logView = LogView(subject=subject.log, parent=self)

    # these functions are automatically called by pyHtmlGui if they exist in the main View class
    def on_frontend_ready(self, nr_of_connections):
        print("on_frontend_ready" , nr_of_connections)

    def on_frontend_disconnected(self, nr_of_connections):
        print("on_frontend_disconnected", nr_of_connections)

    def save_value(self):
        try:
            self.subject.save_paras()
        except Exception as e:
            self.call_javascript('alert', args=[f"Error: {e}"])
