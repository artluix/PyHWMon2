import time
import glob
import subprocess

INTERVAL = 0.5

cpu_freq_table = []
cpu_temp_table = []
cpu_usage_table = []
gpu_freq_row = []
hdd_temp_str = []



def main():
    while 1:
        #cpu_t = cpu_temperature()
        #cpu_f = cpu_frequency()
        #hdd_t = hdd_temperature()
        #gpu_f = gpu_frequency()
        #print(cpu_t)
        #print(cpu_f)
        #print(hdd_t)
        #print(gpu_f)
        time.sleep(INTERVAL)


def min_list(list_1, list_2):
    return [min(a, b) for a, b in zip(list_1, list_2)]


def max_list(list_1, list_2):
    return [max(a, b) for a, b in zip(list_1, list_2)]


def cpu_temperature():
    # Indexes:  0 - Physical Id 0
    #           1 - Core 0
    #           2 - Core 1

    path = '/sys/class/hwmon/hwmon0/temp[0-9]_'

    temp_row = []
    for filename in sorted(glob.glob(path + 'input')):
        with open(filename, 'r') as f:
            temp_row.append(int(int(f.readline()) / 1000))

    global cpu_temp_table
    if not cpu_temp_table:
        cpu_temp_table = [temp_row] * 3
    else:
        cpu_temp_table[0] = temp_row
        cpu_temp_table[1] = min_list(cpu_temp_table[0], cpu_temp_table[1])
        cpu_temp_table[2] = max_list(cpu_temp_table[0], cpu_temp_table[2])

    temp_label = []
    for filename in sorted(glob.glob(path + 'label')):
        with open(filename, 'r') as f:
            temp_label.append(f.readline().rstrip('\n'))

    s = 'CPU temperature [Cur   Min    Max]\n'
    for l, temp_str in zip(temp_label, zip(*cpu_temp_table)):
        s += str(l).ljust(16) + '   '.join(str(x) + '°C' for x in temp_str)	+ '\n'

    return s


def cpu_frequency():
    # Indexes: 	0 - current
    # 		   	1 - min
    #			2 - max

    path = '/sys/devices/system/cpu/cpu[0-9]/cpufreq/cpuinfo_cur_freq'

    freq_row = []
    for filename in sorted(glob.glob(path)):
        with open(filename, 'r') as f:
            freq_row.append(int(int(f.readline()) / 1000))

    global cpu_freq_table
    if not cpu_freq_table:
        cpu_freq_table = [freq_row] * 3
    else:
        cpu_freq_table[0] = freq_row
        cpu_freq_table[1] = min_list(cpu_freq_table[0], cpu_freq_table[1])
        cpu_freq_table[2] = max_list(cpu_freq_table[0], cpu_freq_table[2])

    s = 'CPU frequency [Cur      Min       Max]\n'
    for i, freq_str in enumerate(zip(*cpu_freq_table)):
        s += 'Core' + str(i).ljust(10) + '   '.join(str(x) + 'MHz' for x in freq_str) + '\n'

    return s


def cpu_usage():
    pass


def gpu_frequency():
    # Indexes:  0 - current
    #           1 - min
    #           2 - max
    
    path = '/sys/class/drm/card0/gt_cur_freq_mhz'

    freq_cur = 0
    with open(path, 'r') as f:
        freq_cur = int(f.readline())

    global gpu_freq_row
    if not gpu_freq_row:
        gpu_freq_row = [freq_cur] * 3
    else:
        gpu_freq_row[0] = freq_cur
        gpu_freq_row[1] = min(freq_cur, gpu_freq_row[1])
        gpu_freq_row[2] = max(freq_cur, gpu_freq_row[2])

<<<<<<< a718309ae174afea608e281fd3e2233489b8a676
    s = 'GPU frequency [Cur,    Min,     Max]\n' + 'GPU'.ljust(14) + '   '.join(str(x) + 'MHz' for x in gpu_freq_row) + '\n'
=======
    s = 'GPU frequency [Cur,    Min,     Max]\n' q+ 'GPU'.ljust(14) + '   '.join(str(x) + 'MHz' for x in gpu_freq_row) + '\n'
>>>>>>> Add max/min values for all sensors

    return s


def hdd_temperature():
    t = int(subprocess.check_output(['hddtemp', '/dev/sda', '-n']))
    s = 'HDD temperature:\n' + str(t) + '°C'

    return s


def battery_status():
    pass

if __name__ == '__main__':
    main()