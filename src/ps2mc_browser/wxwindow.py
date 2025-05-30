import os
from typing import List
import wx

from .browser import Browser
from .wxcanvas import WxCanvas


class WxApp(wx.App):
    """
    The main application.
    """
    def OnInit(self):
        frame = WxFrame("PS2 memory card browser")
        self.SetTopWindow(frame)
        frame.Show(True)
        return True


class WxFrame(wx.Frame):
    """
    The main application window.
    OpenGL canvas on the left, and the game list box on the right.
    """
    def __init__(self, title: str):
        frame_style = wx.DEFAULT_FRAME_STYLE & ~(wx.RESIZE_BORDER | wx.MAXIMIZE_BOX)
        wx.Frame.__init__(self, None, -1, title, style=frame_style)
        self.browser = None
        self.mc_path = None
        self.selected_game = None
        self.icon_sys, self.icons = None, None
        self.panel = WxPanel(self)
        self.canvas = WxCanvas(self)
        self.statusbar = self.CreateStatusBar()
        self.games = list()
        self.on_init()

    def on_init(self):
        self.setup_menu()
        self.setup_layout()

    def setup_menu(self):
        menubar = wx.MenuBar()
        menu = wx.Menu()
        menubar.Append(menu, "&File")
        menu.Append(wx.ID_OPEN)
        menu.Append(wx.ID_EXIT)
        self.SetMenuBar(menubar)
        self.Bind(wx.EVT_MENU, self.on_open_file, id=wx.ID_OPEN)
        self.Bind(wx.EVT_MENU, self.on_exit, id=wx.ID_EXIT)
        self.Bind(wx.EVT_CLOSE, self.on_exit)

    def setup_layout(self):
        sizer = wx.BoxSizer(wx.HORIZONTAL)
        sizer.Add(self.canvas)
        sizer.Add(self.panel)
        self.SetSizerAndFit(sizer)

    def on_open_file(self, evt: wx.Event):
        """
        Open a file dialog to select a PS2 memory card file.
        """
        file_dialog = wx.FileDialog(
            self, "Open", "", "", "PS2 Memory Card Files (*.ps2)|*.ps2", wx.FD_OPEN | wx.FD_FILE_MUST_EXIST
        )
        if file_dialog.ShowModal() == wx.ID_OK:
            self.mc_path = file_dialog.GetPath()
            file_dialog.Destroy()
            self.refresh_all()

    def on_exit(self, evt: wx.Event):
        if self.browser is not None:
            self.browser.destroy()
        self.canvas.destroy()
        self.Destroy()

    def refresh_all(self):
        """
        Refresh the canvas and game list when a new memory card image is selected.
        """
        if self.browser is not None:
            self.browser.destroy()
        self.browser = Browser(self.mc_path)
        root_dirs = self.browser.list_root_dir()
        self.games = [x.name for x in root_dirs]
        self.panel.update(self.games)
        self.update_selected_game(self.games[0])

    def update_selected_game(self, game: str):
        """
        Update the canvas when a game is selected.

        Parameters:
            game (str):  The selected game title.
        """
        self.selected_game = game
        self.icon_sys, self.icons = self.browser.get_icon(game)
        self.statusbar.SetStatusText(
            f"{self.icon_sys.subtitle[0]} {self.icon_sys.subtitle[1]}"
        )
        self.canvas.refresh(self.icon_sys, self.icons)

    def export_files(self, game: str, file_path: str):
        try:
            self.browser.export(game, file_path)
            wx.MessageBox(f"File saved successfully at:\n{file_path}", "Success", wx.OK | wx.ICON_INFORMATION)
        except Exception as e:
            wx.MessageBox(f"Failed to save file:\n{str(e)}", "Error", wx.OK | wx.ICON_ERROR)


