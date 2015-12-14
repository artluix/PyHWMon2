from gi import require_version
require_version('Gtk', '3.0')

from gi.repository import Gtk, GObject
import threading
import subprocess
import time
import glob


INTERVAL = 0.5

def min_row(list_1, list_2):
    return [min(a, b) for a, b in zip(list_1, list_2)]

def max_row(list_1, list_2):
    return [max(a, b) for a, b in zip(list_1, list_2)]



class Host:
    def __init__(self):
        self.name = self.__name()


    def get_name(self):
        return self.name


    def __name(self):
        path = '/etc/hostname'
        name_str = ''
        with open(path, 'r') as f:
            name_str = f.readline()
        return name_str.rstrip('\n')



class Cpu:

    def __init__(self):
        self.name = self.__name()
        self.temp_table = []
        self.temp_labels = self.__temp_labels()

        self.freq_table = []
        self.freq_labels = self.__freq_labels()

        self.usage_table = []
        self.usage_labels = self.__usage_labels()


    def get_name(self):
        return self.name


    def get_temperature(self):
        return self.temp_table

    def get_temp_labels(self):
        return self.temp_labels


    def get_frequency(self):
        return self.freq_table

    def get_freq_labels(self):
        return self.freq_labels


    def get_usage(self):
        return self.usage_table

    def get_usage_labels(self):
        return self.usage_labels


    def __name(self):
        name_str = subprocess.check_output('lscpu | grep \'Model name\'', shell = True).decode()
        return name_str.split(':')[1].lstrip(' ').rstrip('\n')


    def __temp_labels(self):
        path = '/sys/class/hwmon/hwmon0/temp[0-9]_label'
        temp_labels = []
        for filename in sorted(glob.glob(path)):
            with open(filename, 'r') as f:
                temp_labels.append(f.readline().rstrip('\n'))
        return temp_labels

    def __temperature(self):
        path = '/sys/class/hwmon/hwmon0/temp[0-9]_input'
        temp_row = []
        for filename in sorted(glob.glob(path)):
            with open(filename, 'r') as f:
                temp_row.append(int(int(f.readline()) / 1000))
        
        if not cpu_temp_table:
            self.temp_table = [temp_row] * 3
        else:
            self.temp_table[0] = temp_row
            self.temp_table[1] = min_row(temp_row, self.temp_table[1])
            self.temp_table[2] = max_row(temp_row, self.temp_table[2])


    def __freq_row(self):
        path = '/sys/devices/system/cpu/cpu[0-9]/cpufreq/cpuinfo_cur_freq'
        freq_row = []
        for filename in sorted(glob.glob(path)):
            with open(filename, 'r') as f:
                freq_row.append(int(int(f.readline()) / 1000))
        return freq_row

    def __freq_labels(self):
        freq_row = self.__freq_row()
        self.freq_table = [freq_row] * 3
        return ['Core ' + str(i) for i in range(len(freq_row))]

    def __frequency(self):
        freq_row = self.__freq_row()
        self.freq_table[0] = freq_row
        self.freq_table[1] = min_row(freq_row, self.freq_table[1])
        self.freq_table[2] = max_row(freq_row, self.freq_table[2])


    def __usage_row(self):
        def get_times():
            path = '/proc/stat'
            times = []
            with open(path, 'r') as f:
                times = [s.replace('  ', ' ').split(' ')[1:] \
                    for s in f.readlines() if 'cpu' in s]
            return [(int(y) for y in x) for x in times]

        def delta_times():
            times_1 = get_times()
            time.sleep(INTERVAL)
            times_2 = get_times()
            return [[(t2 - t1) for t1, t2 in zip(t1_row, t2_row)] for t1_row, t2_row in zip(times_1, times_2)]

        def get_load():
            dt = delta_times()
            idle_time = [float(x[3]) for x in dt]
            total_time = [sum(x) for x in dt]
            load = [int((1 - (x / y)) * 100) for x, y in zip(idle_time, total_time)]
            return load

        return get_load()

    def __usage_labels(self):
        usage_row = self.__usage_row()
        self.usage_table = [usage_row] * 3
        return ['UC'] + ['Core ' + str(x) for x in range(len(usage_row) - 1)]

    def __usage(self):
        usage_row = self.__usage_row()
        self.usage_table[0] = usage_row
        self.usage_table[1] = min_row(usage_row, self.usage_table[1])
        self.usage_table[2] = max_row(usage_row, self.usage_table[2])



