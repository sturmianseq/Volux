from volux import (
    VoluxModule,
    VoluxConnection,
    RequestAddConnection,
    RequestRemoveConnection,
    RequestGetConnections,
    RequestStartSync,
    RequestSyncState,
    RequestStopSync,
    RequestGetModules,
)
import tkinter as tk
from tkinter import ttk
import colorama

colorama.init()
import logging

log = logging.getLogger("voluxgui module")
log.setLevel(logging.DEBUG)
# create console handler with a higher log level
ch = logging.StreamHandler()
ch.setLevel(logging.INFO)
# create formatter and add it to the handlers
formatter = logging.Formatter(
    "%(asctime)s - %(name)s - %(levelname)s - %(message)s - %(lineno)d"
)
ch.setFormatter(formatter)
# add the handlers to the logger
log.addHandler(ch)


class VoluxGui(VoluxModule):
    def __init__(self, shared_modules=[], pollrate=None, *args, **kwargs):
        super().__init__(
            module_name="Volux GUI",
            module_attr="gui",
            module_get=self.get,
            get_type=None,
            get_min=None,
            get_max=None,
            module_set=self.set,
            set_type=None,
            set_min=None,
            set_max=None,
            shared_modules=shared_modules,
            pollrate=pollrate,
            *args,
            **kwargs
        )

        self._shared_modules.append(self)

        self.root = tk.Tk()
        self.mainApp = MainApplication(self.root, self, style="mainApp.TFrame")
        self.example_val = 0

    def get(self):

        return self.example_val

    def set(self, new_val):

        container_width = (
            self.mainApp.value_bar.winfo_width()
        )  # note: wasteful, find alternative or remove in future

        self.mainApp.value_bar_fill.config(width=container_width * (new_val / 100))

    def init_window(self):

        self.gui_style = ttk.Style()
        self.gui_style.configure("mainApp.TFrame", background="#19191B")
        self.gui_style.configure("value_bar.TFrame", background="BLACK")
        self.gui_style.configure("value_bar_fill.TFrame", background="RED")

        self.mainApp.pack(side="top", fill=tk.BOTH, expand=True)
        self.root.title("Volux")
        screen_size = (self.root.winfo_screenwidth(), self.root.winfo_screenheight())
        self.root.geometry(
            "{}x{}+{}+{}".format(800, 500, 1920 - 800, 1080 - 500)
        )  # define the size of the window
        self.mainApp._update_loop()
        self.root.mainloop()


