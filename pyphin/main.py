'''
Program:- pyPhin
Description:- A file explorer TUI (simple)
Author:- Krishiv Patel 
Date:- 28th feb 2026
GitHub username:- krishiv2489
Repo:- https://github.com/krishiv2489/pyPhin.git     
'''

from textual.app import App, ComposeResult
from textual.widgets import Footer, Static, ListItem, ListView, Label
from textual.containers import Container
from textual import work
from textual.worker import Worker, WorkerState 

from . import pyath as pt # backend — all the filesystem stuff lives here

class FileExplorerApp(App):
    
    CSS_PATH = "file.tcss" # for textual cascading style sheets
    BINDINGS = [("q", "quit",     "Exit"),
                ("s", "enterDir", "Enter"),
                ("w", "goBack",   "Go Back"),
                ("a", "showMeta", "Properties")] # 'a' triggers the metadata view
    
    def compose(self) -> ComposeResult:
        yield Static("  pyPhin", id="title_bar")
        yield Static(f"  {pt.Path.home()}", id="path_bar")  # real content, not empty string
        with Container(id="main"):
            yield ListView(id="left_list")
            yield ListView(id="right_list")
        yield Footer()  # always last — Footer messes with 1fr if yielded mid-compose
        
    def on_mount(self) -> None: # only runs once when the program is fired and never again
        self.core = pt.Paths(pt.Path.home()) # start at home dir — linux only, needs change for windows
        self.current_worker = None # no worker running yet
        
        # grab references so we dont query_one every single time
        self.left_list  = self.query_one("#left_list",  ListView)
        self.right_list = self.query_one("#right_list", ListView)
        self.path_bar   = self.query_one("#path_bar",   Static)
        
        self._update_path_bar() # show the starting path right away
        self.refresh_left_panel()

        if self.left_list.children:
            self.left_list.index = 0 # highlight the first item automatically
            first_item = self.left_list.children[0]
            self.refresh_right_panel(first_item.name) # preview that first item on the right

    # ── Path bar ──────────────────────────────────────────────────────────

    def _update_path_bar(self):
        # just pushes the current path into the top Static widget — called after every navigation
        self.path_bar.update(f"  {self.core.currentPath}")

    # ── Left panel ────────────────────────────────────────────────────────

    def refresh_left_panel(self):
        dirs, files = self.core.readEntries() # get sorted dirs and files from backend
        self.left_list.clear() # wipe whatever was there before
        
        if dirs and files: # both exist — show folders section then files section
            self.left_list.append(ListItem(Label("  📁  Folders"), classes="r"))
            self.left_list.append(ListItem(Static("  ───────────────────"), classes="sep"))
            for d in dirs:
                self.left_list.append(ListItem(Label(f"  {d}"), name=d)) # name= is important — used to identify item later
            self.left_list.append(ListItem(Static(""))) # spacer between sections
            self.left_list.append(ListItem(Label("  📄  Files"), classes="r"))
            self.left_list.append(ListItem(Static("  ───────────────────"), classes="sep"))
            for f in files:
                self.left_list.append(ListItem(Label(f"  {f}"), name=f))
                
        elif not dirs and files: # only files, no folders
            self.left_list.append(ListItem(Label("  📄  Files"), classes="r"))
            self.left_list.append(ListItem(Static("  ───────────────────"), classes="sep"))
            for f in files:
                self.left_list.append(ListItem(Label(f"  {f}"), name=f))
                
        elif dirs and not files and dirs[0] != "<Permission Denied>": # only folders, no files
            self.left_list.append(ListItem(Label("  📁  Folders"), classes="r"))
            self.left_list.append(ListItem(Static("  ───────────────────"), classes="sep"))
            for d in dirs:
                self.left_list.append(ListItem(Label(f"  {d}"), name=d))

        elif not dirs and not files: # literally nothing in here
            self.left_list.append(ListItem(Static("  ── Empty Directory ──"), classes="error"))
            
        elif dirs[0] == "<Permission Denied>": # OS blocked us from reading
            for d in dirs:
                self.left_list.append(ListItem(Label(d), name=d, classes="error"))
            
        else: # something else went wrong
            self.left_list.append(ListItem(Static("  ── Error reading Directory ──"), classes="error"))

    # ── Right panel ───────────────────────────────────────────────────────

    def refresh_right_panel(self, folder_name):
        self.right_list.clear()
        if not folder_name:
            return
        
        previewPath = self.core.currentPath / folder_name # pathlib / operator joins paths cleanly
        
        if previewPath.exists() and previewPath.is_dir():
            if self.current_worker and not self.current_worker.is_finished:
                self.current_worker.cancel() # cancel the old worker if user moved fast
            self.right_list.append(ListItem(Label("  Loading..."))) # placeholder while worker runs
            self.current_worker = self.loadDir(previewPath) # kick off background thread
    
    def update_right_panel(self, dirs, files): # called by worker once its done — same logic as left panel
        self.right_list.clear()

        if dirs and files:
            self.right_list.append(ListItem(Label("  📁  Folders"), classes="r"))
            self.right_list.append(ListItem(Static("  ───────────────────"), classes="sep"))
            for d in dirs:
                self.right_list.append(ListItem(Label(f"  {d}"), name=d))
            self.right_list.append(ListItem(Static("")))
            self.right_list.append(ListItem(Label("  📄  Files"), classes="r"))
            self.right_list.append(ListItem(Static("  ───────────────────"), classes="sep"))
            for f in files:
                self.right_list.append(ListItem(Label(f"  {f}"), name=f))
                
        elif not dirs and files:
            self.right_list.append(ListItem(Label("  📄  Files"), classes="r"))
            self.right_list.append(ListItem(Static("  ───────────────────"), classes="sep"))
            for f in files:
                self.right_list.append(ListItem(Label(f"  {f}"), name=f))
                
        elif dirs and not files and dirs[0] != "<Permission Denied>":
            self.right_list.append(ListItem(Label("  📁  Folders"), classes="r"))
            self.right_list.append(ListItem(Static("  ───────────────────"), classes="sep"))
            for d in dirs:
                self.right_list.append(ListItem(Label(f"  {d}"), name=d))

        elif not dirs and not files:
            self.right_list.append(ListItem(Static("  ── Empty Directory ──"), classes="error"))
            
        elif dirs[0] == "<Permission Denied>":
            for d in dirs:
                self.right_list.append(ListItem(Label(d), name=d, classes="error"))
            
        else:
            self.right_list.append(ListItem(Static("  ── Error reading Directory ──"), classes="error"))

    # ── Events ────────────────────────────────────────────────────────────

    def on_list_view_selected(self, event: ListView.Selected):
        # fires when user presses enter on a left panel item — preview it on the right
        if event.list_view.id == "left_list" and event.item:
            self.refresh_right_panel(event.item.name)

    @work(thread=True) # runs in a background thread so UI doesnt freeze
    def loadDir(self, path):
        return self.core.readEntries(path)

    @work(thread=True) # same — folder size calc can be slow so keep it off the main thread
    def loadMeta(self, name):
        return self.core.getMetadata(name)

    def on_worker_state_changed(self, event: Worker.StateChanged):
        worker = event.worker
        if worker is not self.current_worker:
            return # ignore results from old cancelled workers
        
        if event.state == WorkerState.SUCCESS:
            result = worker.result
            if result is None:
                return

            if isinstance(result, dict): # dict means it came from loadMeta not loadDir
                meta = result
                self.right_list.clear()
                if "error" in meta: # backend signals errors via dict key, not exceptions
                    self.right_list.append(ListItem(Label(f"  Error: {meta['error']}", classes="error")))
                    return
                self.right_list.append(ListItem(Label("  ⚙  Properties"), classes="r"))
                self.right_list.append(ListItem(Static("  ───────────────────")))
                for key, val in meta.items():
                    # :<13 pads the key to 13 chars so values all line up in a column
                    self.right_list.append(ListItem(Label(f"  {key.capitalize():<13}  {val}")))
            else:
                dirs, files = result # tuple means it came from loadDir
                self.update_right_panel(dirs, files)

        elif event.state == WorkerState.ERROR:
            self.right_list.clear()
            self.right_list.append(ListItem(Label("  Error reading directory", classes="error")))

    # ── Actions ───────────────────────────────────────────────────────────

    def action_enterDir(self):
        if not self.left_list.highlighted_child: # nothing selected, do nothing
            return
        index = self.left_list.index
        if index is None:
            return
        item = self.left_list.children[index]
        if self.core.goInto(item.name): # returns True only if path is a valid dir
            self._update_path_bar()
            self.refresh_left_panel()
            if self.left_list.children:
                self.left_list.index = 0
                self.refresh_right_panel(self.left_list.children[0].name)
            else:
                self.right_list.clear()

    def action_goBack(self):
        self.core.goUp()
        self._update_path_bar()
        self.call_later(self._after_navigation) # call_later lets the UI settle before we refresh

    def _after_navigation(self): # split out of action_goBack so call_later can reference it
        self.refresh_left_panel()
        if self.left_list.children:
            self.left_list.index = 0
            self.refresh_right_panel(self.left_list.children[0].name)
        else:
            self.right_list.clear()

    def action_showMeta(self):
        index = self.left_list.index
        if index is None:
            return
        item = self.left_list.children[index]
        if not item.name: # separators and headers have no name, skip them
            return
        self.right_list.clear()
        self.right_list.append(ListItem(Label("  Loading properties...")))
        self.current_worker = self.loadMeta(item.name) # hand off to worker thread


if __name__ == "__main__":
    app = FileExplorerApp()
    app.run()

def main():
    app = FileExplorerApp()
    app.run()