import wx
from browser import Browser
from wxcanvas import WxCanvas


class WxApp(wx.App):
    def OnInit(self):
        frame = WxFrame("PS2 memory card browser")
        self.SetTopWindow(frame)
        frame.Show(True)
        return True


class WxFrame(wx.Frame):
    def __init__(self, title):
        frame_style = wx.DEFAULT_FRAME_STYLE & ~(wx.RESIZE_BORDER | wx.MAXIMIZE_BOX)
        wx.Frame.__init__(self, None, -1, title, style=frame_style)
        self.browser = None
        self.mc_path = None
        self.selected_game = None
        self.icon_sys, self.icon = None, None
        self.panel = WxPanel(self)
        self.canvas = WxCanvas(self)
        self.statusbar = self.CreateStatusBar()
        self.on_init()
        self.running = True

    def on_init(self):
        menubar = wx.MenuBar()
        menu = wx.Menu()
        menubar.Append(menu, "&File")
        menu.Append(wx.ID_OPEN)
        menu.Append(wx.ID_EXIT)
        self.SetMenuBar(menubar)
        self.Bind(wx.EVT_MENU, self.on_open_file, id=wx.ID_OPEN)

        sizer = wx.BoxSizer(wx.HORIZONTAL)
        sizer.Add(self.canvas)
        sizer.Add(self.panel)
        self.SetSizerAndFit(sizer)

    def on_open_file(self, evt):
        file_dialog = wx.FileDialog(self, "Open", "", "",
                                    "(*.ps2)|*.ps2",
                                    wx.FD_OPEN | wx.FD_FILE_MUST_EXIST)
        file_dialog.ShowModal()
        self.mc_path = file_dialog.GetPath()
        file_dialog.Destroy()
        self.refresh_all()

    def refresh_all(self):
        self.browser = Browser(self.mc_path)
        root_dirs = self.browser.list_root_dir()
        games = [x.name for x in root_dirs]
        self.panel.update(games)

    def update_selected_game(self, game):
        self.selected_game = game
        self.icon_sys, self.icon = self.browser.get_icon(game)
        self.statusbar.SetStatusText(f'{self.icon_sys.subtitle[0]} {self.icon_sys.subtitle[1]}')
        self.canvas.refresh(self.icon_sys, self.icon)


class WxPanel(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent)
        self.parent = parent
        self.lb = wx.ListBox(self, size=(250, 480))
        self.Bind(wx.EVT_LISTBOX, self.on_select, self.lb)

    def on_select(self, evt):
        self.parent.update_selected_game(self.lb.GetStringSelection())

    def update(self, games):
        self.lb.Clear()
        if games is not None and len(games) > 0:
            for game in games:
                self.lb.Append(game)
            self.lb.Select(0)
            self.on_select(None)


if __name__ == '__main__':
    app = WxApp(False)
    app.MainLoop()