class MainApplication(ttk.Frame):
    def __init__(self, parent, module_root, *args, **kwargs):
        ttk.Frame.__init__(self, parent, *args, **kwargs)
        self.parent = parent
        self.module_root = module_root
        self.ext_modules = self.module_root._shared_modules
        self.vis_on = tk.BooleanVar()
        self.sync_running = tk.BooleanVar()

        log.debug("shared modules: {}".format(self.ext_modules))

        self.wip_notice = ttk.Label(
            self, text="NOTE: GUI IS A WORK-IN-PROGRESS", anchor=tk.CENTER
        )
        self.wip_notice.pack(side="top", fill=tk.X)

        self.input_frame = ttk.Frame(self)
        self.input_frame.pack(side="left", fill=tk.Y, padx="14px", pady="14px")

        self.input_label = ttk.Label(self.input_frame, text="INPUTS")
        self.input_label.pack(side="top", fill=tk.BOTH)

        self.input_listbox = tk.Listbox(
            self.input_frame, selectmode=tk.SINGLE, exportselection=False
        )
        self.input_listbox.pack()

        self.input_testget = ttk.Button(
            self.input_frame, text="Get Test", command=self._get_test
        )
        self.input_testget.pack()

        self.output_frame = ttk.Frame(self)
        self.output_frame.pack(side="left", fill=tk.Y, padx="14px", pady="14px")

        self.output_label = ttk.Label(self.output_frame, text="OUTPUTS")
        self.output_label.pack(side="top", fill=tk.BOTH)

        self.output_listbox = tk.Listbox(
            self.output_frame, selectmode=tk.SINGLE, exportselection=False
        )
        self.output_listbox.pack()

        self.output_testset = ttk.Button(
            self.output_frame, text="Set Test", command=self._set_test
        )
        self.output_testset.pack()

        self.output_testset_data = ttk.Entry(self.output_frame)
        self.output_testset_data.pack()

        self.connections_frame = ttk.Frame(self)
        self.connections_frame.pack(side="left", fill=tk.Y, padx="14px", pady="14px")

        self.connections_label = ttk.Label(self.connections_frame, text="CONNECTIONS")
        self.connections_label.pack(side="top", fill=tk.BOTH)

        self.connections_listbox = tk.Listbox(
            self.connections_frame, selectmode=tk.EXTENDED, exportselection=True
        )
        self.connections_listbox.pack()

        self.connections_controls = ttk.Frame(self.connections_frame)
        self.connections_controls.pack()

        self.connections_checkbutton = ttk.Checkbutton(
            self.connections_controls,
            text="Enable Sync",
            variable=self.sync_running,
            command=self._sync_toggled,
        )
        self.connections_checkbutton.grid(row=0, columnspan=2)

        self.connections_add_button = ttk.Button(
            self.connections_controls, text="ADD", command=self._add_connection
        )
        self.connections_add_button.grid(row=1, column=0)

        self.connections_remove_button = ttk.Button(
            self.connections_controls, text="REMOVE", command=self._remove_connection
        )
        self.connections_remove_button.grid(row=1, column=1)

        self.connections_hzbox_label = ttk.Label(
            self.connections_controls, text="Pollrate (Hz)"
        )
        self.connections_hzbox_label.grid(row=2, column=0)

        self.connections_hzbox = ttk.Entry(self.connections_controls, width="5")
        self.connections_hzbox.grid(row=2, column=1)

        self.connections_refresh = ttk.Button(
            self.connections_controls,
            text="REFRESH CONNECTIONS",
            command=self._refresh_connections,
        )
        self.connections_refresh.grid(row=3, columnspan=2)

        self.demo_slider = ttk.Scale(self.output_frame, from_=0, to=100)
        self.demo_slider.pack()

        for smodule in self.ext_modules:
            if hasattr(smodule, "tk_frame"):
                setattr(self, smodule.frame_attr, smodule.tk_frame(self))
                this_frame = getattr(self, smodule.frame_attr)
                smodule._set_gui_instance(self.module_root)
                this_frame.pack(side="left", fill=tk.Y, padx="14px", pady="14px")

        self.value_bar = ttk.Frame(self.parent, height=14, width=100, pad="1px")
        self.value_bar.pack(side="bottom", fill=tk.X)

        self.value_bar_fill = ttk.Frame(
            self.value_bar, height=14, width=0, style="value_bar_fill.TFrame"
        )
        self.value_bar_fill.pack(fill=tk.Y)

        # if hasattr(self.module_root,'broker'):
        self._update_input_output_listboxes()

    def _update_loop(self):

        self.after(1000, self._update_loop)

    def _sync_toggled(self):

        sync_enabled_in_gui = self.sync_running.get()

        if sync_enabled_in_gui == True:

            self._start_connection_sync()

        elif sync_enabled_in_gui == False:

            self._stop_connection_sync()

    def _get_test(self):

        input_module = self._get_selected_input_module()
        get_result = input_module.get()
        log.info("get method response: {}".format(get_result))

    def _set_test(self):

        sel = self.output_listbox.curselection()
        if len(sel) > 0:
            i = self.output_listbox.curselection()[0]
            set_response = self.ext_modules[i].set(int(self.output_testset_data.get()))
            log.info("set method response: {}".format(set_response))
        else:
            raise ValueError("no output selected!")

    def _get_selected_input_module(self):

        sel = self.input_listbox.curselection()
        if len(sel) > 0:
            i = sel[0]
        return self.ext_modules[i]

    def _get_selected_output_module(self):

        sel = self.output_listbox.curselection()
        if len(sel) > 0:
            i = sel[0]
        return self.ext_modules[i]

    def _get_sync_hz(self):

        hzbox_val = self.connections_hzbox.get()

        if hzbox_val == "":

            raise ValueError("error: please enter sync hz!")

        else:

            return int(hzbox_val)

    def _update_input_output_listboxes(self):

        # request = RequestGetModules(self.module_root)
        # modules = self.module_root.broker.process_request(request)

        modules = self.ext_modules

        self.input_listbox.delete(0, tk.END)  # clear input listbox
        self.output_listbox.delete(0, tk.END)  # clear output listbox

        for i in range(len(modules)):

            module = modules[i]

            if hasattr(module, "get"):

                self.input_listbox.insert(tk.END, module._module_name)

            if hasattr(module, "set"):

                self.output_listbox.insert(tk.END, module._module_name)

    def _update_output_listbox(self):

        request = RequestGetModules(self.module_root)
        modules = self.broker.process_request(request)

        for i in range(len(modules)):

            module = self.ext_modules[i]

            if hasattr(module, "set"):

                self.output_listbox.insert(tk.END, module._module_name)

    def _get_selected_mdevices(self):
        devices_to_return = [
            self.parent.mlifx.managed_devices[device_i] for device_i in device_indexes
        ]
        return devices_to_return  # return a tuple of indexes for selected items

    def _add_connection(self):

        connection = VoluxConnection(
            self._get_selected_input_module(),
            self._get_selected_output_module(),
            self._get_sync_hz(),
        )
        request = RequestAddConnection(self.module_root, connection=connection)
        self.module_root.broker.process_request(request)
        self._refresh_connections()

    def _remove_connection(self):

        connection = self._get_selected_connection()
        request = RequestRemoveConnection(self.module_root, connection=connection)
        self.module_root.broker.process_request(request)
        self._refresh_connections()

    def _get_connections(self):

        request = RequestGetConnections(self.module_root)
        return self.module_root.broker.process_request(request)

    def _get_selected_connection(self):

        connections = self._get_connections()
        connection_index = self.connections_listbox.curselection()[0]
        i = 0
        for connection_UUID in connections:
            if i == connection_index:
                return connections[connection_UUID]
            i += 1

    def _refresh_connections(self):

        connections = self._get_connections()
        self.connections_listbox.delete(0, tk.END)

        for cUUID in connections:

            self.connections_listbox.insert(tk.END, connections[cUUID].nickname)

    def _start_connection_sync(self):

        request = RequestStartSync(self.module_root)

        self.module_root.broker.process_request(request)

    def _stop_connection_sync(self):

        request = RequestStopSync(self.module_root)

        self.module_root.broker.process_request(request)

    def _get_sync_state(self):

        request = RequestSyncState(self.module_root)

        return self.module_root.broker.process_request(request, verbose=False)
