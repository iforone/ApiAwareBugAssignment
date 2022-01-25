from time import timezone

import subprocess
import base
import pandas as pd
import pytz
from dateutil import parser
import git
from dateutil.parser import ParserError
from Extractor import get_imports, get_packages


class DeepProcessor:
    def __init__(self, project, builder, database):
        self.continue_ = True
        self.last_changes = {}
        self.project = project
        self.path = './data/input/' + self.project
        self.previous = '1999-01-01 00:00:00'
        self.builder = builder
        self.database = database

    def update(self, new_bug):
        # TODO: raw commits without considering bug is easier to maintain
        self.extract_commits(new_bug)
        self.extract_apis(new_bug)
        self.memorize(new_bug)
        self.continue_ = False

    def extract_commits(self, new_bug):
        commits = self.find_commits_between(new_bug['report_time'], self.previous)

        for index, commit in commits.items():
            repo = git.Repo.init(self.path)
            changes = repo.git.show(commit['hash'])
            split_changes = changes.split('\ndiff')
            # [0] is the commit but we already know it
            split_changes = split_changes[1:]

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

                # probably all 4 lines are important - split_change_lines[0:4]
                # probably all of the text is important - split_change_lines[4:]
                filtered_code = [x for x in split_change_lines[indexer + 2:] if
                                 x.startswith('-') or x.startswith('+')]
                new = {'file': (split_change_lines[indexer + 1])[5:],
                       'code': '\n'.join(filtered_code),
                       # mix with the commit information
                       'hash': commit['hash'],
                       'author': commit['author'],
                       'username': commit['username'],
                       'committed_at': commit['committed_at'],
                       'commit_message': commit['commit_message'],
                       'is_extractable': (split_change_lines[indexer]).endswith('.java') or (
                       split_change_lines[indexer + 1]).endswith('.java')
                       }
                self.last_changes[len(self.last_changes)] = new

    # sync developers API experience
    def extract_apis(self, new_bug):
        for index, change in self.last_changes.items():
            # only changes that are java file are considered for api usage detection\
            # but all commits are storred for developer detection
            if not change['is_extractable']:
                self.last_changes[index]['packages'] = ''
                continue

            repo = git.Repo.init(self.path)
            repo.git.checkout(change['hash'])
            imports = get_imports(self.path, change['file'], change['code'])
            packages = get_packages(imports, True)
            self.last_changes[index]['packages'] = packages

    # find commits between a specific timeline
    def find_commits_between(self, end_, start_):
        initial = 'cd ./data/input/' + self.project
        subprocess.run(initial + ';git checkout master', capture_output=True, shell=True)
        command = initial + ';git log --after="' + str(start_) + '-05:00" --before="' + str(end_) + '-05:00"'
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
                skipped = 0
                for each_line in line[1:]:
                    if each_line.startswith('Author:'):
                        break
                    skipped = skipped + 1
                author = (line[1 + skipped].replace('Author: ', '').split('<')[0]).rstrip()
                try:
                    username = line[1 + skipped].replace('>', '').split('<')[1]
                except IndexError:
                    username = author

                new_row = {'hash': hash_,
                           'author': author,
                           'username': username,
                           # EST  = UTC - 5 hours
                           'committed_at': str(
                               parser.parse(line[2 + skipped].replace('Date:   ', '')).astimezone(pytz.timezone('utc'))
                           ),
                           'commit_message': (' '.join(line[4 + skipped:])).lstrip().rstrip()
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

            # the only commits we do not consider are automatic ones from cvs
            if 'cvs' == new_row['author']:
                continue

            commits_dict[len(commits_dict)] = new_row

        return commits_dict

    def memorize(self, new_bug):
        subprocess.run('cd ./data/input/' + self.project + ';git checkout master', capture_output=True, shell=True)
        if 0 != len(self.last_changes):
            query = '''
            INSERT IGNORE INTO processed_code (file_name, codes, commit_hash, author, username, committed_at, commit_message, packages, is_extractable)
            VALUES
            '''
            list_ = []
            for x, last_change in self.last_changes.items():
                query += '(%s,%s, %s, %s, %s, %s, %s, %s, %s),'
                list_.extend([last_change['file'].encode(encoding='UTF-8', errors='xmlcharrefreplace'),
                              last_change['code'].encode(encoding='UTF-8', errors='xmlcharrefreplace'),
                              last_change['hash'],
                              last_change['author'],
                              last_change['username'],
                              last_change['committed_at'],
                              last_change['commit_message'].encode(encoding='UTF-8', errors='xmlcharrefreplace'),
                              last_change['packages'].encode(encoding='UTF-8', errors='xmlcharrefreplace'),
                              last_change['is_extractable'],
                              ])
            query = query[:-1]
            try:
                self.builder.execute(query, list_)
                self.database.commit()
            except Exception as e:
                print(str(e))
                f = open("query.txt", "a")
                f.write(query)
                f.close()
                print(new_bug)
                f = open("values.txt", "a")
                f.write(','.join(list_))
                f.close()
                exit(-1)
            except:
                print('query failed -- why?')
                f = open("query.txt", "a")
                f.write(query)
                f.close()
                print(new_bug)
                f = open("values.txt", "a")
                f.write(','.join(list_))
                f.close()
                exit(-1)
        self.last_changes = {}
        self.previous = new_bug['report_time']  # now the present is the past
