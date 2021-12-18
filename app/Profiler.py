import csv

from Profile import Profile
import numpy as np
import subprocess
import pandas as pd
from dateutil import parser
import git
from Extractor import get_imports, get_packages


def write_to_text(file_name, text):
    text_file = open(file_name, 'w')
    text_file.write(text)
    text_file.close()


class Profiler:
    def __init__(self, approach, project):
        print('running profiler')
        self.real_commits = {}
        self.last_changes = {}
        self.approach = approach
        self.project = project
        self.path = './data/input/' + self.project
        self.previous = '1999-01-01 00:00:00'
        #self.previous = '2001-10-10 22:53:38'
        self.all_changes = {}

    def sync_history(self, new_bug):
        pass

    def sync_activity(self, new_bug):
        pass

    def sync_api(self, new_bug):
        pass

    def match_api(self, new_bug):
        if self.approach == 'direct':
            pass
        elif self.approach == 'indirect':
            pass

    def rank_developers(self):
        # profile = Profile()
        return np.array(['name 1', 'name 2', 'Markus Keller'])

    def extract_apis(self):
        pass
