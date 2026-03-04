'''
Program:- pyPhin
Description:- A file explorer TUI (simple)
Author:- Krishiv Patel 
Date:- 28th feb 2026
GitHub username:- krishiv2489
Repo:- https://github.com/krishiv2489/pyPhin.git     
'''

from textual.app import App, ComposeResult
from textual.widgets import Footer, Static, ListItem, ListView, Label, Rule
from textual.containers import Container
from textual import work, worker
from textual.worker import Worker, WorkerState 

from . import pyath as pt #to import the functions of the backend

class FileExplorerApp(App):
    
    CSS_PATH = "file.tcss" #for textual cascading style sheets
    BINDINGS = [("q","quit","Exit"),
                ("s","enterDir","Enter Dir."),
                ("w","goBack","Go Back")]
    
    def compose(self) -> ComposeResult: # this is the functions / method that makes the tui happen
        yield Footer()
        with Container(id="main"):
            yield ListView(id="left_list") #use this instead of vertical scroll as this is same but selectable
            yield ListView(id="right_list")
        
    def on_mount(self) -> None: # only runs once when the program is fired and never again
        self.theme = "rose-pine" #sets default tui theme but can be changed by user
        self.core = pt.Paths(pt.Path.home())# for linux only but needs to be changed for windows
        
        self.current_worker = None #sets the worker to none
        
        self.left_list = self.query_one("#left_list", ListView)
        self.right_list = self.query_one("#right_list", ListView)
        self.refresh_left_panel()

        if self.left_list.children:
            self.left_list.index = 0 #sets the the first item in the left list as selected and displays it on right
            
            first_item = self.left_list.children[0] # gets the first item in the list view and extract the name for the folder to be shown
            folder_name = first_item.name
            self.refresh_right_panel(folder_name)
            
    def refresh_left_panel(self):
        dirs, files = self.core.readEntries()
        self.left_list.clear()
        
        if len(dirs) != 0 and len(files) != 0:
            self.left_list.append(ListItem(Label("📁")))
            self.left_list.append(ListItem(Static("---------------")))

            for d in dirs:
                self.left_list.append(ListItem(Label(d), name=d))

            self.left_list.append(ListItem(Static()))
            self.left_list.append(ListItem(Label("📄")))
            self.left_list.append(ListItem(Static("---------------")))

            for f in files:
                self.left_list.append(ListItem(Label(f), name=f))
                
        elif len(dirs) == 0 and len(files) != 0 :
            self.left_list.append(ListItem(Label("📄")))
            self.left_list.append(ListItem(Static("---------------")))

            for f in files:
                self.left_list.append(ListItem(Label(f), name=f))
                
        elif len(files) == 0 and len(dirs) != 0 and dirs[0] != "<Permission Denied>":
            self.left_list.append(ListItem(Label("📁")))
            self.left_list.append(ListItem(Static("---------------")))

            for d in dirs:
                self.left_list.append(ListItem(Label(d), name=d))

        elif len(files) == 0 and len(dirs) == 0:
            self.left_list.append(ListItem(Static("----Empty Directory!----"), classes="error"))
            
        elif dirs[0] == "<Permission Denied>":
            for d in dirs:
                self.left_list.append(ListItem(Label(d), name=d, classes="error"))
            
        else:
            self.left_list.append(ListItem(Static("----Error reading Directory!----"),classes="error"))
    
    def refresh_right_panel(self, folder_name):
        
        self.right_list.clear()
        
        if not folder_name:
            return
        
        previewPath = self.core.currentPath / folder_name
        
        if previewPath.exists() and previewPath.is_dir():
            if self.current_worker and not self.current_worker.is_finished:
                self.current_worker.cancel()

            self.right_list.append(ListItem(Label("Loading...")))
            self.current_worker = self.loadDir(previewPath)
    
    def update_right_panel(self, dirs, files):
        self.right_list.clear()

        if len(dirs) != 0 and len(files) != 0:
            self.right_list.append(ListItem(Label("📁")))
            self.right_list.append(ListItem(Static("---------------")))

            for d in dirs:
                self.right_list.append(ListItem(Label(d), name=d))

            self.right_list.append(ListItem(Static()))
            self.right_list.append(ListItem(Label("📄")))
            self.right_list.append(ListItem(Static("---------------")))

            for f in files:
                self.right_list.append(ListItem(Label(f), name=f))
                
        elif len(dirs) == 0 and len(files) != 0 :
            self.right_list.append(ListItem(Label("📄")))
            self.right_list.append(ListItem(Static("---------------")))

            for f in files:
                self.right_list.append(ListItem(Label(f), name=f))
                
        elif len(files) == 0 and len(dirs) != 0 and dirs[0] != "<Permission Denied>":
            self.right_list.append(ListItem(Label("📁")))
            self.right_list.append(ListItem(Static("---------------")))

            for d in dirs:
                self.right_list.append(ListItem(Label(d), name=d))

        elif len(files) == 0 and len(dirs) == 0:
            self.right_list.append(ListItem(Static("----Empty Directory!----"), classes="error"))
            
        elif dirs[0] == "<Permission Denied>":
            for d in dirs:
                self.right_list.append(ListItem(Label(d), name=d, classes="error"))
            
        else:
            self.right_list.append(ListItem(Static("----Error reading Directory!----"),classes="error"))
    
    def on_list_view_selected(self, event: ListView.Selected):
        if event.list_view.id == "left_list" and event.item:
            folderNamePreview = event.item.name
            self.refresh_right_panel(folderNamePreview)
            return folderNamePreview
        
    @work(thread=True)
    def loadDir(self, path):
        return self.core.readEntries(path)
    
    def on_worker_state_changed(self, event: Worker.StateChanged):
        worker = event.worker
        
        if worker is not self.current_worker:
            return
        
        if event.state == WorkerState.SUCCESS:
            result = worker.result

            if result is None:
                return

            dirs, files = result
            self.update_right_panel(dirs, files)

        elif event.state == WorkerState.ERROR:
            self.right_list.clear()
            self.right_list.append(ListItem(Label("Error reading directory")))
            
    def action_enterDir(self):
        if not self.left_list.highlighted_child: 
            return
        
        index = self.left_list.index
        if index is None:
            return
        
        item = self.left_list.children[index]
        folder_name = item.name
        
        if self.core.goInto(folder_name):
            self.refresh_left_panel()
            
            if self.left_list.children:
                self.left_list.index = 0
                first_item = self.left_list.children[0]
                self.refresh_right_panel(first_item.name)
            else:
                self.right_list.clear()    
                
                
    def action_goBack(self):
        self.core.goUp()
        self.call_later(self._after_navigation)
        
    def _after_navigation(self):
        self.refresh_left_panel()
        
        if self.left_list.children:
            self.left_list.index = 0
            first_item = self.left_list.children[0]
            self.refresh_right_panel(first_item.name)
        else:
            self.right_list.clear()

if __name__ == "__main__":
    app = FileExplorerApp()
    app.run()
    
def main():
    app = FileExplorerApp()
    app.run()