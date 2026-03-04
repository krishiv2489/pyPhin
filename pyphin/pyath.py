from pathlib import Path    # cross platform lib to work with file paths cleanly
import stat                 # lets us decode raw permission numbers into readable strings like drwxr-xr-x
from datetime import datetime # to convert unix timestamps (raw seconds) into readable dates

class Paths():
    def __init__(self, p) -> None:
        self.currentPath = Path(p) # wraps the starting path in a Path object so we can do operations on it
        
    def readEntries(self, path_to_read: Path | None = None): # can take a path but doesnt need one — defaults to currentPath
        dirs = []
        files = []
        
        read_from_path = path_to_read if path_to_read else self.currentPath # use given path or fall back to current
        
        try:
            entries = list(read_from_path.iterdir())[:1000] # iterdir() gives all items in folder, cap at 1000 to avoid lag on huge dirs
        except PermissionError:
            return ["<Permission Denied>"], [] # OS said no — return a signal string instead of crashing
        except Exception:
             return ["<Error Reading Directory>"], []
        
        for subdir in entries:
            if (subdir.name[0] != "."): # skip hidden files/folders (dotfiles)
                try:
                    if subdir.is_dir():
                        dirs.append(subdir.name)
                    elif subdir.is_file():
                        files.append(subdir.name)
                except PermissionError:
                    continue # skip individual items we cant read instead of stopping everything
                
        dirs.sort()  # alphabetical order
        files.sort()
        return dirs, files
    
    def goInto(self, folderName) -> bool:
        newPath = self.currentPath / folderName # / is pathlib's way of joining paths — cleaner than os.path.join
        if newPath.exists() and newPath.is_dir():
            self.currentPath = newPath # update the current location
            return True
        return False # caller checks this to know if navigation actually happened
    
    def goUp(self):
        self.currentPath = self.currentPath.parent # .parent gives the folder one level above

    def getMetadata(self, name: str) -> dict:
        path = self.currentPath / name
        
        try:
            s = path.stat() # asks the OS for raw file metadata — size, timestamps, permissions etc
        except PermissionError:
            return {"error": "Permission Denied"} # signal errors via dict key so caller doesnt need try/except
        except Exception as e:
            return {"error": str(e)}
        
        # convert raw byte size into human readable — B, KB, MB, GB
        if path.is_dir():
            try:
                # rglob("*") walks every file recursively — can be slow on huge folders, thats why we run this in a worker
                raw_size = sum(f.stat().st_size for f in path.rglob("*") if f.is_file())
            except (PermissionError, OSError):
                raw_size = 0 # if we cant read some files just count what we can
        else:
            raw_size = s.st_size # for files st_size is just the direct size in bytes

        size = raw_size
        for unit in ["B", "KB", "MB", "GB"]:
            if size < 1024:
                size_str = f"{size:.1f} {unit}"
                break
            size /= 1024
        else:
            # the else on a for loop only runs if we never hit break — means size is TB range
            size_str = f"{size:.1f} TB"

        return {
            "name":        path.name,
            "type":        "Directory" if path.is_dir() else "File" if path.is_file() else "Symlink",
            "path":        str(path.resolve()),  # resolve() gives the full absolute path, no relative bits
            "size":        size_str,
            "modified":    datetime.fromtimestamp(s.st_mtime).strftime("%Y-%m-%d  %H:%M:%S"), # st_mtime = last content change, fromtimestamp converts unix seconds to readable date
            "changed":     datetime.fromtimestamp(s.st_ctime).strftime("%Y-%m-%d  %H:%M:%S"), # st_ctime on linux = inode change time (rename, chmod etc) NOT creation time
            "permissions": stat.filemode(s.st_mode), # st_mode is a raw int bitmask, filemode() turns it into drwxr-xr-x style string
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