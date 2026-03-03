from textual.app import App, ComposeResult
from textual.widgets import Footer, Static, ListItem, ListView, Label, Rule
from textual.containers import Container
from textual import work, worker
from textual.worker import Worker, WorkerState

from . import pyath as pt

class FileExplorerApp(App):
    
    CSS_PATH = "file.tcss"
    BINDINGS = [("q","quit","Exit"),
                ("s","enterDir","Enter Dir."),
                ("w","goBack","Go Back")]
    
    def compose(self) -> ComposeResult:
        yield Footer()
        with Container(id="main"):
            yield ListView(id="left_list")
            yield ListView(id="right_list")
        
    def on_mount(self) -> None:
        self.theme = "rose-pine"
        self.core = pt.Paths('/')
        
        self.current_worker = None
        
        self.left_list = self.query_one("#left_list", ListView)
        self.right_list = self.query_one("#right_list", ListView)
        self.refresh_left_panel()

        if self.left_list.children:
            self.left_list.index = 0
            
            first_item = self.left_list.children[0]
            folder_name = first_item.name
            self.refresh_right_panel(folder_name)
            
    def refresh_left_panel(self):
        dirs, files = self.core.readEntries()
        self.left_list.clear()
        
        for d in dirs:
            self.left_list.append(ListItem(Label(d), name=d))
    
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
            self.right_list.append(ListItem(Static("----Empty Directory!----")))
            
        elif dirs[0] == "<Permission Denied>":
            for d in dirs:
                self.right_list.append(ListItem(Label(d), name=d))
            
        else:
            self.right_list.append(ListItem(Static("----Error reading Directory!----")))
    
    def on_list_view_selected(self, event: ListView.Selected):
        if event.list_view.id == "left_list" and event.item:
            folderNamePreview = event.item.name
            self.refresh_right_panel(folderNamePreview)
        
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
        pass
    
    def action_goBack(self):
        pass
    

if __name__ == "__main__":
    app = FileExplorerApp()
    app.run()
    
def main():
    app = FileExplorerApp()
    app.run()