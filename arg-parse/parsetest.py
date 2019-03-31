import argparse

# https://docs.python.org/dev/howto/argparse.html

def parse_arguments():
    # setup parser
    parser = argparse.ArgumentParser(
            description='Short argparse usage example',
            )

    # positional args (mandatory)
    parser.add_argument('echo', help='echo this string')

    # specify a type for the arg
    parser.add_argument("square", type=int,
            help="display a square of a given number")

    # define a flag
    parser.add_argument("-v", "--verbose",
            action="store_true",                # store only true or false value
            help="increase output verbosity")

    # limit possible values
    parser.add_argument('-n', '--number',
            type=int,
            choices=[0,1,2],
            help='number can only be 0,1,2',
            )

    # fancy option with count
    parser.add_argument('-r', '--repeat',
            action='count',
            default=0,
            help='you can repeat this option and it will be counted',
            )

    # last line to parse them
    args = parser.parse_args()

    #  parse the args even more if needed
    args_parsed = { a : v for a, v in args._get_kwargs() }
    return args_parsed

def main(x, y, echo, square, verbose, number, repeat=1):
    print(f'echo: {echo}')
    print(f'repeat: {repeat}')

if __name__ == '__main__':
    arguments = parse_arguments()
    print(f'{arguments}')

    myx = 9
    myy = 3
    main(myx, myy, **arguments)
