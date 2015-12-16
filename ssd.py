import subprocess


class SSD:

    def __init__(self):
        self.name = self.__name()
        self.temp_label = 'SSD'
        self.temp_row = []


    def get_name(self):
        return self.name


    def get_temp_label(self):
        return self.temp_label

    def get_temperature(self):
        self.__temperature()
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