class Gpu:
    def __init__(self):
        self.name = self.__name()
        self.freq_label = 'Gpu'
        self.freq_row = []


    def get_name(self):
        return self.name


    def get_freq_label(self):
        return self.freq_label

    def get_frequency(self):
        return self.freq_row


    def __name(self):
        gpu_name_str = subprocess.check_output('lspci | grep \'VGA\'', shell = True).decode()
        return gpu_name_str.split('VGA')[1].split(':')[1].lstrip(' ').rstrip('\n')


    def __frequency(self):
        path = '/sys/class/drm/card0/gt_cur_freq_mhz'
        freq_cur = 0
        with open(path, 'r') as f:
            freq_cur = int(f.readline())

        if not self.freq_row:
            self.freq_row = [freq_cur] * 3
        else:
            self.freq_row[0] = freq_cur
            self.freq_row[1] = min(freq_cur, self.freq_row[1])
            self.freq_row[2] = max(freq_cur, self.freq_row[2])



class Hdd:
    def __init__(self):
        self.name = self.__name()
        self.temp_label = 'Hdd'
        self.temp_row = []


    def get_name(self):
        return self.name


    def get_temp_label(self):
        return self.temp_label

    def get_temperature(self):
        return self.temp_row


    def __name(self):
        hdd_name_str = subprocess.check_output('hdparm -I /dev/sda | grep \'Model Number\'', shell=True).decode()
        return hdd_name_str.split(':')[1].lstrip(' ').rstrip('\n')


    def __temperature(self):
        temp_cur = int(subprocess.check_output(['hddtemp', '/dev/sda', '-n']))
        if not self.temp_row:
            self.temp_row = [temp_cur] * 3
        else:
            self.temp_row[0] = temp_cur
            self.temp_row[1] = min(temp_cur, self.temp_row[1])
            self.temp_row[2] = max(temp_cur, self.temp_row[2])



class Battery:
    def __init__(self):
        self.name = self.__name()
        self.voltage_label = 'Voltage'
        self.voltage_row = []

        self.charge_header_labels = ['Now', 'Full', 'Full Design']
        self.charge_label = 'Charge'
        self.charge_row = []

    def get_name(self):
        return self.name 


    def get_voltage_label(self):
        return self.voltage_label

    def get_voltage(self):
        return self.voltage_row


    def get_charge_header_labels(self):
        return self.charge_header_labels

    def get_charge_label(self):
        return self.charge_label

    def get_charge(self):
        return self.charge_row


    def __name(self):
        path_manufacturer = '/sys/class/power_supply/BAT1/manufacturer'
        path_model_name = '/sys/class/power_supply/BAT1/model_name'
        bat_name_str = ''
        with open(path_manufacturer, 'r') as f:
            bat_name_str = f.readline().replace('\n', ' ')
        with open(path_model_name, 'r') as f:
            bat_name_str += f.readline().rstrip('\n')
        return bat_name_str


    def __voltage(self):
        path = '/sys/class/power_supply/BAT1/voltage_now'
        voltage_cur = 0
        with open(path, 'r') as f:
            voltage_cur = int(f.readline()) / 1000000

        if not self.voltage_row:
            self.voltage_row = [voltage_cur] * 3
        else:
            self.voltage_row[0] = voltage_cur
            self.voltage_row[1] = min(voltage_cur, self.voltage_row[1])
            self.voltage_row[2] = max(voltage_cur, self.voltage_row[2])


    def __charge(self):
        charge_filenames = ('now', 'full', 'full_design')
        path = '/sys/class/power_supply/BAT1/charge_'  
        if not self.charge_row:
            for filename in charge_filenames:
                with open(path + filename) as f:
                    self.charge_row.append(int(int(f.readline()) / 1000))
        else:
            for i, filename in enumerate(charge_filenames[0:1]):
                with open(path + filename) as f:
                    self.charge_row[i] = int(int(f.readline()) / 1000)



