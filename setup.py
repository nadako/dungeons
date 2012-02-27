from distutils.core import setup
import py2exe

setup(
    windows=['fov.py'],
    data_files=['SDL.dll', 'libtcod-mingw.dll', 'terminal.png']
)
