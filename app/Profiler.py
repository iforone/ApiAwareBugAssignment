from Profile import Profile
import numpy as np
import subprocess
import pandas as pd
from dateutil import parser
import git

class Profiler:
    def __init__(self, approach, project):
        self.approach = approach
        self.project = project
        self.previous = '1999-01-01 00:00:00'

    def sync_history(self, new_bug):
        pass

    def sync_activity(self, new_bug):
        commits = self.find_commits_between(new_bug['report_time'], self.previous)
        real_commits = commits[commits['username'] != '']

        for index, commit in real_commits.iterrows():
            repo = git.Repo.init('./data/input/' + self.project)
            changes = repo.git.show(commit['hash'])
            split_changes = changes.split('\ndiff')[1:]
            changes_df = pd.DataFrame()

            for split_change in split_changes:
                split_change_lines = split_change.split('\n')
                split_change_lines[2] = (split_change_lines[2]).rstrip()
                split_change_lines[3] = (split_change_lines[3]).rstrip()
                if (split_change_lines[2]).endswith('.java') or (split_change_lines[3]).endswith('.java'):
                    # probably all 4 lines are important - split_change_lines[0:4]
                    # probably all of the text is important - split_change_lines[4:]
                    filtered_code = [x for x in split_change_lines[4:] if x.startswith('-') or x.startswith('+')]
                    new = {'file': (split_change_lines[2])[5:], 'code': '\n'.join(filtered_code)}
                    changes_df = changes_df.append(new, ignore_index=True)

            # 'dca7e3c8'
            #changes_df.to_csv('x.csv')
            exit()
            # for api -> return the full original file
            repo.git.checkout(commit['hash'])
            #https://git.jetbrains.org/?p=idea/community.git;a=blob;f=java/java-analysis-impl/src/com/intellij/codeInspection/unusedImport/ImportsAreUsedVisitor.java;h=ed5bd45d15374c0ef96b149ef74bc79683eb52bf;hb=4954832e922ea51843cbca8ede89421f36bd7366
            print(changes)
            exit(1)

    # sync developers API experience
    def sync_api(self, new_bug):
        pass

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
