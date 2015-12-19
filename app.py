#!/usr/bin/python
# -*- coding: utf-8 -*-

import gtk, pango, gobject
from gtk import gdk
import threading
import subprocess
import time
import json
import re


from host import Host
from cpu import CPU
from gpu import GPU
from ssd import SSD
from battery import Battery


INTERVAL = 0.5


class App(gtk.Window):

    def __init__(self):
        gtk.Window.__init__(self)

        self.host = Host()
        self.cpu = CPU()
        self.gpu = GPU()
        self.ssd = SSD()
        self.bat = Battery()

        self.notebook = gtk.Notebook()
        self.add(self.notebook)

        self.page_1 = gtk.VBox()
        self.__fill_page_1()
        self.notebook.append_page(self.page_1, gtk.Label('Hardware Monitor'))


        self.page_2 = gtk.VBox()
        self.__fill_page_2()
        self.notebook.append_page(self.page_2, gtk.Label('Hardware Info'))


        self.page_3 = gtk.VBox()
        self.__fill_page_3()
        self.notebook.append_page(self.page_3, gtk.Label('About'))

        gtk.rc_parse('/home/artluix/.themes/glossy_orange/gtk-2.0/gtkrc')

#---------------------------------------------- PAGE 1 -------------------------------------------------------------

    def __fill_page_1(self):
        self.store_1 = gtk.TreeStore(str, str, str, str)
        treeview = gtk.TreeView(self.store_1)
        treeview.set_enable_tree_lines(True)
        treeview.modify_font(pango.FontDescription('monaco 10'))
        renderer = gtk.CellRendererText()

        scrolled_window = gtk.ScrolledWindow()
        scrolled_window.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
        scrolled_window.add(treeview)
        self.page_1.pack_start(scrolled_window, True, True, 0)

        columns = ('Sensor', 'Value', 'Min', 'Max')
        for i in range(len(columns)):
            column = gtk.TreeViewColumn(columns[i], renderer, text=i)
            treeview.append_column(column)

        self.__add_nodes_to_store_1()
        treeview.expand_all()

        self.__add_threads()
        self.__set_threads_daemons()
        self.__start_threads()


    def __add_nodes_to_store_1(self):
        host_node = self.store_1.append(None, [self.host.get_name()] + [''] * 3 )

        cpu_node = self.store_1.append(host_node, [self.cpu.get_name()] + [''] * 3)

        cpu_temp_node = self.store_1.append(cpu_node, ['Temperature'] + [''] * 3)
        self.cpu_temp_value_nodes = []
        for t_l in self.cpu.get_temp_labels():
            self.cpu_temp_value_nodes.append(self.store_1.append(cpu_temp_node, [t_l] + [''] * 3))

        cpu_freq_node = self.store_1.append(cpu_node, ['Frequency'] + [''] * 3)
        self.cpu_freq_value_nodes = []
        for f_l in self.cpu.get_freq_labels():
            self.cpu_freq_value_nodes.append(self.store_1.append(cpu_freq_node, [f_l] + [''] * 3))

        cpu_usage_node = self.store_1.append(cpu_node, ['Usage'] + [''] * 3)
        self.cpu_usage_value_nodes = []
        for u_l in self.cpu.get_usage_labels():
            self.cpu_usage_value_nodes.append(self.store_1.append(cpu_usage_node, [u_l] + [''] * 3))

        gpu_node = self.store_1.append(host_node, [self.gpu.get_name()] + [''] * 3)

        gpu_freq_node = self.store_1.append(gpu_node, ['Frequency'] + [''] * 3)
        self.gpu_freq_value_node = self.store_1.append(gpu_freq_node, [self.gpu.get_freq_label()] + [''] * 3)

        ssd_node = self.store_1.append(host_node, [self.ssd.get_name()] + [''] * 3)

        ssd_temp_node = self.store_1.append(ssd_node, ['Temperature'] + [''] * 3)
        self.ssd_temp_value_node = self.store_1.append(ssd_temp_node, [self.ssd.get_temp_label()] + [''] * 3)

        bat_node = self.store_1.append(host_node, [self.bat.get_name()] + [''] * 3)

        bat_voltage_node = self.store_1.append(bat_node, ['Voltage'] + [''] * 3)
        self.bat_voltage_value_node = self.store_1.append(bat_voltage_node, [self.bat.get_voltage_label()] + [''] * 3)

        bat_charge_node = self.store_1.append(bat_node, ['Charge'] + [''] * 3)
        self.store_1.append(bat_charge_node, [''] + self.bat.get_charge_header_labels())
        self.bat_charge_value_node = self.store_1.append(bat_charge_node, [self.bat.get_charge_label()] + [''] * 3)


    def __add_threads(self):
        sensors_update_callbacks = [self.__cpu_temp_update_callback, self.__cpu_freq_update_callback,
            self.__cpu_usage_update_callback, self.__gpu_freq_update_callback, self.__ssd_temp_update_callback,
            self.__bat_voltage_update_callback, self.__bat_charge_update_callback]

        self.sensors_threads = []
        for c in sensors_update_callbacks:
            self.sensors_threads.append(threading.Thread(target=self.__thread_callback, args=[c]))

    def __thread_callback(self, update_func):
        while True:
            gobject.idle_add(update_func)
            time.sleep(INTERVAL)

    def __set_threads_daemons(self):
        for t in self.sensors_threads:
            t.daemon = True

    def __start_threads(self):
        for t in self.sensors_threads:
            t.start()



    def __cpu_temp_update_callback(self):
        cpu_temperature = self.cpu.get_temperature()
        for i, cpu_temp_row in enumerate(zip(*cpu_temperature)):
            for j, cpu_temp_v in enumerate(cpu_temp_row):
                self.store_1.set(self.cpu_temp_value_nodes[i], j + 1, str(cpu_temp_v) + ' °C')


    def __cpu_freq_update_callback(self):
        cpu_frequency = self.cpu.get_frequency()
        for i, cpu_freq_row in enumerate(zip(*cpu_frequency)):
            for j, cpu_freq_v in enumerate(cpu_freq_row):
                self.store_1.set(self.cpu_freq_value_nodes[i], j + 1, str(cpu_freq_v) + ' MHz')

    def __cpu_usage_update_callback(self):
        cpu_usage = self.cpu.get_usage()
        for i, cpu_usage_row in enumerate(zip(*cpu_usage)):
            for j, cpu_usage_v in enumerate(cpu_usage_row):
                self.store_1.set(self.cpu_usage_value_nodes[i], j + 1, str(cpu_usage_v) + ' %')


    def __gpu_freq_update_callback(self):
        gpu_freq_row = self.gpu.get_frequency()
        for i, gpu_freq_v in enumerate(gpu_freq_row):
            self.store_1.set(self.gpu_freq_value_node, i + 1, str(gpu_freq_v) + ' MHz')


    def __ssd_temp_update_callback(self):
        ssd_temp_row = self.ssd.get_temperature()
        for i, ssd_temp_v in enumerate(ssd_temp_row):
            self.store_1.set(self.ssd_temp_value_node, i + 1, str(ssd_temp_v) + ' °C')


    def __bat_voltage_update_callback(self):
        bat_voltage_row = self.bat.get_voltage()
        for i, bat_voltage_v in enumerate(bat_voltage_row):
            self.store_1.set(self.bat_voltage_value_node, i + 1, str(bat_voltage_v) + ' V')

    def __bat_charge_update_callback(self):
        bat_charge_row = self.bat.get_charge()
        for i, bat_charge_v in enumerate(bat_charge_row):
            self.store_1.set(self.bat_charge_value_node, i + 1, str(bat_charge_v) + ' mWh')

