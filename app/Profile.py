import collections


def array_to_frequency_list(words, date):
    list_ = {}
    counter = collections.Counter(words)
    for i, c in counter.items():
        list_[i] = {'frequency': c, 'date': date}
    return list_


class Profile:
    def __init__(self, name, history, code, api):
        self.name = name
        self.history = history
        self.code = code
        self.api = api

    def update_history(self, list_):
        for i, content in list_.items():
            if i in self.history:
                self.history[i]['frequency'] += content['frequency']
                # update date only if it is more in the future
                if self.history[i]['date'] < content['date']:
                    self.history[i]['date'] = content['date']
            else:
                self.history[i] = content
