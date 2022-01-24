# class CodeScanner a given java code snippet and finds meaningful identifiers in it
import re

from nltk import PorterStemmer
from nltk.corpus import stopwords
from base import input_directory, stop_words_file


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

    def link_commit_message_and_bug(self, all_text_):
        # TODO: check for the bug ids pattern
        pattern_bug_ids = re.compile(r"\[(\d+)\]")
        pattern_bug_ids_mentioning_bug = re.compile(r"\[Bug (\d+)\]")

        id_matches = pattern_bug_ids.findall(all_text_)
        id_matches.extend(pattern_bug_ids_mentioning_bug.findall(all_text_))
        id_matches = set(id_matches)

        # SAVE ALL 3 to database and this part is done
        # another note is adding more patterns based on the data
        # How many developers in total in code?
        # Hoe many developers in bug reports?

        return id_matches

    def analyze_commit_message(self, all_text_):
        return self.analyze_code(all_text_)

    def analyze_code(self, all_text_, with_lexicon_analysis=False):
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
            # identifier decomposition - based on BSBA  - this is basically 1-shingling
            decomposed = camel_case_decomposed_list(token)
            # w-shingling: 2-shingling
            shingles = w_shingles(' '.join(decomposed), 2)
            temp_tokens = {token}
            temp_tokens.update(decomposed)
            temp_tokens.update(shingles)
            temp_tokens = set(temp_tokens)

            all_tokens.extend(temp_tokens)

        # remove java stopwords
        all_tokens = [word for word in all_tokens if word not in self.stop_words]
        # to lowercase everything
        all_tokens = [x.lower() for x in all_tokens]
        # remove english stopwords
        all_tokens = [word for word in all_tokens if word not in self.english_stop_words]

        # TODO: remove punctuations - seems okay 22-Jan-2022 ✅
        stemmer = PorterStemmer()
        all_tokens = [stemmer.stem(word) for word in all_tokens]
        print(all_tokens)
        return all_tokens
