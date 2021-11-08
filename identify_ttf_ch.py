import sys
import subprocess
import hanzidentifier
import os
import shutil

class Font:
    def __init__(self, unicode:str):
        self._unicode = unicode
        self._char = ''
    
    @property
    def char(self):
        if self._char == '':
            try:
                b = bytes.fromhex(self._unicode)
                self._char = b.decode('utf_16_be')
            except UnicodeDecodeError as err:
                self._char = f'invalid:{err.reason}'
        return self._char
    
    def is_traditional(self):
        return hanzidentifier.is_traditional(self.char)

    def is_simplified(self):
        return hanzidentifier.is_simplified(self.char)

class TtfFile:
    def __init__(self, path:str):
        self._path = path
        self._fonts = []
        self._traditional_cnt = -1
        self._simplified_cnt = -1

    @property
    def path(self):
        return self._path

    @property
    def fonts(self):
        if len(self._fonts) == 0:
            comp_proc = subprocess.run(['otfinfo', '-u', self._path], capture_output = True)
            output = comp_proc.stdout.decode('utf-8')
            lines = output.split('\n')
            for l in lines:
                unicode = l.split(' ')[0].replace('uni', '')
                f = Font(unicode)
                self._fonts.append(f)
        return self._fonts

    @property
    def traditional_cnt(self):
        if self._traditional_cnt == -1:
            self._traditional_cnt = 0
            for f in self.fonts:
                self._traditional_cnt += 1 if f.is_traditional() else 0
        return self._traditional_cnt
    
    @property
    def simplified_cnt(self):
        if self._simplified_cnt == -1:
            self._simplified_cnt = 0
            for f in self.fonts:
                self._simplified_cnt += 1 if f.is_simplified() else 0
        return self._simplified_cnt
    
    def __str__(self):
        return f'{self._path}\t{self.traditional_cnt}\t{self.simplified_cnt}'

    def move(self, destination:str):
        shutil.move(self._path, destination)

class TtfSortor:
    def __init__(self, dir:str, tra_bondary:int = 9000):
        self._dir = os.path.abspath(dir)
        self._ttf_files = []
        self._tra_bondary = tra_bondary
    
    @property
    def ttf_files(self) -> list[TtfFile]:
        if len(self._ttf_files) == 0:
            for file_path in os.listdir(self._dir):
                if file_path.upper().endswith('.TTF'):
                    p = os.path.abspath(self._dir + '/' + file_path)
                    f = TtfFile(p)
                    self._ttf_files.append(f)
        return self._ttf_files

    def classify(self):
        traditional_dir = self._dir + '/traditional'
        simplified_dir = self._dir + '/simplified'
        if not os.path.exists(traditional_dir):
            os.mkdir(traditional_dir)
        if not os.path.exists(simplified_dir):
            os.mkdir(simplified_dir)
        
        for f in self.ttf_files:
            tra_cnt = f.traditional_cnt
            if tra_cnt > self._tra_bondary:
                f.move(traditional_dir)
            else:
                f.move(simplified_dir)
    
    def print_ch_fonts_cnt(self):
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
    if mode.lower() == 'print':
        sorter = TtfSortor(dir_path)
        sorter.print_ch_fonts_cnt()
    elif mode.lower() == 'classify':
        tra_bondary = 9000
        if argLen == 4 and str.isnumeric(sys.argv[3]):
            tra_bondary = int(sys.argv[3]) 
        
        sorter = TtfSortor(dir_path, tra_bondary)
        sorter.classify()
