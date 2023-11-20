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
        self.icon_sys, self.icons = None, None
        self.panel = WxPanel(self)
        self.canvas = WxCanvas(self)
        self.statusbar = self.CreateStatusBar()
        self.on_init()
        self.games = list()

    def on_init(self):
        menubar = wx.MenuBar()
        menu = wx.Menu()
        menubar.Append(menu, "&File")
        menu.Append(wx.ID_OPEN)
        menu.Append(wx.ID_EXIT)
        self.SetMenuBar(menubar)
        self.Bind(wx.EVT_MENU, self.on_open_file, id=wx.ID_OPEN)
        self.Bind(wx.EVT_MENU, self.on_exit, id=wx.ID_EXIT)
        self.Bind(wx.EVT_CLOSE, self.on_exit)

        sizer = wx.BoxSizer(wx.HORIZONTAL)
        sizer.Add(self.canvas)
        sizer.Add(self.panel)
        self.SetSizerAndFit(sizer)

    def on_open_file(self, evt):
        file_dialog = wx.FileDialog(
            self, "Open", "", "", "(*.ps2)|*.ps2", wx.FD_OPEN | wx.FD_FILE_MUST_EXIST
        )
        file_dialog.ShowModal()
        self.mc_path = file_dialog.GetPath()
        file_dialog.Destroy()
        if self.mc_path is not None and self.mc_path != "":
            self.refresh_all()

    def on_exit(self, evt):
        if self.browser is not None:
            self.browser.destroy()
        self.canvas.destroy()
        self.Destroy()

    def refresh_all(self):
        """
        When a new memory card image is selected, refresh the canvas and game list.
        """
        if self.browser is not None:
            self.browser.destroy()
        self.browser = Browser(self.mc_path)
        root_dirs = self.browser.list_root_dir()
        self.games = [x.name for x in root_dirs]
        self.panel.update(self.games)
        self.update_selected_game(self.games[0])

    def update_selected_game(self, game):
        """
        When a game is selected, refresh the canvas.
        """
        self.selected_game = game
        self.icon_sys, self.icons = self.browser.get_icon(game)
        self.statusbar.SetStatusText(
            f"{self.icon_sys.subtitle[0]} {self.icon_sys.subtitle[1]}"
        )
        self.canvas.refresh(self.icon_sys, self.icons)


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


if __name__ == "__main__":
    app = WxApp(False)
    app.MainLoop()
