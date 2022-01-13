# this class is used to find, save, scan and parse APIs and API-related tokens
import mysql.connector
import pandas as pd
import subprocess

from mysql.connector import ProgrammingError

main_dir = './'
input_directory = 'data/input/'
javase_directory = input_directory + 'javase/'
javaee_directory = input_directory + 'javaee/'
javase_tree_file = 'javase.txt'
javaee_tree_file = 'javaee.txt'


def run_java(c):
    command = "docker exec -i my_little_alpine bash -c \"" + c + "\""
    process = subprocess.run(command, capture_output=True, shell=True)

    return process.stdout.decode("utf-8")


def get_subclasses(import_):
    print('subclasses of: ' + import_ + ' in Java')
    corrected_import_ = import_.replace('.*', '')
    # JAVA SE:
    all_classes = read_all_file(main_dir + javase_directory + javase_tree_file)
    result = filter(lambda x: x.startswith(corrected_import_), all_classes)

    return list(result)


def get_jar_subclasses(each_import_, jar):
    print('subclasses of: ' + each_import_ + ' in ' + jar)
    result = run_java('cd input/jars && jar -tf ' + jar + ' ' + each_import_.replace('/'))

    return result.split('\n')


def r_replace(s, old, new, occurrence):
    li = s.rsplit(old, occurrence)

    return new.join(li)


def read_all_file(filename):
    with open(filename) as f:
        list_ = f.read().splitlines()

    return list_


