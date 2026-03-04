from pathlib import Path #a cross platform lib to extract and play with paths

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