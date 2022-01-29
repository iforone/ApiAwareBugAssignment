import math
import pytz
from pandas import Timestamp
from Profile import Profile, array_to_frequency_list, frequency_to_frequency_list
import pandas as pd
from base import SECONDS_IN_A_DAY


def write_to_text(file_name, text):
    text_file = open(file_name, 'w')
    text_file.write(text)
    text_file.close()


class Profiler:
    def __init__(self, approach, project, builder):
        print('🍔 running profiler')
        # the approach that is being used for finding the underlying relation between a new bug and previous data
        self.approach = approach
        # name of the project
        self.project = project
        # the beginning of the timeframe in which activities should be considered for update
        self.previous = Timestamp('1999-01-01 00:00:00')
        # array of known bugs that are already processed at any moment
        self.previous_bugs = {}
        # array of known developer profiles at any moment
        self.profiles = {}
        # builder for query to projects
        self.builder = builder
        # temporary keep last changes in code between a time frame
        self.temp_changes = None

    def sync_profiles(self, bug):
        self.sync_history(bug)
        self.get_changed_codes(self.previous, bug['report_time'])
        self.sync_activity(bug)
        self.sync_api(bug)
        # checking authors and exiting history
        # unify all update methods

    def get_changed_codes(self, begin, end):
        self.builder.execute("""
            SELECT id, codes_bag_of_words, commit_bag_of_words, used_apis, author, committed_at
            FROM processed_code
            WHERE %s <= committed_at AND committed_at < %s AND is_extractable = 1
        """, [str(begin), str(end)])
        self.temp_changes = pd.DataFrame(self.builder.fetchall())
        if len(self.temp_changes) != 0:
            self.temp_changes.columns = self.builder.column_names

    def sync_history(self, new_bug):
        if len(self.previous_bugs) == 0:
            return

        last_bug = self.previous_bugs[len(self.previous_bugs) - 1]
        # TODO for now let's just use the words in bug report later it can be codes too
        last_bug_terms = last_bug['bag_of_word_stemmed'].split()
        last_bug_terms_f = array_to_frequency_list(last_bug_terms, last_bug['report_time'])

        # none of the bug reports in JDT have more than one assignee so this is technically one assignee
        assignees = last_bug['assignees'].split(',')
        for assignee in assignees:
            if assignee in self.profiles:
                self.profiles[assignee].update_history(last_bug_terms_f)
            else:
                self.profiles[assignee] = Profile(assignee, last_bug_terms_f, {}, {})

    def sync_activity(self, new_bug):
        for index, change in self.temp_changes.iterrows():
            author = change['author']
            code_terms = array_to_frequency_list(change['codes_bag_of_words'].split(','), change['committed_at'])

            if author in self.profiles:
                self.profiles[author].update_code(code_terms)
            else:
                self.profiles[author] = Profile(author, {}, code_terms, {})

    def sync_api(self, new_bug):
        for index, change in self.temp_changes.iterrows():
            author = change['author']
            api_terms = frequency_to_frequency_list(change['used_apis'], change['committed_at'])

            if author in self.profiles:
                self.profiles[author].update_api(api_terms)
            else:
                self.profiles[author] = Profile(author, {}, api_terms, {})

    def get_bug_apis(self, new_bug):
        if self.approach == 'direct':
            return []
        elif self.approach == 'indirect':
            return []

    def similar_bugs(self, new_bug, top=5):
        similar_bugs = {}
        for index_, previous_bug in self.previous_bugs.items():
            if False:
                pass

        return similar_bugs

    def rank_developers(self, new_bug):
        result = self.calculate_ranks(new_bug).tolist()
        self.previous = new_bug['report_time']
        self.previous_bugs[len(self.previous_bugs)] = new_bug

        return result

    def calculate_ranks(self, new_bug):
        bug_apis = self.get_bug_apis(new_bug)
        bug_terms = new_bug['bag_of_word_stemmed'].split()
        # TODO: remove 30 most common words from bug reports in VSM
        # ask question about this

        local_scores = pd.DataFrame(columns=['developer', 'score'])

        for index_, profile in self.profiles.items():
            fix_experience = self.time_based_tfidf(profile.history, bug_terms, new_bug['report_time'], 'history')
            code_experience = self.time_based_tfidf(profile.code, bug_terms, new_bug['report_time'], 'code')
            api_experience = self.time_based_tfidf(profile.api, bug_apis, new_bug['report_time'], 'api')

            score = fix_experience + code_experience + api_experience
            local_scores.loc[len(local_scores)] = [profile.name, score]

        return local_scores.sort_values(by='score', ascending=False)['developer']

    # A time-based approach to automatic bug report assignment
    # Ramin Shokripoura, John Anvik, Zarinah M. Kasiruna, Sima Zamania
    def time_based_tfidf(self, profile_terms, bug_terms, bug_time, module):
        expertise = 0

        for bug_term in bug_terms:
            if bug_term in profile_terms:
                if self.dev_count(bug_term, module) == 0:
                    continue
                temp = profile_terms[bug_term]
                tfidf = temp['frequency'] * math.log10(len(self.profiles) / self.dev_count(bug_term, module))

                difference_in_seconds = (bug_time - temp['date']).total_seconds()
                difference_in_days = difference_in_seconds / SECONDS_IN_A_DAY
                damped_difference_in_days = math.sqrt(difference_in_days)
                if difference_in_days == 0:
                    # lim 1/ x where x -> 0+ is +infinite
                    recency = float('inf')
                else:
                    recency = (1 / self.dev_count(bug_term, module)) + (1 / damped_difference_in_days)

                time_tf_idf = tfidf * recency
                expertise += time_tf_idf

        return expertise

    def dev_count(self, bug_term, module):
        counter = 0
        for index_, profile in self.profiles.items():
            if module == 'history' and bug_term in profile.history:
                counter += 1
            if module == 'code' and bug_term in profile.code:
                counter += 1
            if module == 'api' and bug_term in profile.api:
                counter += 1

        return counter

