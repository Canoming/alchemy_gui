import sys, os
from pyhtmlgui import PyHtmlGui
from alchemy_gui.src.app import PlayGround
from alchemy_gui.views.appView import AppView

from time import sleep

SCRIPT_DIR = os.path.dirname(os.path.realpath(__file__))

def main(work_dir = None):

    args = sys.argv[1:]

    if len(args) > 0:
        work_dir = os.path.join(args[0],"") if len(args) > 0 else None
        print(f'work_dir: {work_dir}')

    if work_dir is None:
        work_dir = os.path.join(SCRIPT_DIR, "assets/src/")
    app = PlayGround(work_dir = work_dir)
    gui = PyHtmlGui(
        app_instance  = app,
        view_class    = AppView,
        static_dir    = os.path.join(SCRIPT_DIR, "assets"),
        template_dir  = os.path.join(SCRIPT_DIR, "templates"),
        base_template = "base.tmpl",
        on_view_connected    = app.on_view_connected,
        on_view_disconnected = app.on_view_disconnected,
        listen_port    = 8042,
        listen_host    = "127.0.0.1",
        auto_reload    = True,
        single_instance= True,
        # Notice the animation and tab view in sync if you open the view in multiple browser windows
    )
    gui.start(show_frontend=True, block=False)

    while gui._server.is_alive:
        sleep(1)

if __name__ == "__main__":

    work_dir = os.path.join(SCRIPT_DIR, "assets/src/")
    print(f'main.py is running at {work_dir}...')
    main(work_dir)