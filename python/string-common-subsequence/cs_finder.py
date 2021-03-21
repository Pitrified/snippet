from random import choices
from random import randint

def ascii_to_char(ascii_val):
    return str(chr(ascii_val))

def generate_string_by_len(length, num_possible_chars):
    '''generate a list of random chars of requested length

    ascii AZ 65-90 az 97-122
    '''
    #  print(f'\nnum_possible_chars {num_possible_chars}')
    if num_possible_chars <= 26:
        possible_chars_ascii = range(65, 65+num_possible_chars)
    elif num_possible_chars <= 26*2:
        possible_chars_ascii = list(range(65, 65+26))
        possible_chars_ascii.extend(range(97, 97+num_possible_chars-26))
    else:
        possible_chars_ascii = list(range(65, 65+26))
        possible_chars_ascii.extend(range(97, 97+26))
        #  print(f'No more than 52 num_possible_chars')
        # TODO LOGGERS BY JOVE

    #  print(f'pca {possible_chars_ascii}')

    #  possible_chars = map(ascii_to_char, possible_chars_ascii)
    possible_chars = list(map(ascii_to_char, possible_chars_ascii))

    #  print(list(possible_chars))
    #  print(f'{possible_chars}')

    S = choices(possible_chars, k=length)

    #  print(S)
    #  print(len(S))

    return S

def generate_similar_string_nonrepeating(length, num_errors):
    numbers = range(length)
    #  X = list( map( '_{:04d}'.format, numbers) )
    char_len = 2
    format_string = f' {{:0{char_len}d}}'
    #  print(format_string)
    X = list( map( format_string.format, numbers) )
    #  print(f'{X}')
    Y = X.copy()

    #  num_errors = 5

    error_string = f'+{{:0{char_len}d}}'
    #  print(error_string)
    for i in range(num_errors):
        where = randint(1, len(X))
        X.insert(where, error_string.format(i))

    error_string = f'-{{:0{char_len}d}}'
    #  print(error_string)
    for i in range(num_errors):
        where = randint(1, len(Y))
        Y.insert(where, error_string.format(i))

    #  print(f'{"".join(X)}')

    return X, Y

