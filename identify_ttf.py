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

    def parse(self):
        comp_proc = subprocess.run(['otfinfo', '-u', self.path], capture_output = True)
        output = comp_proc.stdout.decode('utf-8')
        lines = output.split('\n')
        for l in lines:
            unicode = l.split(' ')[0].replace('uni', '')
            f = Font(unicode)
            self.fonts.append(f)

    def get_traditional_cnt(self):
        cnt = 0
        for f in self.fonts:
            cnt += 1 if f.is_traditional() else 0
        return cnt
                
    def get_simplified_cnt(self):
        cnt = 0
        for f in self.fonts:
            cnt += 1 if f.is_simplified() else 0
        return cnt
    
    def __str__(self):
        return f'{self.path}\t{self.get_traditional_cnt()}\t{self.get_simplified_cnt()}'

    def move(self, destination:str):
        shutil.move(self.path, destination)

class TtfSortor:
    def __init__(self, dir:str):
        self.dir = os.path.abspath(dir)
        self.ttf_files = []
    
    def get_all_ttf_files(self):
        for file_path in os.listdir(self.dir):
            if file_path.upper().endswith('.TTF'):
                p = os.path.abspath(self.dir + '/' + file_path)
                f = TtfFile(p)
                f.parse()
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
            if f.get_traditional_cnt() > 9000:
                f.move(traditional_dir)
            else:
                f.move(simplified_dir)
            

if __name__ == '__main__':
    if len(sys.argv) == 1:
        print('Please input a directory includes TTF files.')
        exit()

    dir_path = sys.argv[1]
    sorter = TtfSortor(dir_path)
    sorter.get_all_ttf_files()
    sorter.classify()
