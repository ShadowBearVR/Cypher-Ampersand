import os
import json

def rewrite_svg():
    dir = os.path.dirname(os.path.realpath(__file__))
 
    replace_class = 'cls-1'

    functions = 'onmouseover="mouseOver(this)" onmouseout="mouseOut(this)" onmousedown="mouseDown(this)"'

    with open(os.path.join(dir, 'GOOD_ISC.svg'), 'r') as inp, open(os.path.join(dir, 'ISC_FULL.svg'), 'w') as out:
        locations = 0
        for line in inp:
            originalLine = line
            line = line.replace(f'class="{replace_class}"', f'id="path{format(locations, "03d")}" class="{replace_class}" {functions}')
            if originalLine is not line:
                locations = locations + 1
            out.write(line)


def main():
    print('Main')
    rewrite_svg()

if __name__ == '__main__':
    main()