class LCSfinder:
    def __init__(self,# rows, columns,
            X,
            Y
            ):
        #  self.rows = rows
        #  self.columns = columns

        self.X = X.copy()
        self.Y = Y.copy()
        self.m = len(self.X)-1
        self.n = len(self.Y)-1

        self.B = {}
        self.cost = {}

    def find_LCS(self):
        '''Find longes common subsequence using memoized approach'''
        self.init_lcs()
        self.rec_lcs(self.m, self.n, 0)

    def init_lcs(self):
        '''init base case'''
        for i in range(self.m+1):
            #  self.B[ (i,0) ] = 0
            #  self.cost[ (i,0) ] = 0
            self.B[ (i,-1) ] = 0
            self.cost[ (i,-1) ] = 0

        for j in range(self.n+1):
            #  self.B[ (0,j) ] = 0
            #  self.cost[ (0,j) ] = 0
            self.B[ (-1,j) ] = 0
            self.cost[ (-1,j) ] = 0

        # we have B as a dict to save memory
        #  for i in range(1,self.m):
            #  for j in range(1,self.n):
                #  self.B[ (i,j) ] = -1

    def rec_lcs(self, i, j, level):
        '''core function'''
        self.printl(f'doing X[{i}]={self.X[i]} Y[{j}]={self.Y[j]}', level)

        #  if i==0 or j==0:
        if i==-1 or j==-1:
            self.printl(f'Returning base', level)
            return 0

        if not (i,j) in self.B:
            # populate this for the first and only time
            if self.X[i] == self.Y[j]:
                self.printl(f'equal X[{i}]={self.X[i]}', level)
                self.B[ (i,j) ] = 1
                self.cost[(i,j)] = 1+self.rec_lcs(i-1, j-1, level+1)
                #  self.printl(f'ret cost {1+self.rec_lcs(i-1, j-1)} self.cost {self.cost[(i,j)]}', level)
            else:
                #  self.printl(f'l calling {i-1} {j}', level)
                cost_up = self.rec_lcs(i-1,j, level+1) # arguably this is not needed, the cost is saved in self.cost anyway
                #  self.printl(f'r calling {i} {j-1}', level)
                cost_left = self.rec_lcs(i,j-1, level+1)
                if cost_up > cost_left:
                #  if self.rec_lcs(i-1,j) < self.rec_lcs(i,j-1):
                    self.printl(f'less {i} {j} {cost_up} {cost_left}', level)
                    self.B[ (i,j) ] = 2
                    #  self.cost[(i,j)] = self.rec_lcs(i-1, j) # so this is fast
                    self.cost[(i,j)] = cost_up
                else:
                    self.printl(f'more {i} {j} {cost_up} {cost_left}', level)
                    self.B[ (i,j) ] = 3
                    #  self.cost[(i,j)] = self.rec_lcs(i, j-1)
                    self.cost[(i,j)] = cost_left

        return self.cost[(i,j)]

    def check_is_cs(self, ssq=None):
        if ssq is None:
            #  ssq = self.get_str_lcs()
            ssq = self.get_list_lcs()

        if self.is_cs(self.X, ssq):
            #  print(f'{ssq} is subsequence of {"".join(self.X)}')
            print(f'X is correct')
        else:
            return False

        if self.is_cs(self.Y, ssq):
            #  print(f'{ssq} is subsequence of {"".join(self.Y)}')
            print(f'Y is correct')
        else:
            return False

        return True

    def is_cs(self, s, ssq):
        i=0
        lens = len(s)
        #  print(f'checking {ssq}, lens {lens} in {"".join(s)}')

        for j, c in enumerate(ssq):
            #  print(f'doing {j} {c}, i {i} s[{i}] {s[i]}')
            while c != s[i]:
                i += 1
                if i>=lens:
                    # not a subsequence as the string has ended
                    return False
            #  print(f'found c[{j}] {c}, i {i} s[{i}] {s[i]}')
            i += 1

        return True

    def printl(self, string, level):
        #  spaces = ' ' * level
        spaces = '    ' * level
        print(f'{spaces}{string}')

    def print_stats(self):
        tot_subproblems = (self.m+1)*(self.n+1)
        solved = len(self.B)
        print(f'Solved {solved} out of {tot_subproblems} subproblems')
        print(f'Ratio {solved/tot_subproblems:.6f}')

    def get_str_B(self):
        #  print(self.get_str_vertical_numbers())
        #  strb = ''
        strb = self.get_str_vertical_numbers() + '\n'
        for i in range(0,self.m+1):
            for j in range(0,self.n+1):
                if (i,j) in self.B:
                    if self.B[ (i,j) ] == 0:
                        strb += '0'
                    elif self.B[ (i,j) ] == 1:
                        strb += '\\'
                    elif self.B[ (i,j) ] == 2:
                        strb += '|'
                    elif self.B[ (i,j) ] == 3:
                        strb += '-'
                    else:
                        print(f'My dude something is weird in {self.B[ (i,j) ]}')
                else:
                    strb += '.'

            strb += '\n'

        return strb

    def get_str_cost(self):
        strb = ''
        for i in range(0,self.m+1):
            for j in range(0,self.n+1):
                if (i,j) in self.cost:
                    #  strb += f'{self.cost[(i,j)]: 2d}'
                    #  strb += f'{self.cost[(i,j)]:1d}'
                    strb += f'{self.cost[(i,j)]:1d}'[-1]
                else:
                    #  strb += ' .'
                    strb += '.'

            strb += '\n'

        return strb

    def get_list_lcs_rec(self, i, j):
        if (i,j) in self.B:
            if self.B[ (i,j) ] == 1:
                #  print(f'match at X[{i}]={self.X[i]} Y[{j}]={self.Y[j]}')
                shorter = self.get_list_lcs_rec(i-1, j-1)
                shorter.append(self.X[i])
                return shorter
            elif self.B[ (i,j) ] == 2:
                return self.get_list_lcs_rec(i-1, j)
            elif self.B[ (i,j) ] == 3:
                return self.get_list_lcs_rec(i, j-1)
            #  else:
                #  print(f'My dude something is weird in {self.B[ (i,j) ]}')
                #  print(f'X[{i}]={self.X[i]} Y[{j}]={self.Y[j]}')

        #  print(f'returning {i} {j}')
        return []

    def get_list_lcs(self):
        return self.get_list_lcs_rec(self.m, self.n)

    def get_str_lcs_rec(self, i, j):
        if (i,j) in self.B:
            if self.B[ (i,j) ] == 1:
                #  print(f'match at X[{i}]={self.X[i]} Y[{j}]={self.Y[j]}')
                return self.get_str_lcs_rec(i-1, j-1) + self.X[i]
            elif self.B[ (i,j) ] == 2:
                return self.get_str_lcs_rec(i-1, j)
            elif self.B[ (i,j) ] == 3:
                return self.get_str_lcs_rec(i, j-1)
            #  else:
                #  print(f'My dude something is weird in {self.B[ (i,j) ]}')
                #  print(f'X[{i}]={self.X[i]} Y[{j}]={self.Y[j]}')

        return ''

    def get_str_lcs(self):
        return self.get_str_lcs_rec(self.m, self.n)

    def get_str_input(self):
        #  print(f'\nInput strings:')
        inpstr = self.get_str_vertical_numbers(True) + '\n'
        #  print(self.get_str_vertical_numbers())
        for c in self.X:
            #  print(f'{c}', end='')
            inpstr += f'{c}'
        inpstr += f'\n'
        for c in self.Y:
            #  print(f'{c}', end='')
            inpstr += f'{c}'
        return inpstr

    def get_str_vertical_numbers(self, width_max=False):
        vertstr = ''
        if width_max:
            max_num = max( len(self.X), len(self.Y) ) 
        else:
            max_num = len(self.Y)

        #  for i in range( max( len(self.X), len(self.Y) ) ):
        #  for i in range(len(self.Y) ):
        for i in range(max_num):
            #  print(f'{i//10}'[-1], end='')
            vertstr += f'{i//10}'[-1]
        vertstr += '\n'
        for i in range(max_num):
            #  print(f'{i:1d}'[-1], end='')
            vertstr += f'{i:1d}'[-1]
        return vertstr

    def get_str_B_cost(self):
        strB = self.get_str_B().split()
        strcost = self.get_str_vertical_numbers().split()
        strcost.extend(self.get_str_cost().split() )

        sbc = ''
        for b, c in zip(strB, strcost):
            sbc += f'{b} {c}\n'

        return sbc
