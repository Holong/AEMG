class Process:
    """description of class"""

    def __init__(self):    
        self.c_file = []
        self.h_file = []
        self.port = []
        self.name = 0

    def set_name(self, str):
        self.name = str

    def set_cfile(self, str):
        self.c_file.append(str)

    def set_hfile(self, str):
        self.h_file.append(str)

    def set_process_port(self, name, type, func):
        self.port.append((name, type, func))