class APIScanner:
    def __init__(self, with_cleaning):
        # connect to api db
        self.database = mysql.connector.connect(
            host='localhost',
            port='32000',
            user='root',
            password='root',
            database='all_apis'
        )
        self.builder = self.database.cursor()
        # make the table for import-to-jar-mapping
        self.make_api_table()
        self.make_scanner_table()
        self.with_cleaning = with_cleaning

    def make_scanner_table(self):
        self.builder.execute('''
            create table IF NOT EXISTS scans
            (
                id int auto_increment,
                importie char(255) null,
                jar char(255) null,
                api char(255) null,
                classifiers text null,
                methods text null,
                constants text null,
                note char(255) null,
                full_resolution longtext null,
                constraint scans_pk
                    primary key (id)
            );
        ''')

    def make_api_table(self):
        self.builder.execute('''
            create table IF NOT EXISTS import_to_jar
            (
                id int auto_increment,
                importie char(255) null,
                jar char(255) null,
                link text null,
                download_link text null,
                constraint import_to_jar_pk
                    primary key (id)
            );
        ''')

        try:
            self.builder.execute('''
            create index import_to_jar_importie_jar_index on import_to_jar (importie, jar);
            ''')
        except ProgrammingError:
            pass

    def clean_and_process_imports(self, project_name, builder_, db_):
        # get all package in changed files
        builder_.execute("""
            SELECT id, packages, cleaned_packages
            FROM processed_code
            WHERE 1
        """)
        changes = pd.DataFrame(builder_.fetchall())
        all_imports = set()

        if self.with_cleaning == 'yes':
            for index_, change in changes.iterrows():
                all_local_imports = set()
                # change[0] === id
                # change[1] === packages
                # change[2] === cleaned_packages
                # strangely, some of the imports required further cleanup
                temp_imports = change[1].replace('"', '').replace(')', '').replace('(', '').replace('\\n', '').split(
                    ',')
                for temp_import in temp_imports:
                    if temp_import == '':
                        continue
                    if temp_import.startswith('.'):
                        continue
                    if '.' not in temp_import:
                        continue
                    corrected = \
                        temp_import.split('//', 1)[0].split('/*', 1)[0].split('packagepclass', 1)[0].split('classTest',
                                                                                                           1)[
                            0].split('publicclass', 1)[0].split('+class', 1)[0].split('{', 1)[0].split('+', 1)[0]
                    corrected_imports = corrected.replace('import', '\n').replace('\\r+', '\n')
                    corrected_imports_split = corrected_imports.split('\n')

                    for s in corrected_imports_split:
                        s = s.lstrip().rstrip().split('\\r', 1)[0]
                        if s.startswith('org.eclipse.' + project_name) or s == '':
                            continue
                        all_imports.add(s)
                        all_local_imports.add(s)

                cleaned_packages = ','.join(all_local_imports)
                builder_.execute("""update processed_code set cleaned_packages = %s WHERE id = %s """,
                                 [cleaned_packages, change[0]])
                db_.commit()

        else:
            for index_, change in changes.iterrows():
                corrected_imports_split = change[2].split(',')
                for s in corrected_imports_split:
                    all_imports.add(s)

        self.process_imports(all_imports)

    def process_imports(self, all_imports):
        for each_import in all_imports:
            if each_import == '':
                continue
            # it is in Java SE or Java EE
            if each_import.startswith('java'):
                if each_import.endswith('.*'):
                    self.scan_java_class_with_sub_classes(each_import)
                else:
                    self.scan_jar(each_import, None)
                continue
            # it is from a jar
            else:
                self.builder.execute('SELECT jar'
                                     ' FROM import_to_jar WHERE importie = %s', [each_import])
                result = self.builder.fetchone()
                if result is None:
                    link = 'https://www.findjar.com/search?query=' + each_import + '&more=false'
                    download_link = 'https://www.findjar.com/class/' + each_import.replace('.*', '').replace('.',
                                                                                                             '/') + '.html'
                    self.builder.execute('INSERT INTO import_to_jar (importie, link, download_link) VALUE (%s, %s, %s)',
                                         [each_import, link, download_link])
                    self.database.commit()
                    print('⚠️ Warning: source code is using a package we could not track because Jar is not found!')
                    continue
                # work within the jar file to extract items
                self.scan_jar(each_import, result[0])
        exit('OKAY')

    # how to just get constants -> just run constants and look for Enum or final
    # 1- ✅ Classifier - class or interface or EnumType (like a type of enum)
    # 2- ✅ Methods method names
    # 3- ✅ Enum constants - constants or constant values of an enum
    # functionality: parse the data and save it to database
    def scan_jar(self, importie, jar=None, save_=True):
        relevant_importie = importie
        note = ''

        if jar == 'none':
            # this is not a real import
            return
        if jar is None:
            if relevant_importie.endswith('classA'):
                relevant_importie_temp = r_replace(relevant_importie, 'classA', '', 1)
            else:
                relevant_importie_temp = relevant_importie

            all_class_text = run_java('cd input/jars && javap -public ' + relevant_importie_temp).rstrip()
            if all_class_text == '':
                if all_class_text == '':
                    # edge case 1- sometimes it is a sub element imported incorrectly
                    # org.junit.Assert.fail -> is actually a method in org.junit.Assert
                    note = 'INTERNAL'
                    all_class_text = run_java(
                        'cd input/jars && javap -public ' + relevant_importie.rsplit('.', 1)[
                            0]).rstrip()
                if all_class_text == '':
                    # this is not a real import
                    print('⚠️ could not find such class in Java SE and JAVA EE: ' + relevant_importie + '\n')
                    return
        elif jar == 'JAVA':
            all_class_text = run_java('cd input/jars && javap -public ' + relevant_importie).rstrip()
        elif jar == 'JAVA_PURE':
            # it is part of java but is mis-categorised
            all_class_text = run_java('cd input/jars && javap -public java.' + relevant_importie).rstrip()
        elif jar == 'CONSIDER':
            # this is a dummy we consider the api of this anyways due limited special cases
            # such as the api does not exist in a runnable version anymore or it does not impact due few commits
            all_class_text = 'class ' + importie + '\n\n'
        else:
            # totally normal imports:
            # check whether the public is sufficient
            all_class_text = run_java('cd input/jars && javap -public -cp "' + jar + '" ' + relevant_importie).rstrip()
            if all_class_text == '':
                # edge case 1- sometimes it is a sub element imported incorrectly
                # org.junit.Assert.fail -> is actually a method in org.junit.Assert
                note = 'INTERNAL'
                all_class_text = run_java(
                    'cd input/jars && javap -public -cp "' + jar + '" ' + relevant_importie.rsplit('.', 1)[0]).rstrip()
        classifiers = set()
        methods = set()
        constants = set()
        try:
            class_lines = all_class_text.split('\n')

            # some compiles do not start with the message
            index_addition = int(class_lines[0].lstrip().startswith('Compiled from'))

            class_name_not_good = class_lines[0 + index_addition]
            class_index = class_name_not_good.find('class')
            if class_index != -1:
                class_name = class_name_not_good[class_index + 5:].lstrip().split()[0].split('<')[0].rstrip().lstrip()
            else:
                class_name = class_name_not_good[class_name_not_good.find('interface') + 9:].lstrip().split()[
                    0].split('<')[0].rstrip().lstrip()

            classifiers.add(class_name)
            classifiers.add(class_name.replace('$', '.'))
            classifiers.add(class_name.split('.')[-1].replace('$', '.'))
            classifiers.add(class_name.replace('$', '.').split('.')[-1])
            # this is the constructor method - if not already there
            methods.add(class_name.replace('$', '.').split('.')[-1])

            for class_line in class_lines[1 + index_addition:]:
                class_line = class_line.lstrip()
                # is method
                if '(' in class_line:
                    method_ = class_line.split('(')[0].split(' ')[-1]

                    methods.add(method_)
                # is enum
                elif 'final ' + class_name in class_line:
                    enum_type = class_name
                    const_ = class_line.split(' ')[-1][:-1]

                    constants.add(enum_type.split('.')[-1].replace('$', '.') + '.' + const_)
                    constants.add(enum_type.replace('$', '.').split('.')[-1] + '.' + const_)
                    constants.add(const_)
                # is constant
                elif 'final ' in class_line and class_line.endswith(
                        ';') and '{' not in class_line and '}' not in class_line:
                    const_ = class_line.split(' ')[-1][:-1]

                    constants.add(const_)

            if note == 'INTERNAL':
                internal_element = relevant_importie.rsplit('.', 1)[1]

                if internal_element in classifiers:
                    internal_as_classifier = internal_element
                else:
                    internal_as_classifier = ''

                if internal_element in methods:
                    internal_as_method = internal_element
                else:
                    internal_as_method = ''

                if internal_element in constants:
                    internal_as_constant = internal_element
                else:
                    internal_as_constant = ''

                if save_:
                    self.builder.execute(
                        'INSERT INTO scans (importie, jar, api, classifiers, methods, constants, full_resolution, note)'
                        ' VALUE (%s, %s, %s, %s, %s, %s, %s, %s)',
                        [importie, jar, '', internal_as_classifier, internal_as_method, internal_as_constant,
                         all_class_text, note])
                    self.database.commit()
                else:
                    return [set(internal_as_classifier), set(internal_as_method), set(internal_as_constant),
                            all_class_text, note]
            else:
                if save_:
                    self.builder.execute(
                        'INSERT INTO scans (importie, jar, api, classifiers, methods, constants, full_resolution, note)'
                        ' VALUE (%s, %s, %s, %s, %s, %s, %s, %s)',
                        [importie, jar, '', ','.join(classifiers), ','.join(methods), ','.join(constants),
                         all_class_text, note])
                    self.database.commit()
                else:
                    return [classifiers, methods, constants, all_class_text, note]
        except:
            print('this failed unfortunately')
            print('cd input/jars && javap -public -cp "' + str(jar) + '" ' + importie)
        # tokenize
        # check against the code
        # add to used_api
        pass

    def scan_jar_class_with_sub_classes(self, each_import_, jar):
        subclasses = get_jar_subclasses(each_import_, jar)

        classifiers = set()
        methods = set()
        constants = set()
        all_texts = set()
        all_notes = set()

        for subclass in subclasses:
            subclass = subclass.replace('/', '.').split('<')[0].split('(')[0]
            [temp_cl, temp_m, temp_co, temp_a, temp_n] = self.scan_jar(subclass, jar, False)
            classifiers.update(temp_cl)
            methods.update(temp_m)
            constants.update(temp_co)
            all_texts.add(temp_a)
            all_notes.add(temp_n)

        self.builder.execute(
            'INSERT INTO scans (importie, jar, api, classifiers, methods, constants, full_resolution, note)'
            ' VALUE (%s, %s, %s, %s, %s, %s, %s, %s)',
            [each_import_, None, '', ','.join(classifiers), ','.join(methods), ','.join(constants), '<========== '
                                                                                                    'SEPARATOR '
                                                                                                    '==========>'.join(
                all_texts), ','.join(all_notes)])
        self.database.commit()

    def scan_java_class_with_sub_classes(self, each_import_):
        subclasses = get_subclasses(each_import_)

        classifiers = set()
        methods = set()
        constants = set()
        all_texts = set()
        all_notes = set()

        for subclass in subclasses:
            subclass = subclass.split('<')[0].split('(')[0]
            [temp_cl, temp_m, temp_co, temp_a, temp_n] = self.scan_jar(subclass, None, False)
            classifiers.update(temp_cl)
            methods.update(temp_m)
            constants.update(temp_co)
            all_texts.add(temp_a)
            all_notes.add(temp_n)

        self.builder.execute(
            'INSERT INTO scans (importie, jar, api, classifiers, methods, constants, full_resolution, note)'
            ' VALUE (%s, %s, %s, %s, %s, %s, %s, %s)',
            [each_import_, None, '', ','.join(classifiers), ','.join(methods), ','.join(constants), '<========== '
                                                                                                    'SEPARATOR '
                                                                                                    '==========>'.join(
                all_texts), ','.join(all_notes)])
        self.database.commit()
