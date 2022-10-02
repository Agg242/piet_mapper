#!/usr/bin/python3

import argparse
import os
from PIL import Image

version = 1.0

PIET_COLORS_COUNT = 20
COMPONENTS_COUNT = 3
LIGHTNESS_COUNT = 3
MAX_RVB_VALUE = 255

RES_OK = 0
ERR_BAD_COLORS_COUNT = 1
ERR_BAD_HUE_SORTING = 2

if os.name == 'posix':
    RED = '\x1b[1;31m'
    GREEN = '\x1b[1;32m'
    ENDC = '\x1b[0m'
    BAD = RED + '[-]' + ENDC
    GOOD = GREEN + '[+]' + ENDC
else:
    RED = ''
    GREEN = ''
    ENDC = ''
    BAD = '[-]'
    GOOD = '[+]'



# hues, from 0 to 7
BLACK_HUE = 0
WHITE_HUE = 7
ref_hues = ['black', 'blue', 'green', 'cyan', 'red', 'magenta', 'yellow', 'white']


class CColor(object):
    def __init__(self, a_values: list):
        self.rvb = a_values
        self.rvb_weight = 1
        self.family = 0
        self.level = 0
        self.reference = None
        
    def AppendPixel(self, a_pixel):
        for component in range(0, COMPONENTS_COUNT):
            # keep average values
            val = self.rvb[component] * self.rvb_weight + a_pixel[component]
            self.rvb[component] = val // (self.rvb_weight + 1)
        self.rvb_weight += 1
        return

    def __str__(self):
        return f'{self.rvb}'

    def __repr__(self):
        return f'{self.rvb}'


def SetPietHues():
    colors = []
    colors.append([[0x00, 0x00, 0x00]])
    for hue in range(BLACK_HUE+1, WHITE_HUE):
        colors.append([[0x00, 0x00, 0x00], [0x00, 0x00, 0x00], [0x00, 0x00, 0x00]])
        for bit in range(0, COMPONENTS_COUNT):
            idx = 2 - bit
            if (hue & (1 << bit)) != 0:
                colors[hue][0][idx] = 0xc0
                colors[hue][1][idx] = 0xff
                colors[hue][2][idx] = 0xff
            else:
                colors[hue][0][idx] = 0x00
                colors[hue][1][idx] = 0x00
                colors[hue][2][idx] = 0xc0
    colors.append([[0xff, 0xff, 0xff]])
    return colors
    
    
def FindColor(a_pixel: list, a_diff: int, a_colors: list):
    good = True
    found = None
    for color in a_colors:
        good = True
        for component in range(0, COMPONENTS_COUNT):
            if abs(a_pixel[component] - color.rvb[component]) > a_diff:
                good = False
                break
        if good:
            found = color
            break
    return found
    
            

def FindColors(a_image, a_diff: int):
    colors = []
    pixels = a_image.load()
    for y in range(0, a_image.size[1]):
        for x in range(0, a_image.size[0]):
            pixel = pixels[x, y]            
            color = FindColor(pixel, a_diff, colors)
            if color == None:
                color = CColor(list(pixel))
                colors.append(color)
            else:
                color.AppendPixel(pixel)
    return colors



