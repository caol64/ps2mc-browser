# pyinstaller.py
import os
import PyInstaller.__main__

app_name = 'ps2mc-browser'
app_file = 'src/wxwindow.py'
hidden_import = 'glcontext'
datas = ['src/shaders', 'shaders']

PyInstaller.__main__.run(
    [
        '--name=%s' % app_name,
        '--windowed',
        '--onefile',
        #'--icon=%s' % 'path/to/your/icon.ico',
        '--add-data=%s' % os.pathsep.join(datas),
        '--hidden-import=%s' % hidden_import,
        app_file,
    ]
)