class MyWindow(Gtk.Window):

    def __init__(self):
        Gtk.Window.__init__(self)
        self.store = Gtk.TreeStore(str, str, str, str)
        self.treeview = Gtk.TreeView(self.store)
        renderer = Gtk.CellRendererText()

        self.host = Host()
        self.cpu = Cpu()
        self.gpu = Gpu()
        self.hdd = Hdd()
        self.bat = Battery()

        columns = ('Sensor', 'Value', 'Min', 'Max')

        for i in range(len(columns)):
            column = Gtk.TreeViewColumn(columns[i], renderer, text=i)
            self.treeview.append_column(column)

        self.host_node = self.store.append(None, [self.host.get_name()] + [''] * 3 )

        self.cpu_node = self.store.append(self.host_node, [self.cpu.get_name()] + [''] * 3)

        self.cpu_temp_node = self.store.append(self.cpu_node, ['Temperature']  + [''] * 3)   
        self.cpu_temp_value_nodes = []     
        for t_l in self.cpu.get_temp_labels():
            self.cpu_temp_value_nodes.append(self.store.append(self.cpu_temp_node, [t_l] + [''] * 3))

        self.cpu_freq_node = self.store.append(self.cpu_node, ['Frequency']  + [''] * 3)   
        self.cpu_freq_value_nodes = []     
        for f_l in self.cpu.get_freq_labels():
            self.cpu_freq_value_nodes.append(self.store.append(self.cpu_freq_node, [f_l] + [''] * 3))

        self.cpu_usage_node = self.store.append(self.cpu_node, ['Usage']  + [''] * 3)   
        self.cpu_usage_value_nodes = []     
        for u_l in self.cpu.get_usage_labels():
            self.cpu_usage_value_nodes.append(self.store.append(self.cpu_usage_node, [u_l] + [''] * 3))

        self.gpu_node = self.store.append(self.host_node, [self.gpu.get_name()] + [''] * 3)

        self.gpu_freq_node = self.store.append(self.gpu_node, ['Frequency'] + [''] * 3)
        self.gpu_freq_value_node = self.store.append(self.gpu_freq_node, [self.gpu.get_freq_label()] + [''] * 3)

        self.hdd_node = self.store.append(self.host_node, [self.hdd.get_name()] + [''] * 3)

        self.hdd_temp_node = self.store.append(self.hdd_node, ['Temperature'] + [''] * 3)
        self.hdd_temp_value_node = self.store.append(self.hdd_temp_node, [self.hdd.get_temp_label()] + [''] * 3)

        self.bat_node = self.store.append(self.host_node, [self.bat.get_name()] + [''] * 3)

        self.bat_voltage_node = self.store.append(self.bat_node, ['Voltage'] + [''] * 3)
        self.bat_voltage_value_node = self.store.append(self.bat_voltage_node, [self.bat.get_voltage_label()] + [''] * 3) 

        self.bat_charge_node = self.store.append(self.bat_node, ['Charge'] + [''] * 3)
        self.bat_charge_value_node = self.store.append(self.bat_charge_node, [self.bat.get_charge_label()] + [''] * 3)


        scrolled_window = Gtk.ScrolledWindow()
        scrolled_window.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        scrolled_window.add(self.treeview)
        scrolled_window.set_min_content_height(200)
        self.add(scrolled_window)

        self.cpu_t_thread = threading.Thread(target=self.update_thread_callback)
        self.cpu_t_thread.daemon = True
        self.cpu_t_thread.start()


    def cpu_temp_thread_callback(self):
        while True:
            GObject.idle_add(self.cpu_temp_update_callback)
            time.sleep(INTERVAL)

    def cpu_freq_thread_callback(self):
        while True:
            GObject.idle_add(self.cpu_freq_update_callback)
            time.sleep(INTERVAL)

    def cpu_usage_thread_callback(self):
        while True:
            GObject.idle_add(self.cpu_usage_update_callback)


    def gpu_freq_thread_callback(self):
        while True:
            GObject.idle_add(self.gpu_freq_update_callback)
            time.sleep(INTERVAL)


    def hdd_temp_thread_callback(self):
        while True:
            GObject.idle_add(self.hdd_temp_update_callback)
            time.sleep(INTERVAL)


    def bat_voltage_thread_callback(self):
        while True:
            GObject.idle_add(self.bat_voltage_update_callback)
            time.sleep(INTERVAL)

    def bat_charge_thread_callback(self):
        while True:
            GObject.idle_add(self.bat_charge_update_callback)
            time.sleep(INTERVAL)



    def cpu_temp_update_callback(self):
        pass

    def cpu_freq_update_callback(self):
        pass

    def cpu_usage_update_callback(self):
        pass


    def gpu_freq_update_callback(self):
        pass


    def hdd_freq_update_callback(self):
        pass


    def bat_voltage_update_callback(self):
        pass

    def bat_charge_update_callback(self):
        pass



def main():
    cpu = Cpu()
    GObject.threads_init()
    win = MyWindow()
    win.connect('delete-event', Gtk.main_quit)
    win.show_all()
    Gtk.main()


if __name__ == '__main__':
    main()
