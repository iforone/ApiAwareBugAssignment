import collections
import pandas

from base import jdt_fixable_names


def array_to_frequency_list(words, date):
    list_ = {}
    counter = collections.Counter(words)
    for i, c in counter.items():
        list_[i] = {'frequency': float(c), 'date': date}
    return list_


def frequency_to_frequency_list(word_str_, date):
    if word_str_ is None or word_str_ == '':
        return {}
    if pandas.isnull(word_str_):
        return {}

    list_ = {}
    words = word_str_.split(',')
    for word in words:
        sp = word.split(':')
        list_[sp[0]] = {'frequency': float(sp[1]), 'date': date}

    return list_


# guess the correct name developers
# some of the developer names are in-consistent between commits and assignee name in the bug report
# yet they refer to the same person (probably due them having made / modified account in different timelines or typos)
def guess_correct_author_name(name, project):
    if project == 'jdt':
        if name in jdt_fixable_names.keys():
            return jdt_fixable_names[name]
    if project == 'swt':
        if name in jdt_fixable_names.keys():
            return jdt_fixable_names[name]
    return name


class Profile:
    def __init__(self, name, history, code, api):
        self.name = name

        self.history = history
        self.code = code
        self.api = api

        # total frequencies
        self.h_f = 0
        self.c_f = 0
        self.a_f = 0

        for i, content in self.history.items():
            self.h_f += float(content['frequency'])
        for i, content in self.code.items():
            self.c_f += float(content['frequency'])
        for i, content in self.api.items():
            self.a_f += float(content['frequency'])

    def __getitem__(self, name):
        return getattr(self, name)

    def __setitem__(self, name, value):
        return setattr(self, name, value)

    def __delitem__(self, name):
        return delattr(self, name)

    def __contains__(self, name):
        return hasattr(self, name)

    def update_history(self, list_):
        self.update(list_, 'history')

    def update_code(self, list_):
        self.update(list_, 'code')

    def update_api(self, list_):
        self.update(list_, 'api')

    def update(self, list_, key):
        for i, content in list_.items():
            if i in self[key]:
                self[key][i]['frequency'] += float(content['frequency'])
                # update date only if it is more in the future
                if self[key][i]['date'] < content['date']:
                    self[key][i]['date'] = content['date']
            else:
                self[key][i] = content

            self.update_total_frequencies(content, key)

    def update_total_frequencies(self, content, key):
        if key == 'history':
            self.h_f += float(content['frequency'])
        if key == 'code':
            self.c_f += float(content['frequency'])
        if key == 'api':
            self.a_f += float(content['frequency'])

    def get_max_frequency(self, key):
        list_ = []
        if key == 'history':
            for i, content in self.history.items():
                list_.append(float(content['frequency']))
        if key == 'code':
            for i, content in self.code.items():
                list_.append(float(content['frequency']))
        if key == 'api':
            for i, content in self.api.items():
                list_.append(float(content['frequency']))
        if len(list_) == 0:
            return 0

        return max(list_)
