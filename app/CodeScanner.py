# class CodeScanner a given java code snippet and finds meaningful identifiers in it
import os
import re

import pandas as pd
from nltk import PorterStemmer
from nltk.corpus import stopwords
from base import input_directory, stop_words_file, output_folder


def camel_case_decomposed_list(identifier):
    regular_expression_ = re.compile(r'''
        # Find words in a string. Order matters!
        [A-Z]+(?=[A-Z][a-z]) |  # All upper case before a capitalized word
        [A-Z]?[a-z]+ |  # Capitalized words / all lower case
        [A-Z]+ |  # All upper case
        \d+  # Numbers
    ''', re.VERBOSE)
    return regular_expression_.findall(identifier)


def w_shingles(sentence, shingle):
    memory = ''
    shingle_sign = '<======>'
    word_index = 0
    shingles = []
    for word in sentence.split():
        if word_index == 0:
            memory += word
        elif word_index < shingle - 1:
            memory += shingle_sign + word
        else:
            memory += shingle_sign + word
            shingles.append(memory.replace(shingle_sign, ''))
            memory = memory.split(shingle_sign, 1)[1]
        word_index += 1
    return shingles


class CodeScanner:
    def __init__(self):
        # java keywords are base stopwords
        stopwords_file = open(input_directory + stop_words_file)
        self.stop_words = [line.rstrip() for line in stopwords_file.readlines()]
        stopwords_file.close()

        self.english_stop_words = set(stopwords.words('english'))

    # def link_commit_message_and_bug(self, all_text_):
    #     # TODO: check for the bug ids pattern
    #     pattern_bug_ids = re.compile(r"\[(\d+)\]")
    #     pattern_bug_ids_mentioning_bug = re.compile(r"\[Bug (\d+)\]")
    #
    #     id_matches = pattern_bug_ids.findall(all_text_)
    #     id_matches.extend(pattern_bug_ids_mentioning_bug.findall(all_text_))
    #     id_matches = set(id_matches)
    #
    #     # SAVE ALL 3 to database and this part is done
    #     # another note is adding more patterns based on the data
    #     # How many developers in total in code?
    #     # Hoe many developers in bug reports?
    #
    #     return id_matches

    def analyze_commit_message(self, all_text_):
        return self.analyze_code(all_text_, True, True)

    def analyze_code(self, all_text_, with_simple_split=False, with_shingle=False, with_lexicon_analysis=False):
        if with_lexicon_analysis:
            exit('failed!')

        # Tian or [40]: tokenize to words -> stopwords removal -> porter stemming
        # [52] also does stemming similar to many others
        # L2R+ [51]: words -> remove stopwords and punctuations -> lowercase -> porter stemming
        # -> (lemmalize no sense for code) that is the part to ask the professor Lämmel
        # -> lexicon analysis -> that is the part to ask the professor Lämmel
        # 51 suggests finding 30 most common words of bugs and removing them.

        # TODO: maybe change '-' to '_'

        tokens = re.findall(r"[\w']+", all_text_)  # tokens = word_tokenize(codes)
        all_tokens = list()

        for token in tokens:
            # test: token = 'getCompilationUnitXMLDocument312Provider'
            # TODO: maybe change underline to nothing + capital letter in next character
            temp_tokens = {token}

            # identifier decomposition - based on BSBA  - this is basically 1-shingling
            decomposed = camel_case_decomposed_list(token)
            # w-shingling: 2-shingling
            shingles = w_shingles(' '.join(decomposed), 2)

            if with_shingle:
                temp_tokens.update(decomposed)
                temp_tokens.update(shingles)
                temp_tokens = set(temp_tokens)

            all_tokens.extend(temp_tokens)

        if with_simple_split:
            simple_spits = all_text_.split()
            for simple_spit in simple_spits:
                if simple_spit not in all_tokens:
                    all_tokens.append(simple_spit)

        # remove java stopwords
        all_tokens = [word for word in all_tokens if word not in self.stop_words]
        # to lowercase everything
        all_tokens = [x.lower() for x in all_tokens]
        all_tokens = [x.replace(',', '') for x in all_tokens]
        # remove english stopwords
        all_tokens = [word for word in all_tokens if word not in self.english_stop_words]

        # TODO: maybe remove punctuations
        stemmer = PorterStemmer()
        all_tokens = [stemmer.stem(word) for word in all_tokens]

        return all_tokens

    def analyze_codes(self, project_name, builder_, db_):
        change_file_name = output_folder + 'lock_' + project_name + '_code.txt'

        if os.path.exists(change_file_name):
            print('✅ Code Scanner is locked. - already tokenized')
            return

        # get all package in changed files
        builder_.execute("""
            SELECT id, codes, commit_message
            FROM processed_code
            WHERE 1
        """)
        changes = pd.DataFrame(builder_.fetchall())

        for index, change in changes.iterrows():
            # 0 - id
            # 1 - code
            # 2 - commit message
            tokenized_code = self.analyze_code(change[1], False, False)
            tokenized_message = self.analyze_commit_message(change[2])

            builder_.execute("""UPDATE processed_code SET codes_bag_of_words = %s , commit_bag_of_words = %s WHERE id 
            = %s """,
                             [','.join(tokenized_code), ','.join(tokenized_message), change[0]])
            db_.commit()
        # lock the scanner
        file = open(change_file_name, "w")
        file.write('locked')
        file.close()
