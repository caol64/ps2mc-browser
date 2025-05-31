# ps2mc-browser
English | [中文](README_zh.md)

![](data/1.gif)

`ps2mc-browser` is a `PS2` save file viewer that can parse the vertices and texture data of 3D icons in `PS2` saves, and then render the icons using OpenGL's capabilities.

If you're familiar with `PS2` or have a certain understanding of `PS2` save files, `ps2mc-browser` can be a very useful tool. It can not only help you view and understand the structure of the save files, but also display these saves on the canvas in the form of 3D icons.
## What's New
3D icons can exhibit different actions based on mouse interactions.

![](data/2.gif)

## Dependencies
The dependencies are listed below:
- Python3.10
- WxPython
- Numpy
- ModernGL
- PyGlm

## Quick Start
It is recommended to use `uv` to create and run in a virtual environment.

```shell
uv venv --python python3.10
uv pip install ps2mc-browser
uv run ps2mc-browser
```

Run the above command to open a GUI window. From the menu bar, select `Open File` and then select the `.ps2` file from your computer.

Alternatively, you can download the latest prebuilt releases from GitHub:
👉 [https://github.com/caol64/ps2mc-browser/releases](https://github.com/caol64/ps2mc-browser/releases)

## Documentation
- [Analyze the file system of the PS2 memory card](https://babyno.top/en/posts/2023/09/parsing-ps2-memcard-file-system/)
- [Export save files from the PS2 memory card](https://babyno.top/en/posts/2023/09/exporting-file-from-ps2-memcard/)
- [Analyze the 3D icons of PS2 game save files](https://babyno.top/en/posts/2023/10/parsing-ps2-3d-icon/)
- [Render the 3D icons of PS2 game save files using Python and OpenGL](https://babyno.top/en/posts/2023/10/rendering-ps2-3d-icon/)
- [Implementation of RLE algorithm in PS2](https://babyno.top/en/posts/2023/10/rle-algorithm-in-ps2/)
- [Texture image encoding algorithm A1B5G5R5 in PS2](https://babyno.top/en/posts/2023/10/ps2-texture-encoding-algorithm-a1b5g5r5/)
- [Analysis of Shader Code in PS2MC-Browser](https://babyno.top/en/posts/2023/12/ps2mc-browsers-shader-introduction/)


## Reference
- [gothi - icon.sys format](https://www.ps2savetools.com/documents/iconsys-format/)
- [Martin Akesson - PS2 Icon Format v0.5](http://www.csclub.uwaterloo.ca:11068/mymc/ps2icon-0.5.pdf)
- [Florian Märkl - mymcplus](https://git.sr.ht/~thestr4ng3r/mymcplus)
- [Ross Ridge - PlayStation 2 Memory Card File System](https://www.ps2savetools.com/ps2memcardformat.html)
