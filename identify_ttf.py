import sys
import subprocess
import hanzidentifier

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

    def analysis(self):
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

if __name__ == '__main__':
    file_path = sys.argv[1]
    print(file_path)
    t = TtfFile(file_path)
    t.analysis()
    print('File\t繁體\t簡體')
    print(t)