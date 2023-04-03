import os
import json

def rewrite_svg():
    dir = os.path.dirname(os.path.realpath(__file__))
 
    classes = [
        'svg-lakes',
        'svg-administration',
        'svg-housing',
        'svg-events',
        'svg-recreation',
        'svg-academic'
    ]

    functions = 'onmouseover="mouseOver(this)" onmouseout="mouseOut(this)" onmousedown="mouseDown(this)"'

    with open(os.path.join(dir, 'input.svg'), 'r') as inp, open(os.path.join(dir, 'outfile2.svg'), 'w') as out:
        locations = 0
        for line in inp:
            for class_string in classes:
                originalLine = line
                line = line.replace(f'class="{class_string}"', f'id="loc-{format(locations, "03d")}" class="{class_string}" {functions}')
                if originalLine is not line:
                    locations = locations + 1
            out.write(line)
    
    #with open(os.path.join(dir, 'output.svg'), 'w') as outfile:
    #    outfile.write('[')
    #    for subject in subjects:
    #        outfile.write(str(get_open_courses(subject['STVSUBJ_CODE'], term).json()))
    #        outfile.write(',')
    #    outfile.write(']')


def main():
    print('Main')
    rewrite_svg()

if __name__ == '__main__':
    main()