import re


def get_imports(file):

    file = open(file, mode='r')
    text = file.read()
    file.close()
    print(text)
    #imports = re.findall(r'import .*(?!org.eclipse.jdt).*;', text)
    #imports = re.findall(r'import .*((?!org.eclipse.jdt).)*.+;', text)
    imports = re.findall(r'import (?!org.eclipse|\\.).*;', text)
    exit(imports)

