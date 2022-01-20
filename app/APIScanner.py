# this class is used to find, save, scan and parse APIs and API-related tokens
import collections
import os
import re
import json
from nltk.tokenize import word_tokenize
import mysql.connector
import pandas as pd
import subprocess
from mysql.connector import ProgrammingError
from base import main_dir, javase_tree_file, input_directory, output_folder, javase_directory


def run_java(c):
    command = "docker exec -i my_little_alpine bash -c \"" + c + "\""
    process = subprocess.run(command, capture_output=True, shell=True)

    return process.stdout.decode("utf-8")


# find all subclasses for a wildcard import from Java SE based on the docker container running it
def get_subclasses(import_):
    corrected_import_ = import_.replace('.*', '')
    all_classes = read_all_file(main_dir + javase_directory + javase_tree_file)
    result = list(filter(lambda x: x.startswith(corrected_import_), all_classes))

    return result


# find all subclasses for a wildcard import from a jar based on a version we could find for it
def get_jar_subclasses(each_import_, jar):
    result = run_java('cd input/jars && jar -tf ' + jar + ' ' + each_import_.replace('.*', '').replace('.', '/'))

    return result.split('\n')


def r_replace(s, old, new, occurrence):
    li = s.rsplit(old, occurrence)

    return new.join(li)


def split_after(string_, sep, pos):
    string_ = string_.split(sep)
    return sep.join(string_[:pos]), sep.join(string_[pos:])


def read_all_file(filename):
    with open(filename) as f:
        list_ = f.read().splitlines()

    return list_


def clean_imports(project_name, builder_, db_, changes, all_imports):
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


