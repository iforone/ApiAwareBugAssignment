import re

import_regex = r'import (?!org.eclipse|\\.).*;'


def get_imports(path, file, fallback):
    if file == '' or file == 'dev/null':
        # if file is deleted return the code changes as fallback
        return re.findall(import_regex, fallback)

    file = open(path + file, mode='r', encoding='utf-8', errors='replace')
    text = file.read()
    file.close()
    return re.findall(import_regex, text)


def get_packages(imports, as_string=False):
    # why -import to import? reason: because sometimes we have code instead of original then it has + or - in the text
    # beginning and it can only be negative because the code is deleted
    imports = [w.replace('-import', 'import').replace('import', '', 1).replace(' static', '', 1).replace(' ', '').replace(';', '') for w in imports]
    if as_string:
        return ','.join(imports)
    return imports
