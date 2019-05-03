from random import choices

def ascii_to_char(ascii_val):
    return str(chr(ascii_val))

def test_generate_string():
    generate_string_by_len(10, 5)
    generate_string_by_len(10, 26)
    generate_string_by_len(10, 26*2)
    generate_string_by_len(10, 26*2+1)

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

    return S

class LCSfinder:
    def __init__(self, rows, columns,
            X,
            Y
            ):
        self.rows = rows
        self.columns = columns

        self.X = X.clone()
        self.Y = Y.clone()
