from Profile import Profile
import numpy as np
import subprocess
import pandas as pd
from dateutil import parser


class Profiler:
    def __init__(self, approach, project):
        self.approach = approach
        self.project = project
        self.previous = '1999-01-01 00:00:00'

    def sync_history(self, new_bug):
        pass

    def sync_activity(self, new_bug):
        pass

    # sync developers API experience
    def sync_api(self, new_bug):
        commits = self.find_commits_between(new_bug['report_time'], self.previous)
        real_commits = commits[commits['username'] != '']

        for index, commit in real_commits.iterrows():
            print(commit)
            exit(1)

    def find_commits_between(self, end, start):
        command = 'cd ./data/input/' + self.project + ';git log --after="' + str(start) + '" --before="' + str(
            end) + '"'

        process = subprocess.run(command, capture_output=True, shell=True)
        commits_text = process.stdout.decode("utf-8")
        commits_df = pd.DataFrame()
        commits_lines = commits_text.split('\n')
        commits_counts = len(commits_lines) / 6
        for index in range(int(commits_counts)):
            begin = 6 * index
            end = 6 * index + 5
            line = commits_lines[begin:end]
            new_row = {'hash': line[0].replace('commit ', ''),
                       'author': line[1].replace('Author: ', '').split('<')[0],
                       'username': line[1].replace('>', '').split('<')[1],
                       # todo: timezone issue can become a problem -- ignor for now
                       'committed_at': str(parser.parse(line[2].replace('Date:   ', ''))),
                       'commit_message': line[4].replace('    ', '')
                       }
            commits_df = commits_df.append(new_row, ignore_index=True)
        return commits_df

    # later >>>

    def match_api(self, new_bug):
        if self.approach == 'direct':
            pass
        elif self.approach == 'indirect':
            pass

    def rank_developers(self):
        # profile = Profile()
        return np.array(['name 1', 'name 2', 'Markus Keller'])
