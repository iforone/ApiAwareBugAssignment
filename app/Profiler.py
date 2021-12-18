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
        self.real_commits = {}
        self.changes_df = {}
        self.approach = approach
        self.project = project
        self.path = './data/input/' + self.project
        self.previous = '1999-01-01 00:00:00'

    def sync_history(self, new_bug):
        pass

    def sync_activity(self, new_bug):
        commits = self.find_commits_between(new_bug['report_time'], self.previous)

        print(new_bug['report_time'])
        print(self.previous)
        for commit in commits.values():
            print(commit['hash'])

        self.previous = new_bug['report_time']  # now the present is the past


        for index, commit in commits.items():
            repo = git.Repo.init(self.path)
            changes = repo.git.show(commit['hash'])
            split_changes = changes.split('\ndiff')[1:]

            for split_change in split_changes:
                split_change_lines = split_change.split('\n')
                indexer = 0  # indexes the line the file name is mentioned

                # skip until the file name
                for split_change_line in split_change_lines:
                    if split_change_line.startswith('---'):
                        break
                    indexer += 1

                if indexer == len(split_change_lines):
                    continue
                split_change_lines[indexer] = (split_change_lines[indexer]).rstrip()
                split_change_lines[indexer + 1] = (split_change_lines[indexer + 1]).rstrip()

                if (split_change_lines[indexer]).endswith('.java') or \
                        (split_change_lines[indexer + 1]).endswith('.java'):
                    # probably all 4 lines are important - split_change_lines[0:4]
                    # probably all of the text is important - split_change_lines[4:]
                    filtered_code = [x for x in split_change_lines[indexer + 2:] if
                                     x.startswith('-') or x.startswith('+')]
                    new = {'file': (split_change_lines[indexer + 1])[5:],
                           'code': '\n'.join(filtered_code),
                           'hash': commit['hash']
                           }
                    self.changes_df[len(self.changes_df)] = new
            # 'dca7e3c8'
            self.real_commits[len(self.real_commits)] = commit

    # sync developers API experience
    def sync_api(self, new_bug):
        # imports = get_imports(self.path + '/org.eclipse.jdt.ui/core refactoring/org/eclipse/jdt/internal/core/refactoring/code/StatementAnalyzer.java')
        # packages = get_packages(imports)
        # https://git.jetbrains.org/?p=idea/community.git;a=blob;f=java/java-analysis-impl/src/com/intellij/codeInspection/unusedImport/ImportsAreUsedVisitor.java;h=ed5bd45d15374c0ef96b149ef74bc79683eb52bf;hb=4954832e922ea51843cbca8ede89421f36bd7366

        for index, change in self.changes_df.items():
            repo = git.Repo.init(self.path)
            repo.git.checkout(change['hash'])
            imports = get_imports(self.path, change['file'], change['code'])
            packages = get_packages(imports, True)
            self.changes_df[index]['packages'] = packages

    # find commits between a specific timeline
    def find_commits_between(self, end, start):
        initial = 'cd ./data/input/' + self.project
        subprocess.run(initial + ';git checkout master', capture_output=True, shell=True)
        command = initial + ';git log --after="' + str(start) + '" --before="' + str(end) + '"'
        process = subprocess.run(command, capture_output=True, shell=True)
        commits_text = process.stdout.decode("utf-8")

        commits_dict = {}
        commits_lines = commits_text.split('\n')
        commits_counts = len(commits_lines) / 6
        for index in range(int(commits_counts)):
            begin = 6 * index
            end = 6 * index + 5
            line = commits_lines[begin:end]
            new_row = {'hash': line[0].replace('commit ', ''),
                       'author': (line[1].replace('Author: ', '').split('<')[0]).rstrip(),
                       'username': line[1].replace('>', '').split('<')[1],
                       # todo: timezone issue can become a problem -- ignore for now
                       'committed_at': str(parser.parse(line[2].replace('Date:   ', ''))),
                       'commit_message': line[4].replace('    ', '')
                       }
            if ''  == new_row['username']:
                continue
            commits_dict[len(commits_dict)] = new_row
        return commits_dict

    # later >>>

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

    def export(self):
        output = pd.DataFrame.from_dict(self.changes_df, orient='index')
        output.to_csv('data/output/' + 'changes.csv')
        exit(1)
