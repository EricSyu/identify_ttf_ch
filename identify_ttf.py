import sys
import subprocess
import hanzidentifier
import os
import shutil

class Font:
    def __init__(self, unicode:str):
        self.unicode = unicode
        self.char = self.__to_char(unicode)
    
    def __to_char(self, unicode:str):
        try:
            b = bytes.fromhex(unicode)
            return b.decode('utf_16_be')
        except UnicodeDecodeError as err:
            return f'invalid:{err.reason}'
    
    def is_traditional(self):
        return hanzidentifier.is_traditional(self.char)

    def is_simplified(self):
        return hanzidentifier.is_simplified(self.char)

class TtfFile:
    def __init__(self, path:str):
        self.path = path
        self.fonts = []
        self.tra_cnt = -1
        self.sim_cnt = -1

    def parse(self):
        comp_proc = subprocess.run(['otfinfo', '-u', self.path], capture_output = True)
        output = comp_proc.stdout.decode('utf-8')
        lines = output.split('\n')
        for l in lines:
            unicode = l.split(' ')[0].replace('uni', '')
            f = Font(unicode)
            self.fonts.append(f)

    def get_traditional_cnt(self):
        if self.tra_cnt == -1:
            cnt = 0
            for f in self.fonts:
                cnt += 1 if f.is_traditional() else 0
            self.tra_cnt = cnt
        return self.tra_cnt
    
    def get_simplified_cnt(self):
        if self.sim_cnt == -1:
            cnt = 0
            for f in self.fonts:
                cnt += 1 if f.is_simplified() else 0
            self.sim_cnt = cnt
        return self.sim_cnt
    
    def __str__(self):
        return f'{self.path}\t{self.get_traditional_cnt()}\t{self.get_simplified_cnt()}'

    def move(self, destination:str):
        shutil.move(self.path, destination)

class TtfSortor:
    def __init__(self, dir:str, tra_bondary:int = 9000):
        self.dir = os.path.abspath(dir)
        self.ttf_files = []
        self.tra_bondary = tra_bondary
    
    def get_all_ttf_files(self) -> list[TtfFile]:
        for file_path in os.listdir(self.dir):
            if file_path.upper().endswith('.TTF'):
                p = os.path.abspath(self.dir + '/' + file_path)
                f = TtfFile(p)
                self.ttf_files.append(f)
        return self.ttf_files

    def classify(self):
        traditional_dir = self.dir + '/traditional'
        simplified_dir = self.dir + '/simplified'
        if not os.path.exists(traditional_dir):
            os.mkdir(traditional_dir)
        if not os.path.exists(simplified_dir):
            os.mkdir(simplified_dir)
        
        for f in self.ttf_files:
            f.parse()
            tra_cnt = f.get_traditional_cnt()
            if tra_cnt > self.tra_bondary:
                f.move(traditional_dir)
            else:
                f.move(simplified_dir)
    
    def print_support_fonts_cnt(self):
        for f in self.ttf_files:
            print(f)

if __name__ == '__main__':
    argLen = len(sys.argv)
    if argLen == 1 or argLen == 2:
        print('It supports print and classify mode.')
        print('1. Please input print and a directory includes TTF files.')
        print('ex: python identify_ttf_ch print ./ttf_files')
        print('2. Please input classify and a directory includes TTF files and a traditional bondary number.')
        print('ex: python identify_ttf_ch classify ./ttf_files 9000')
        exit()

    mode = sys.argv[1]
    dir_path = sys.argv[2]
    if mode.upper() == 'print':
        sorter = TtfSortor(dir_path)
    elif mode.upper() == 'classify':
        tra_bondary = 9000
        if argLen == 3 and str.isnumeric(sys.argv[3]):
            tra_bondary = int(sys.argv[3])
        
        sorter = TtfSortor(dir_path, tra_bondary)
        sorter.get_all_ttf_files()
        sorter.classify()