def SortHues(a_colors: list, a_diff: int):
    hues = [[], [], [], [], [], [], [], []]
    for color in a_colors:
        # find max component level
        max_level = 0
        for component in range(0, COMPONENTS_COUNT):
            if (color.rvb[component] + a_diff) > max_level:
                max_level = color.rvb[component]
        
        # find main components
        family = 0
        nb_components = 0
        for component in range(0, COMPONENTS_COUNT):
            if abs(color.rvb[component] - max_level) < a_diff:
                family |= 1 << (2 - component)
                color.level += color.rvb[component]
                nb_components += 1
        color.level = color.level // nb_components
                
        # detect black and white
        if family == 0b111:
            if color.rvb[0] < (MAX_RVB_VALUE // 2): # black
                family = 0
        hues[family].append(color)
        color.family = family
                
    return hues



def PrintHues(a_hues: list):
    for family in range(0, len(a_hues)):
        hue = a_hues[family]
        print(f'{ref_hues[family]}\t({family:04b}):')
        for color in hue:
            print(f'\t\t{color.rvb} -> {color.reference}')
    return



def SortColors(a_hues):
    for hue in range(BLACK_HUE+1, WHITE_HUE):
        a_hues[hue].sort(key=lambda color: color.level)
    return
        
        
def AssociateColors(a_hues, a_piet_colors):
    a_hues[0][0].reference = a_piet_colors[0][0]
    for hue in range(BLACK_HUE+1, WHITE_HUE):
        for lightness in range(0, LIGHTNESS_COUNT):
            a_hues[hue][lightness].reference = a_piet_colors[hue][lightness]
    a_hues[7][0].reference = a_piet_colors[7][0]
    return



def RemapColors(a_image, a_colors, a_diff, a_name):
    clean = Image.new(mode = "RGB", size = (a_image.size[0], a_image.size[1]))
    src = a_image.load()
    dst = clean.load()
    for y in range(0, a_image.size[1]):
        for x in range(0, a_image.size[0]):
            color = FindColor(src[x, y], a_diff, a_colors)
            dst[x, y] = tuple(color.reference)
    clean.save(a_name)
    return



def ProcessFile(args):
    global colors
    result = RES_OK
    
    image = Image.open(args.file)
    pixels = image.load()
    
    print('[*] Enumerating colors...')
    colors = FindColors(image, args.diff_threshold)
    len_cols = len(colors)
    if len_cols != PIET_COLORS_COUNT:
        if len_cols > PIET_COLORS_COUNT:
            action = 'in'
        else:
            action = 'de'
        print(f'{BAD} Error: found {len(colors)} colors, try {action}creasing diff threshold')
        result = ERR_BAD_COLORS_COUNT
        return result
    
    print(f'{GOOD} found {len(colors)} colors')
    
    
    print('[*] Sorting hues...')
    hues = SortHues(colors, args.level_threshold)
    for hue in range(BLACK_HUE+1, WHITE_HUE): 
        if len(hues[hue]) != LIGHTNESS_COUNT:
            result = ERR_BAD_HUE_SORTING
            print(f'{BAD} Error: bad hue sorting for {ref_hues[hue]}, found {len(hues[hue])} colors, try acting on level threshold')
    if len(hues[0]) != 1:
            result = ERR_BAD_HUE_SORTING
            print(f'{BAD} Error: bad hue sorting for {ref_hues[hue]}, found {len(hues[0])} colors, try acting on level threshold')
    if len(hues[7]) != 1:
            result = ERR_BAD_HUE_SORTING
            print(f'{BAD} Error: bad hue sorting for {ref_hues[hue]}, found {len(hues[7])} colors, try acting on level threshold')
    if result != RES_OK:
        PrintHues(hues)
        return result
    
    print(f'{GOOD} coherent hue sorting')
    
    
    print('[*] Sorting lightnesses...')
    SortColors(hues)
    print(f'{GOOD} done')
    
    print('[*] Associating to Piet palette...')
    piet_colors = SetPietHues()
    AssociateColors(hues, piet_colors)
    if args.verbose:
        PrintHues(hues)
    print(f'{GOOD} done')
    
    if args.output != '':
        output_name = args.output
    else:
        output_name = os.path.splitext(args.file)[0] + '.remapped.png'
    print(f'[*] Remapping colors and saving remapped image to {output_name}')
    RemapColors(image, colors, args.diff_threshold, output_name)
    print(f'{GOOD} done')
    return
    


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description = "Trivial Piet cleaner")
    parser.add_argument('file', help='Source Image File')
    parser.add_argument('-d', '--diff_threshold', help='threshold differentiating two colors, used to identify the 20 different piet colors', type=int, default=10)
    parser.add_argument('-l', '--level_threshold', help='threshold differentiating two color component values, used to identify to which hue a color belongs', type=int, default=10)
    parser.add_argument('-o', '--output', help='output file name, default to <name>.remapped.png', default='')
    parser.add_argument('-v', '--verbose', help='displays mapping information', action='store_true')
    args = parser.parse_args()
    ProcessFile(args)
    