#---------------------------------------------- PAGE 2 -------------------------------------------------------------

    def __fill_page_2(self):
        self.store_2 = gtk.TreeStore(str)
        treeview = gtk.TreeView(self.store_2)
        treeview.set_enable_tree_lines(True)
        treeview.modify_font(pango.FontDescription('monaco 10'))
        renderer = gtk.CellRendererText()

        scrolled_window = gtk.ScrolledWindow()
        scrolled_window.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
        scrolled_window.add(treeview)
        self.page_2.pack_start(scrolled_window, True, True, 0)

        column = gtk.TreeViewColumn('List Hardware', renderer, text=0)
        treeview.append_column(column)

        self.dimms = self.__read_dimms()

        data = self.__read_lshw()
        self.__parse_json_to_store_2(data)


    def __read_dimms(self):
        subprocess.call(['sudo', 'modprobe', 'eeprom'])
        s = subprocess.check_output('decode-dimms').decode()
        return s.split('\n\n\n')[1:3]


    def __parse_dimm(self, dimm, parent_node, i):
        dimm_blks = dimm.split('\n\n')
        dimm_header = dimm_blks[0].split('\n')
        dimm_header[0], dimm_header[1] = dimm_header[1], dimm_header[0]
        dimm_blks[0] = dimm_header[1]

        dimm_name = dimm_header[0][48:-1] + str(i)
        dimm_from_name = dimm_header[1].split(':')[0]
        dimm_from_path = dimm_header[1].split(':')[1].lstrip(' ')

        name_node = self.store_2.append(parent_node, [dimm_name])
        k_node = self.store_2.append(name_node, [dimm_from_name])
        self.store_2.append(k_node, [dimm_from_path])

        for blk in dimm_blks[1:]:
            blk_l = blk.split('\n')
            blk_name = blk_l[0].split('===')[1][1:-1]
            blk_name_node = self.store_2.append(name_node, [blk_name])
            for s in blk_l[1:]:
                k = s[0:48].rstrip(' ')
                v = s[48:]
                k_node = self.store_2.append(blk_name_node, [k])
                self.store_2.append(k_node, [v])


    def __read_lshw(self):
        data_str = subprocess.check_output(['lshw', '-json']).decode()
        return json.loads(data_str)


    def __parse_json_to_store_2(self, d, parent_node=None):
        if type(d) is dict:
            if 'id' in d:
                if re.match('bank:[0-9]', d['id']):
                    n = int(d['id'][-1])
                    if n in (0, 2):
                        n >>= 1
                        self.__parse_dimm(self.dimms[n], parent_node, n)
                else:
                    parent_node = self.store_2.append(parent_node, [str(d['id'])])
                    del(d['id'])
                    for k in d:
                        if k not in ('capabilities', 'configuration', 'children'):
                            key_node = self.store_2.append(parent_node, [str(k)])
                            if type(d[k]) is not list:
                                value_node = self.store_2.append(key_node, [str(d[k])])
                            else:
                                for v in d[k]:
                                    value_node = self.store_2.append(key_node, [str(v)])
                        elif k == 'configuration':
                            key_node = self.store_2.append(parent_node, [str(k)])
                            value_dict = d[k]
                            for k_dict in value_dict:
                                key_l_node = self.store_2.append(key_node, [str(k_dict)])
                                self.store_2.append(key_l_node, [str(value_dict[k_dict])])
                        elif k == 'capabilities':
                            key_node = self.store_2.append(parent_node, [str(k)])
                            self.store_2.append(key_node, [' '.join(str(x) for x in d[k])])

                if 'children' in d:
                    for list_dict in d['children']:
                        self.__parse_json_to_store_2(list_dict, parent_node)

#---------------------------------------------- PAGE 3 -------------------------------------------------------------

    def __fill_page_3(self):
        textview = gtk.TextView()
        textview.modify_font(pango.FontDescription('Droid Sans 14'))
        textview.set_editable(False)
        textview.set_cursor_visible(False)
        textview.set_justification(gtk.JUSTIFY_CENTER)
        textbuffer = textview.get_buffer()
        s = '\n\n\n\n\n\n\n\n\nThis program is brought to you by\nArtluix - Daineko Stanislau\nSt. of BSUIR of FKSiS\nof chair of Informatics\n\nBig thanks and credits to devs of:\ndecode-dimms\n lshw\n hdparm\n hddterm'
        textbuffer.set_text(s)
        self.page_3.pack_start(textview, True, True, 0)


def main():
    gdk.threads_init()
    app = App()
    app.connect('delete-event', gtk.main_quit)
    app.show_all()
    gtk.main()


if __name__ == '__main__':
    main()
