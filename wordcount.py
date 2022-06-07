import re

def getContent(fullpath):
    content = []
    try:
        with open(fullpath) as f:
            content = f.readlines()
    except (FileNotFoundError, PermissionError, OSError):
        print("IO Error")

    return content

if __name__ == "__main__":
    content = getContent("test/ponctuation.txt")
    nblines = len(content)
    # word count
    wc = 0
    # caracter count
    cc = 0
    for line in content:
        print(line)
        wc = wc + len(re.findall(r'\w+',line))
        cc = cc + len(re.findall(r'.',line))

    print(f"nb lines {nblines} - nb mots {wc} - nb signes {cc}")


