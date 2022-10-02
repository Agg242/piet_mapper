# piet_mapper
Piet color palette remapper

Small utility helping mapping piet colors to a piet program image.

A use case would be if you get a piet program through printing and scanning. The original piet colors would be lost, but if you succeed in keeping hues distinction, piet_mapper will help associating current colors to original piet colors.

eg:
```  
  $ ./piet_mapper.py -d 7 -l 24 -o remapped.png scanned_piet.png
  [*] Enumerating colors...
  [+] found 20 colors
  [*] Sorting hues...
  [+] coherent hue sorting
  [*] Sorting lightnesses...
  [+] done
  [*] Associating to Piet palette...
  [+] done
  [*] Remapping colors and saving remapped image to remapped.png
  [+] done

  $ npiet -v remapped.png
  info: verbose set to 1
  info: using file remapped.png
  info: got 50 x 50 pixel with 256 cols
  info: codelsize guessed is 1 pixel
  CTF{Am1g4_rul3Z}
```

Prerequisite:
  Python Pillow module installed. (https://python-pillow.org/)
  
A prep work is required before using piet_mapper, with your favorite image manipulation program (name it Photoshop, The Gimp or whatever):
  - any graphics unrelated to piet must be removed
  - the image must be precisely cropped and scaled so that one pixel represents one codel, this also helps eliminating unwanted anti-aliasing
  - hues differentiation should be improved, eg by applying a color profile or whatever helps

```
Usage: piet_mapper.py [-h] [-d DIFF_THRESHOLD] [-l LEVEL_THRESHOLD] [-o OUTPUT] [-v] file
Trivial Piet cleaner
positional arguments:                                                                                                                                               
  file                  Source Image File
options:                                                                                                                                                          
  -h,  --help            show this help message and exit                                                                                                             
  -d DIFF_THRESHOLD, --diff_threshold DIFF_THRESHOLD                                                                                                                                      threshold differentiating two colors, used to identify the 20 different piet colors                                                         
  -l LEVEL_THRESHOLD, --level_threshold LEVEL_THRESHOLD                                                                                                                                  threshold differentiating two color component values, used to identify to which hue a color belongs                                        
  -o OUTPUT, --output OUTPUT                                                                                                                                                              output file name, default to <name>.remapped.png                                                                                            
  -v, --verbose         displays mapping information
```
 
  
DIFF_THRESHOLD is the acceptable delta of any color component. 
As an example, a DIFF_THRESHOLD of 1 means that any component difference differentiate two colors.
In case of 20, two colors are considered different if the any component difference is greater or equal to 20.
Eg: (220, 10, 50) is considered the same color as (239, 1, 32).
This parameter helps isolating precisely 20 colors in the image:
```
  > python3 piet_mapper.py -d 20 scanned_piet.png
  [*] Enumerating colors...
  [-] Error: found 19 colors, try decreasing diff threshold

  > piet_mapper.py -d 5 scanned_piet.png
  [*] Enumerating colors...
  [-] Error: found 22 colors, try increasing diff threshold

  > piet_mapper.py -d 7 scanned_piet.png
  [*] Enumerating colors...
  [+] found 20 colors
```

LEVEL_THRESHOLD is the acceptable delta of any color component while looking for main components of each color. This parameter helps refining color assignment to the six colored hues. As long as assignment is wrong, piet_mapper will fail and color assignment will be displayed.
```
  $ ./piet_mapper.py -d 7 -l 10 -o remapped.png scanned_piet.png
  [*] Enumerating colors...
  [+] found 20 colors
  [*] Sorting hues...
  [-] Error: bad hue sorting for green, found 5 colors, try acting on level threshold
  [-] Error: bad hue sorting for cyan, found 2 colors, try acting on level threshold
  [-] Error: bad hue sorting for red, found 4 colors, try acting on level threshold
  [-] Error: bad hue sorting for magenta, found 2 colors, try acting on level threshold
  [-] Error: bad hue sorting for yellow, found 2 colors, try acting on level threshold
  black   (0000):
                  [0, 0, 0] -> None
  blue    (0001):
                  [47, 72, 163] -> None
                  [184, 174, 219] -> None
                  [58, 84, 173] -> None
  green   (0010):
                  [73, 192, 182] -> None
                  [66, 186, 79] -> None
                  [170, 193, 42] -> None
                  [183, 226, 165] -> None
                  [94, 194, 69] -> None
  cyan    (0011):
                  [110, 206, 214] -> None
                  [186, 231, 232] -> None
  red     (0100):
                  [236, 35, 48] -> None
                  [191, 30, 46] -> None
                  [247, 166, 178] -> None
                  [229, 170, 213] -> None
  magenta (0101):
                  [172, 61, 164] -> None
                  [150, 50, 157] -> None
  yellow  (0110):
                  [229, 235, 37] -> None
                  [242, 245, 170] -> None
  white   (0111):
                  [253, 253, 253] -> None
```        

OUTPUT is the name of the output file if mapping succeeds. By default, the input file name is used and get ".remapped" appended just before ".png".



  
