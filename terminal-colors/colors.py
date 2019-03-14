from os import system

def main():
    cs = 'echo -n "\\033[{}m{}\\033[0m"'
    system(cs.format(32, 'Hi\n'))

if __name__ == '__main__':
    main()


# More info:
# martin-thoma.com/colorize-your-scripts-output/
# mewbies.com/motd_console_codes_color_chart_in_color_black_background.htm

