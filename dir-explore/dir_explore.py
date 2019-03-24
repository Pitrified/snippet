#!python2

from os import listdir
from os.path import isfile
from os.path import join
from os.path import getsize

class Folder():
    def __init__(self, path):
        self.size = 0
        self.children = []
        self.path = path
        self.ty = 'fol'

    def __str__(self):
        schi = ''
        for f in self.children:
            schi += str(f)
        return schi

    def __repr__(self):
        #    schi = '['
        schi = ''
        for f in self.children:
            schi += 'sp '+self.path + '@\n'
            schi += 're '+repr(f)+'$\n'
        #    schi += ']'
        return schi
        # return self.path

class File():
    def __init__(self, path):
        self.path = path
        self.size = getsize(path)
        self.ty = 'fil'

    def __str__(self):
        return self.path

    def __repr__(self):
        re = ''
        re += self.path
        #    re = '\n'
        re += ':'
        re += str(self.size)
        return re

def popola(fol):
    path = fol.path
    print('in popola con {}'.format(path))
    for f in listdir(path):
        child = join(path, f)
        # print('figlio {}'.format(child))
        if isfile(child):
            fol.children.append(File(child))
        else:
            fol.children.append(Folder(child))
    for f in fol.children:
        if f.ty == 'fil':
            # print('file {}'.format(f.path))
            pass
        else:
            popola(f)

def main():
    # print('main')
    # afile = File('unfile')
    # afolder = Folder('unacartella')
    # print('{} {}'.format(afile.name, afolder.name))
    # print('{} {}'.format(type(afile), type(afolder)))
    path_to_root = 'root'
    rootfolder = Folder(path_to_root)
    popola(rootfolder)
    #    print(rootfolder.children)
    #    print(rootfolder)
    print(repr(rootfolder))

if __name__ == '__main__':
    main()
