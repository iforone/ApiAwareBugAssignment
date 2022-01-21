# class CodeScanner a given java code snippet and finds meaningful identifiers in it
import re

from nltk import PorterStemmer
from nltk.corpus import stopwords
from base import input_directory, stop_words_file


class CodeScanner:
    def __init__(self):
        # java keywords are base stopwords
        stopwords_file = open(input_directory + stop_words_file)
        self.stop_words = [line.rstrip() for line in stopwords_file.readlines()]
        stopwords_file.close()

        self.english_stop_words = set(stopwords.words('english'))

    def analyze_code(self, code_, commit_message_):
        # Tian or [40]: tokenize to words -> stopwords removal -> porter stemming
        # [52] also does stemming similar to many others
        # L2R+ [51]: words -> remove stopwords and punctuations -> lowercase -> porter stemming
        # -> (lemmalize no sense for code) that is the part to ask the professor Lämmel
        # 51 suggests finding 30 most common words of bugs and removing them.

        all_text = code_  # + ' ' + commit_message_
        tokens = re.findall(r"[\w']+", all_text)  # tokens = word_tokenize(codes)

        # TODO: remove punctuations

        filtered_words = [word for word in tokens if word not in self.stop_words]
        filtered_words = [word for word in filtered_words if word not in self.english_stop_words]

        # TODO: remove 30 most common words from bug reports
        filtered_words_lowercase = [x.lower() for x in filtered_words]

        stemmer = PorterStemmer()
        stemmed_words = [stemmer.stem(word) for word in filtered_words_lowercase]

        exit(stemmed_words)