class WxPanel(wx.Panel):
    """
    The panel containing the game list.
    """
    def __init__(self, parent: wx.Panel):
        wx.Panel.__init__(self, parent)
        self.parent = parent
        self.list_box = wx.ListBox(self, size=(250, 480))
        self.Bind(wx.EVT_LISTBOX, self.on_select, self.list_box)
        # Bind the right-click event
        self.list_box.Bind(wx.EVT_CONTEXT_MENU, self.on_right_click)

    def on_select(self, evt: wx.Event):
        """
        Handle the selection event of the game list box.
        """
        self.parent.update_selected_game(self.list_box.GetStringSelection())

    def update(self, games: List[str]):
        """
        Update the game list box.

        Parameters:
            games (List[str]):  The game titles to be displayed in the list box.
        """
        self.list_box.Clear()
        if games:
            self.list_box.AppendItems(games)
            self.list_box.Select(0)

    def on_right_click(self, event: wx.Event):
        """
        Handle the right-click event to show a popup menu.
        """
        # Create the popup menu
        menu = wx.Menu()

        menu_item1 = menu.Append(wx.ID_ANY, "Export files...")
        # menu_item2 = menu.Append(wx.ID_ANY, "Export psu file...")
        # menu_item3 = menu.Append(wx.ID_ANY, "Action 3")

        # Bind menu item events
        self.Bind(wx.EVT_MENU, self.export_files, menu_item1)
        # self.Bind(wx.EVT_MENU, self.export_psu_file, menu_item2)
        # self.Bind(wx.EVT_MENU, self.on_action_3, menu_item3)

        # Show the popup menu
        self.PopupMenu(menu)
        menu.Destroy()

    def export_files(self, event: wx.Event):
        """
        Handle the 'Save File' action:
        - Prompt the user to select a directory.
        - Create a subdirectory 'folder' within the selected directory.
        - Save a file into the subdirectory.
        - Prompt the user if the subdirectory already exists.
        """
        with wx.DirDialog(
            self,
            "Select Directory to Save File",
            style=wx.DD_DEFAULT_STYLE | wx.DD_DIR_MUST_EXIST,
        ) as dir_dialog:
            if dir_dialog.ShowModal() == wx.ID_OK:
                game = self.list_box.GetStringSelection()
                # Get the directory path selected by the user
                dir_path = dir_dialog.GetPath()
                folder_path = f"{dir_path}/{game}"

                # Check if 'folder' already exists
                if os.path.exists(folder_path):
                    overwrite = wx.MessageBox(
                        f"The folder '{folder_path}' already exists. Do you want to overwrite it?",
                        "Folder Exists",
                        wx.YES_NO | wx.ICON_QUESTION
                    )
                    if overwrite != wx.YES:
                        return  # User chose not to overwrite

                self.parent.export_files(game, dir_path)

    # def export_psu_file(self, event: wx.Event):
    #     """
    #     Handle the 'Save File' action by opening a save file dialog
    #     and writing a sample file to the selected directory.
    #     """
    #     with wx.FileDialog(
    #         self,
    #         "Save File",
    #         wildcard="Text files (*.txt)|*.txt|All files (*.*)|*.*",
    #         style=wx.FD_SAVE | wx.FD_OVERWRITE_PROMPT,
    #     ) as save_dialog:
    #         if save_dialog.ShowModal() == wx.ID_OK:
    #             # Get the file path selected by the user
    #             file_path = save_dialog.GetPath()

    #             try:
    #                 # Write a sample file to the selected path
    #                 with open(file_path, "w") as file:
    #                     file.write("This is a sample file saved from wxPython.")

    #                 wx.MessageBox(f"File saved successfully at:\n{file_path}", "Success", wx.OK | wx.ICON_INFORMATION)
    #             except Exception as e:
    #                 wx.MessageBox(f"Failed to save file:\n{str(e)}", "Error", wx.OK | wx.ICON_ERROR)

    # def on_action_3(self, event: wx.Event):
    #     wx.MessageBox("You selected Action 3!")


def main():
    app = WxApp(False)
    app.MainLoop()


if __name__ == "__main__":
    main()
