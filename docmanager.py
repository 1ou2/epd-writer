import os

class DocManager:
    def __init__(self,docdir="doc") -> None:
        self.docdir = os.path.join(os.path.dirname(os.path.realpath(__file__)), docdir)
        # current file being edited
        self.fname = ""
        # current file descriptor
        self.fd = None
    
        if not os.path.exists(self.docdir):
            os.makedirs(self.docdir)
        self.files = os.listdir(self.docdir) 

    def getDocs(self):
        # refresh list
        self.files = os.listdir(self.docdir)
        return self.files

    def newFile(self,name):
        self.fname = os.path.join(self.docdir,name)
        self.fd = open(self.fname,"w")

    def getFullPath(self,name):
        return os.path.join(self.docdir,name)
        
    

if __name__ == "__main__":
    dm = DocManager()
    docs = dm.getDocs()
    
    