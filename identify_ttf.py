from ast import Param
import sys
import subprocess

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
        return False

    def is_simplified(self):
        return False

class TtfFile:
    def __init__(self, path:str):
        self.path = path
        self.fonts = []

    def analysis(self):
        comp_proc = subprocess.run(['otfinfo', '-u', self.path], capture_output = True)
        output = comp_proc.stdout.decode('utf-8')
        lines = output.split('\n')
        for l in lines:
            unicode = l.split(' ')[0].replace('uni', '')
            f = Font(unicode)
            self.fonts.append(f)

if __name__ == '__main__':
    # file_path = sys.argv[1]
    file_path = "汉仪槑萌体.TTF"
    t = TtfFile(file_path)
    t.analysis()
