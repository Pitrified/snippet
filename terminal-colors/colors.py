from os import system

def main():
    cs = 'echo -n "\\033[{}m{}\\033[0m"'
    system(cs.format(32, 'Hi\n'))

    cs = r'echo -n "\e[{code}m{chars}\e[0m"'
    system(cs.format(code=4, chars='Hi\n'))

    print("\033[31;1;4mHello\033[0m")
    print("\033[31;1;4;3;9mHello\033[0m")
    print("\033[31;1;4;3mHello\033[0m")
    print("\033[31;1;4mHello\033[0m")
    cs = "\033[{}m{}\033[0m"

    styles = range(0,8+1)
    colors = list(range(30,37+1))+list(range(90,97+1))
    backgrounds = list(range(40,47+1)) + list(range(100,107+1))
    for s in styles:
        for c in colors:
            for b in backgrounds:
                code = f'{s};{c};{b}'
                print(cs.format(code, code) , end='')
                print(' ' , end='')
            print()
        print()



if __name__ == '__main__':
    main()

# NOTE
# on a terminal, echo -e is needed for it to parse escape sequences

# More info:
# martin-thoma.com/colorize-your-scripts-output/
# mewbies.com/motd_console_codes_color_chart_in_color_black_background.htm

