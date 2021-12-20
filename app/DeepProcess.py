import numpy as np
import subprocess
import pandas as pd
from dateutil import parser
import git
from dateutil.parser import ParserError
from Extractor import get_imports, get_packages


class DeepProcessor:
    def __init__(self, project, builder, database):
        self.last_changes = {}
        self.project = project
        self.path = './data/input/' + self.project
        self.previous = '1999-01-01 00:00:00'
        self.builder = builder
        self.database = database

    def update(self, new_bug):
        self.extract_commits(new_bug)
        self.extract_apis(new_bug)
        self.memorize(new_bug)

    def extract_commits(self, new_bug):
        commits = self.find_commits_between(new_bug['report_time'], self.previous)

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
                           'code': ('\n'.join(filtered_code)).replace('"', '""'),
                           # mix with the commit information
                           'hash': commit['hash'],
                           'author': commit['author'],
                           'username': commit['username'],
                           'committed_at': commit['committed_at'],
                           'commit_message': (commit['commit_message']).replace('"', '""')
                           }
                    self.last_changes[len(self.last_changes)] = new
            break

    # sync developers API experience
    def extract_apis(self, new_bug):
        for index, change in self.last_changes.items():
            repo = git.Repo.init(self.path)
            repo.git.checkout(change['hash'])
            imports = get_imports(self.path, change['file'], change['code'])
            packages = get_packages(imports, True)
            self.last_changes[index]['packages'] = packages

    # find commits between a specific timeline
    def find_commits_between(self, end_, start_):
        initial = 'cd ./data/input/' + self.project
        subprocess.run(initial + ';git checkout master', capture_output=True, shell=True)
        command = initial + ';git log --after="' + str(start_) + '" --before="' + str(end_) + '"'
        process = subprocess.run(command, capture_output=True, shell=True)
        commits_text = process.stdout.decode("utf-8")
        commits_dict = {}
        commits_lines = commits_text.split('\ncommit')

        for commit in commits_lines:
            if '' == commit:
                continue

            new_row = {}
            line = commit.split('\n')

            try:
                hash_ = (line[0]).replace('commit ', '').lstrip().rstrip()
                author = (line[1].replace('Author: ', '').split('<')[0]).rstrip()
                try:
                    username = line[1].replace('>', '').split('<')[1]
                except IndexError:
                    username = author

                new_row = {'hash': hash_,
                           'author': author,
                           'username': username,
                           # todo: timezone issue can become a problem -- ignore for now
                           'committed_at': str(parser.parse(line[2].replace('Date:   ', ''))),
                           'commit_message': (' '.join(line[4:])).lstrip().rstrip()
                           }
            except ParserError as error:
                print(str(error))
                print(start_)
                print(end_)
                file1 = open("errors.txt", "w")
                file1.write(commits_text)
                file1.close()
                exit(-1)
            except IndexError as error:
                print('index error')
                print(str(error))
                print(start_)
                print(end_)
                file1 = open("errors.txt", "w")
                file1.write(commits_text)
                file1.close()
                exit(-1)

            if '' == new_row['username']:
                continue
            commits_dict[len(commits_dict)] = new_row
        return commits_dict

    def memorize(self, new_bug):
        subprocess.run('cd ./data/input/' + self.project + ';git checkout master', capture_output=True, shell=True)
        if 0 != len(self.last_changes):
            a = ','.join(['file_name', 'codes', 'commit_hash', 'author', 'username', 'committed_at', 'commit_message', 'packages'])
            b = ''
            for last_change in self.last_changes.values():
                b += '(' + ','.join(f'"{w}"' for w in last_change.values()) + '),'
            b = b[:-1]
            query = "Insert IGNORE Into processed_code (%s) Values %s" % (a, b)
            print(query)
            self.builder.execute(query)
            self.database.commit()
        self.last_changes = {}
        self.previous = new_bug['report_time']  # now the present is the past
