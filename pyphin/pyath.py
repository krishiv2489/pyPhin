from pathlib import Path #a cross platform lib to extract and play with paths
import stat
from datetime import datetime
class Paths():
    def __init__(self, p) -> None:
        self.currentPath = Path(p)
        
    def readEntries(self, path_to_read: Path | None = None): #can take paths but does not expect one
        dirs = []
        files = []
        
        read_from_path = path_to_read if path_to_read else self.currentPath
        #permission and error handling
        try:
            entries = list(read_from_path.iterdir())[:1000] #limits the no of entries by 1000 to reduce the disk i/o thus reducing lag
        except PermissionError:
            return ["<Permission Denied>"], []
        except Exception:
             return ["<Error Reading Directory>"], []
        
        for subdir in entries: #checks what the content is file/folder and ...
            if (subdir.name[0]!="."):
                try:
                    if subdir.is_dir():
                        dirs.append(subdir.name)
                    elif subdir.is_file():
                        files.append(subdir.name)
                        
                except PermissionError:
                    continue
                
        dirs.sort()
        files.sort()
        return dirs, files
    
    def goInto(self, folderName) -> bool:
        newPath = self.currentPath / folderName # / is a path functionality to easily merge paths 
        if newPath.exists() and newPath.is_dir():
            self.currentPath = newPath #updates path
            return True
        return False
    
    def goUp(self):
        self.currentPath = self.currentPath.parent
    
    def getMetadata(self, name: str) -> dict:
        path = self.currentPath / name
        
        try:
            s = path.stat()
        except PermissionError:
            return {"error": "Permission Denied"}
        except Exception as e:
            return {"error": str(e)}
        
        size = s.st_size
        for unit in ["B", "KB", "MB", "GB"]: #The else on a for loop is a Python feature that runs only if the loop completed without hitting a break
            if size < 1024:
                size_str = f"{size:.1f} {unit}"
                break
            size /= 1024
        else:
            size_str = f"{size:.1f} TB"

        return {
        "name":     path.name,
        "type":     "Directory" if path.is_dir() else "File" if path.is_file() else "Symlink",
        "path":     str(path.resolve()), #gives absolute path and not relative
        "size":     size_str if path.is_file() else "—",
        "modified": datetime.fromtimestamp(s.st_mtime).strftime("%Y-%m-%d  %H:%M:%S"),
        "changed":  datetime.fromtimestamp(s.st_ctime).strftime("%Y-%m-%d  %H:%M:%S"),
        "permissions": stat.filemode(s.st_mode),
    }
        
        
    #this to test this program in isolation 
    '''def run(self):
        while True:
            dir, list1 = self.readEntries()
            for d in dir:
                print(d)
            usrPath = input("Enter the name of folder (u to go up)(q to quit):- ")
            if usrPath == "q":
                break
            if usrPath == "u":
                self.goUp()
            self.goInto(usrPath)

p1 = Paths('/')
p1.run()'''