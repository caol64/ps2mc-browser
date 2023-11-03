import sys
sys.path.append('src')
import wx

from wxwindow import WxFrame


def test_gui():
    app = wx.App(False)
    frame = WxFrame("PS2 memory card browser")
    app.SetTopWindow(frame)
    frame.Show(True)
    frame.Close()
    app.Destroy()
