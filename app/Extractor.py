import re


def get_imports(path, file, fallback):
    if file == '' or file == 'dev/null':
        # if file is deleted return the code changes as fallback
        return fallback

    file = open(path + file, mode='r', encoding='utf-8', errors='replace')
    text = file.read()
    file.close()
    return re.findall(r'import (?!org.eclipse|\\.).*;', text)


def get_packages(imports, as_string=False):
    imports = [w.replace('import', '').replace(' ', '').replace('static', '').replace(';', '') for w in imports]
    if as_string:
        return ','.join(imports)
    return imports