# class APIScanner uses javap to grep the class files from jar or java source code
# it tokenizes classifiers, methods and constants
# if an import uses wildcard it considers all possible classes or subclasses that start with the name
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

        # java keywords are base stopwords
        stopwords_file = open(input_directory + 'java_stopwords.txt')
        self.stop_words = [line.rstrip() for line in stopwords_file.readlines()]
        stopwords_file.close()

    def make_scanner_table(self):
        self.builder.execute('''
            create table IF NOT EXISTS scans
            (
                id int auto_increment,
                importie char(255) null,
                jar char(255) null,
                api char(255) null,
                classifiers longtext null,
                methods longtext null,
                constants longtext null,
                note text null,
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
        change_file_name = output_folder + 'lock_' + project_name + '_scanner.txt'

        if os.path.exists(change_file_name):
            print('✅ Scanner is locked. - import_to_jar and scanner table already exist')
            return

        # get all package in changed files
        builder_.execute("""
            SELECT id, packages, cleaned_packages
            FROM processed_code
            WHERE 1
        """)
        changes = pd.DataFrame(builder_.fetchall())
        all_imports = set()

        if self.with_cleaning == 'yes':
            clean_imports(project_name, builder_, db_, changes, all_imports)
        else:
            for index_, change in changes.iterrows():
                corrected_imports_split = change[2].split(',')
                for s in corrected_imports_split:
                    all_imports.add(s)

        self.process_imports(all_imports)

        # lock the scanner
        file = open(change_file_name, "w")
        file.write('locked')
        file.close()

    def process_imports(self, all_imports):
        for each_import in all_imports:
            # empty import
            if each_import == '':
                continue

            # it is in Java SE or Java EE?
            if each_import.startswith('java'):
                if each_import.endswith('.*'):
                    self.scan_java_class_with_sub_classes(each_import)
                else:
                    self.scan_jar(each_import, None)
                continue

            # it is from a JAR?
            else:
                self.builder.execute('SELECT jar FROM import_to_jar WHERE importie = %s', [each_import])
                result = self.builder.fetchone()
                # result[0] = jar name

                # if the jar is missing -> it should be discovered
                if result is None:
                    self.make_request_for_missing_import(each_import)
                    continue
                # work within the jar file to extract items
                if result[0] == 'none':
                    continue
                elif each_import.endswith('.*'):
                    self.scan_jar_class_with_sub_classes(each_import, result[0])
                else:
                    self.scan_jar(each_import, result[0])

    # how to just get constants -> just run constants and look for Enum or final
    # 1- ✅ Classifier - class or interface or EnumType (like a type of enum)
    # 2- ✅ Methods method names
    # 3- ✅ Enum constants - constants or constant values of an enum
    # functionality: parse the data and save it to database
    # parameters:
    # importie: this is a specific class from a jar or java se source
    # jar: either none or None or a real jar file located in jars/ folder
    # save: boolean to decide if you want to save the result of tokenization to database or return as list
    #       by default we save but for subclasses from a wildcard import it is false
    # force_consider: do you want to force this class to be considered without any further consideration
    #       it is only triggered if machine tries to find the class and fails
    # for each package:
    # classifier -> classes, interfaces, enum types / we can see what else is available
    # interface summary, class summary, enum summary, exception summary, reference summary?
    def scan_jar(self, importie, jar=None, save_=True, force_consider=False):
        relevant_importie = importie
        note = ''

        if jar == 'none' or relevant_importie == '' or relevant_importie is None or relevant_importie.endswith('.'):
            # this is not a real import
            return [set(), set(), set(), '', '']
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
                        'cd input/jars && javap -public ' + relevant_importie.rsplit('.', 1)[0]
                    ).rstrip()
                if all_class_text == '':
                    # this is not a real import
                    if save_:
                        self.builder.execute(
                            'INSERT INTO scans'
                            ' (importie, jar, api, classifiers, methods, constants, full_resolution, note)'
                            ' VALUE (%s, %s, %s, %s, %s, %s, %s, %s)', [importie, jar, '', '', '', '', '', 'CONSIDER']
                        )
                        self.database.commit()
                    print('⚠️ Warning - not in Java SE: ' + relevant_importie + '\n')
                    return [set(), set(), set(), '', 'CONSIDER']
        elif jar == 'JAVA':
            all_class_text = run_java('cd input/jars && javap -public ' + relevant_importie).rstrip()
        elif jar == 'JAVA_PURE':
            # it is part of java but is mis-categorised
            all_class_text = run_java('cd input/jars && javap -public java.' + relevant_importie).rstrip()
        elif jar == 'CONSIDER' or force_consider:
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

                # edge case 4 - if the internal is not found at all
                if internal_as_classifier == '' and internal_as_constant == '' and internal_as_method == '':
                    internal_as_method = ','.join(set([importie, importie.split('.')[-1]]))
                    note = 'INTERNAL-PROBLEMATIC'

                if save_:
                    self.builder.execute(
                        'INSERT INTO scans (importie, jar, api, classifiers, methods, constants, full_resolution, note)'
                        ' VALUE (%s, %s, %s, %s, %s, %s, %s, %s)',
                        [importie, jar, '', internal_as_classifier, internal_as_method, internal_as_constant,
                         all_class_text, note])
                    self.database.commit()
                else:
                    return [set([internal_as_classifier]), set([internal_as_method]), set([internal_as_constant]),
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
            print('⚠️ warning - broken import: cd input/jars && javap -public -cp "' + str(jar) + '" ' + importie)
            return [set(), set(), set(), '', '']

    def scan_jar_class_with_sub_classes(self, each_import_, jar):
        subclasses = get_jar_subclasses(each_import_, jar)

        classifiers = set()
        methods = set()
        constants = set()
        all_texts = set()
        all_notes = set()

        if 0 == len(subclasses):
            # edge case 3: due very limited usage just CONSIDER these imports
            # this class does not exist anymore in its original jar
            # I can't remake the jar due copyright or similar issues
            [temp_cl, temp_m, temp_co, temp_a, temp_n] = self.scan_jar(each_import_, jar, False, True)
            classifiers.update(temp_cl)
            methods.update(temp_m)
            constants.update(temp_co)
            all_texts.add(temp_a)
            all_notes.add(temp_n)
        else:
            for subclass in subclasses:
                # jar classes from jar -tf usually end with the .class:
                if subclass.endswith('.class'):
                    subclass = r_replace(subclass, '.class', '', 1)
                subclass = subclass.replace('/', '.').split('<')[0].split('(')[0].replace('$', '.')

                [temp_cl, temp_m, temp_co, temp_a, temp_n] = self.scan_jar(subclass, jar, False)
                classifiers.update(temp_cl)
                methods.update(temp_m)
                constants.update(temp_co)
                all_texts.add(temp_a)
                all_notes.add(temp_n)

        self.builder.execute(
            'INSERT INTO scans (importie, jar, api, classifiers, methods, constants, full_resolution, note)'
            ' VALUE (%s, %s, %s, %s, %s, %s, %s, %s)',
            [each_import_, jar, '', ','.join(classifiers), ','.join(methods), ','.join(constants), '<========== '
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

        if 0 == len(subclasses):
            # edge case 3: due very limited usage just CONSIDER these imports
            # this is from JAVA EE
            # I can't remake the jar due copyright or similar issues
            [temp_cl, temp_m, temp_co, temp_a, temp_n] = self.scan_jar(each_import_, None, False, True)
            classifiers.update(temp_cl)
            methods.update(temp_m)
            constants.update(temp_co)
            all_texts.add(temp_a)
            all_notes.add(temp_n)
        else:
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

    def make_request_for_missing_import(self, each_import_):
        link = 'https://www.findjar.com/search?query=' + each_import_ + '&more=false'
        download_link = 'https://www.findjar.com/class/' + each_import_.replace('.*', '').replace('.', '/') + '.html'
        self.builder.execute('INSERT INTO import_to_jar (importie, link, download_link) VALUE (%s, %s, %s)',
                             [each_import_, link, download_link])
        self.database.commit()
        print('⚠️ Warning - jar missing: source code is using a package we could not track because Jar is not found!')

        return

    # set API level (api) for each package in scans table when it is empty
    def update_apis(self):
        self.builder.execute(""" SELECT id, importie FROM scans WHERE api = '' """)
        scans = pd.DataFrame(self.builder.fetchall())

        for index_, scan in scans.iterrows():
            id_ = scan[0]  # 0 = id
            import_ = scan[1]  # 1 : importie

            if import_.startswith('util'):
                import_ = 'java.' + import_

            if import_.startswith('java') or import_.startswith('junit') or import_.startswith('sun'):
                api = split_after(import_, '.', 2)[0]
            else:
                api = split_after(import_, '.', 3)[0]

            self.builder.execute("""update scans set api = %s WHERE id = %s """, [api, str(id_)])
            self.database.commit()

    # check each row of the processed_code in the selected project for the usage of tokens related to any API
    def mark_api_usage_in_code(self, project_name, builder_, db_):
        change_file_name = output_folder + 'lock_' + project_name + '_api.txt'
        if os.path.exists(change_file_name):
            print('✅ api usage is locked. - used_apis already labeled')
            return

        builder_.execute("""
            SELECT id, codes, cleaned_packages, used_apis
            FROM   processed_code
            WHERE  cleaned_packages != '' and is_extractable = 1  and id != 122458
        """)
        changes = pd.DataFrame(builder_.fetchall())
        # 0 - id
        # 1 - codes
        # 2 - cleaned_packages
        # 3 - used_apis - this is empty initially since we are calculating it
        # 4 - api_usage_details - exactly what is matched - this is empty initially since we are calculating it
        for index_, change in changes.iterrows():
            id_ = change[0]
            codes = change[1]
            imports = change[2].split(',')

            tokens = re.findall(r"[\w']+", codes)  # tokens = word_tokenize(codes)
            filtered_words = [word for word in tokens if word not in self.stop_words]
            filtered_words_collection = collections.Counter(filtered_words)

            api_usage_counts = {}  # count of each api token
            # this can be a float number when a token is shared between multiple APIs
            # reservie : is the key we use for apis with CONSIDER anyways note
            apis = {}  # all true apis not imports but due imports
            all_tokens = []  # all tokens are used for duplicate suppression

            # prepare:
            for importie in imports:
                self.builder.execute('''
                    SELECT api, CONCAT(classifiers, ',',  methods, ',', constants, ','), jar, note 
                    FROM scans 
                    WHERE importie = %s''', [importie])

                result = self.builder.fetchone()
                if result is None:
                    continue
                # make a row for each IMPORTIE
                apis[importie] = {
                    'name': result[0],
                    'jar': result[2],
                    'note': (result[2] == 'CONSIDER' or (result[3] is not None and 'CONSIDER' in result[3])),
                    'all_api_tokens': set([word for word in result[1].split(',') if word not in ['', None, ' ']]),

                }

                # make a count row for each API
                if apis[importie]['name'] not in api_usage_counts:
                    api_usage_counts[apis[importie]['name']] = {}

                # add all elements of API to a full list to count and suppress repeated elements
                all_tokens.extend(apis[importie]['all_api_tokens'])

            # count all tokens between imports
            all_tokens_collection = collections.Counter(all_tokens)

            # process:
            for importie in imports:
                if importie not in apis:
                    continue

                api_name = apis[importie]['name']
                all_api_tokens = apis[importie]['all_api_tokens']
                if apis[importie]['note']:
                    api_usage_counts[api_name].update({
                        'reservie': 1 + api_usage_counts[api_name].get('reservie', 0)
                    })

                for api_token in all_api_tokens:
                    if api_token in filtered_words:
                        api_usage_counts[api_name].update({
                            api_token: (filtered_words_collection[api_token] / all_tokens_collection[api_token]) + api_usage_counts[api_name].get(api_token, 0)
                        })

            api_true_counts = []
            for key in api_usage_counts.keys():
                temp_usage_count = round(sum(api_usage_counts[key].values()), 4)
                if 0 == temp_usage_count:
                    continue
                api_true_counts.append(str(key) + ':' + str(temp_usage_count))

            # save to database:
            api_true_counts_string = ','.join(api_true_counts)
            api_usage_details_string = json.dumps(api_usage_counts)
            builder_.execute("""update processed_code set used_apis = %s, api_usage_details = %s WHERE id = %s """,
                             [api_true_counts_string, api_usage_details_string, id_])
            db_.commit()

        pass
        # lock the scanner
        file = open(change_file_name, "w")
        file.write('locked')
        file.close()

    def count_used_apis(self, builder_):
        builder_.execute("""
                    SELECT
                    used_apis
                    FROM
                    processed_code
                    WHERE
                    used_apis != '' and used_apis is not null
                """)
        changes = pd.DataFrame(builder_.fetchall())

        all_imports = {}
        for index_, change in changes.iterrows():
            each_imports = change[0].split(',')
            for each_import in each_imports:
                n = each_import.split(':')[0]
                c = each_import.split(':')[1]
                all_imports[n] = float(c) + all_imports.get(n, 0)
        print(all_imports)
