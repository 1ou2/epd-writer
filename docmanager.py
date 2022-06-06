import os

REFRESH_RATE = 8
CHAR_PER_LINE = 60
NB_HISTORY_LINES = 5
NB_MAX_LINES = 10

class Document:
    def __init__(self,path) -> None:
        self.path = path
        # index used to display lines of the document
        self.startdisplay = 0
        self.fulllen = 0
        self.fitlen = 0
        self.fullcontent = []
        self.displaycontent = []
        self.fitcontent = []
        
        try:
            with open(self.path) as f:
                self.fullcontent = f.readlines()
        except (FileNotFoundError, PermissionError, OSError):
            print("IO Error")
        self.fulllen = len(self.fullcontent)
        self.getfitcontent()
        

    # content : a list of lines - the full file
    # startline : starting line to use for the display
    def getDisplayContent(self,startline):
        displaycontent = self.fullcontent[startline:]
        print(displaycontent)
        # fit lines to max size
        fitcontent = []
        for line in displaycontent:
            if len(line) <= CHAR_PER_LINE:
                fitcontent.append(line)
            else:
                
                for i in range(0,len(line),CHAR_PER_LINE):
                    fitcontent.append(line[i:i+CHAR_PER_LINE])
                if i+CHAR_PER_LINE < len(line):
                    fitcontent.append(line[i+CHAR_PER_LINE:len(line)])
        if len(fitcontent) < NB_MAX_LINES:
            return fitcontent
        else:
            return fitcontent[-NB_HISTORY_LINES:]


class DocManager:
    def __init__(self,docdir="doc"):
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
        
       # content : a list of lines - the full file
    # startline : starting line to use for the display
    def getDisplayContent(self,content,startline):
        displaycontent = content[startline:]
        print(displaycontent)
        # fit lines to max size
        fitcontent = []
        for line in displaycontent:
            if len(line) <= CHAR_PER_LINE:
                fitcontent.append(line)
            else:
                
                for i in range(0,len(line),CHAR_PER_LINE):
                    fitcontent.append(line[i:i+CHAR_PER_LINE])
                if i+CHAR_PER_LINE < len(line):
                    fitcontent.append(line[i+CHAR_PER_LINE:len(line)])
        if len(fitcontent) < NB_MAX_LINES:
            return fitcontent
        else:
            return fitcontent[-NB_HISTORY_LINES:]

    def getDoc(self,path):
        content = []
        try:
            with open(path) as f:
                content = f.readlines()
        except (FileNotFoundError, PermissionError, OSError):
            print("IO Error")

        doc = Document(path)
        return doc        

if __name__ == "__main__":
    dm = DocManager()
    docs = dm.getDocs()
    longdoc = dm.getDoc("test/longtext.txt")
    print(longdoc.fulllen)
    print(longdoc.fitcontent)
    fitc = longdoc.getDisplayContent(3)
    print(fitc)
    


    