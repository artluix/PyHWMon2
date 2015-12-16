
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