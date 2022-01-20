# class CodeScanner a given java code snippet and finds meaningful identifiers in it
import re
from nltk.corpus import stopwords
from base import input_directory, stop_words_file


class CodeScanner:
    def __init__(self):
        # java keywords are base stopwords
        stopwords_file = open(input_directory + stop_words_file)
        self.stop_words = [line.rstrip() for line in stopwords_file.readlines()]
        stopwords_file.close()

        self.english_stop_words = set(stopwords.words('english'))

    def analyze_code(self, code_):
        tokens = re.findall(r"[\w']+", code_)  # tokens = word_tokenize(codes)
        print(tokens)
        filtered_words = [word for word in tokens if word not in self.stop_words and word not in self.english_stop_words]
        exit(filtered_words)