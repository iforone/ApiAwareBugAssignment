import collections
import math
from pandas import Timestamp
from Profile import Profile, array_to_frequency_list, frequency_to_frequency_list, guess_correct_author_name
import pandas as pd
from base import SECONDS_IN_A_DAY, bug_similarity_threshold, LEARN, TEST
from Analysis import Analysis
from Mapper import Mapper


def write_to_text(file_name, text):
    text_file = open(file_name, 'w')
    text_file.write(text)
    text_file.close()


class Profiler:
    def __init__(self, approach, project, builder):
        self.analysis = Analysis()
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
        # profiles that contribute to an specific components
        self.component_mapper = Mapper()
        # builder for query to projects
        self.builder = builder
        # temporary keep last changes in code between a time frame
        self.temp_changes = None

    def sync_profiles(self, bug, mode):
        self.sync_history(bug, mode)
        self.get_changed_codes(self.previous, bug['report_time'], mode)
        self.sync_activity(bug, mode)
        self.sync_api(bug, mode)

    def get_changed_codes(self, begin, end, mode):
        self.builder.execute("""
            SELECT id, codes_bag_of_words, commit_bag_of_words, used_apis, author, committed_at, commit_hash
            FROM processed_code
            WHERE %s <= committed_at AND committed_at < %s
        """, [str(begin), str(end)])
        self.temp_changes = pd.DataFrame(self.builder.fetchall())
        if len(self.temp_changes) != 0:
            self.temp_changes.columns = self.builder.column_names

    def sync_history(self, new_bug, mode):
        if len(self.previous_bugs) == 0:
            return

        last_bug = self.previous_bugs[len(self.previous_bugs) - 1]
        # final updates for memorizing important values of a bug to be used later
        self.previous_bugs[len(self.previous_bugs) - 1]['bag_of_word_stemmed_split'] = \
            self.previous_bugs[len(self.previous_bugs) - 1]['bag_of_word_stemmed'].split()

        self.previous_bugs[len(self.previous_bugs) - 1]['bag_of_word_stemmed_frequency'] = \
            collections.Counter(self.previous_bugs[len(self.previous_bugs) - 1]['bag_of_word_stemmed_split'])

        self.previous_bugs[len(self.previous_bugs) - 1]['direct_apis'] = {}

        # TODO for now let's just use the words in bug report later it can be codes too
        last_bug_terms = self.previous_bugs[len(self.previous_bugs) - 1]['bag_of_word_stemmed_split']
        last_bug_terms_f = array_to_frequency_list(last_bug_terms, last_bug['report_time'])

        assignees = ''
        if mode == LEARN:
            assignees = last_bug['assignees'].split(',')
        elif mode == TEST:
            assignees = last_bug['chosen'].split(',')

        if 1 < len(assignees):
            exit('❌ API experience track of bugs would not work. you need to consider all assignees')

        for assignee in assignees:
            if assignee in self.profiles:
                self.profiles[assignee].update_history(last_bug_terms_f)
                temp_api_dict = self.profiles[assignee].api.copy()
                self.previous_bugs[len(self.previous_bugs) - 1]['direct_apis'] = temp_api_dict
            else:
                self.profiles[assignee] = Profile(assignee, last_bug_terms_f, {}, {})
            self.component_mapper.update(assignee, last_bug['component'])

    def sync_activity(self, new_bug, mode):
        # each change in a commit is a row but the commit message should be considered only once
        already_considered_hashes = []

        for index, change in self.temp_changes.iterrows():
            # edge case: some users have different name in Eclipse bug board VS in code
            author = guess_correct_author_name(change['author'], self.project)
            # edge case: some codes are provided by another developer yet committed by different user
            # author = self.component_mapper.is_by_different_author(author, change, 'UI')

            tempest = change['codes_bag_of_words'].split(',')

            if change['commit_hash'] not in already_considered_hashes:
                tempest += change['commit_bag_of_words'].split(',')
                already_considered_hashes.append(change['commit_hash'])

            code_terms = array_to_frequency_list(tempest, change['committed_at'])

            # adding code terms to profile
            if author in self.profiles:
                self.profiles[author].update_code(code_terms)
            else:
                self.profiles[author] = Profile(author, {}, code_terms, {})
            self.component_mapper.update(author, 'JDT-UI')

    def sync_api(self, new_bug, mode):
        for index, change in self.temp_changes.iterrows():
            author = guess_correct_author_name(change['author'], self.project)
            # author = self.component_mapper.is_by_different_author(author, change, 'UI')

            api_terms = frequency_to_frequency_list(change['used_apis'], change['committed_at'])

            if author in self.profiles:
                self.profiles[author].update_api(api_terms)
            else:
                self.profiles[author] = Profile(author, {}, api_terms, {})
            self.component_mapper.update(author, 'JDT-UI')

    def get_direct_bug_apis(self, bug_terms):
        # direct - use the API experience of assignees for the similar bugs
        # Jaccard is slightly worse but way faster - I want to see how the rest pans out
        similar_bug_ids = self.top_similar_bugs(bug_terms, bug_similarity_threshold)

        list_ = {}
        for index_ in similar_bug_ids:
            apis = self.previous_bugs[index_]['direct_apis']
            for i_, api in apis.items():
                list_.update({i_: api['frequency'] + list_.get(i_, 0)})

        return list_

    def get_indirect_bug_apis(self, commit_hash):
        self.builder.execute("SELECT used_apis FROM processed_code WHERE commit_hash LIKE '" + commit_hash + "%'")

        changes = pd.DataFrame(self.builder.fetchall())

        list_ = {}
        for index, change in changes.iterrows():
            tempest = frequency_to_frequency_list(change[0], None)
            for i_, api in tempest.items():
                list_.update({i_: api['frequency'] + list_.get(i_, 0)})

        return list_

    # returns index of the most similar bugs based on tf-idf similarity
    def top_similar_bugs(self, bug_terms, top):
        local_scores = {}

        for index_, previous_bug in self.previous_bugs.items():
            score = self.jaccard(previous_bug['bag_of_word_stemmed_split'], bug_terms)
            if 0 < score:
                local_scores[index_] = score

        if len(local_scores) == 0:
            return []

        return sorted(local_scores, key=local_scores.get, reverse=True)[:top]

    def rank_developers(self, new_bug):
        result = self.calculate_ranks(new_bug)

        new_bug['chosen'] = result[0][0]
        self.previous = new_bug['report_time']
        self.previous_bugs[len(self.previous_bugs)] = new_bug

        return result

    def calculate_ranks(self, new_bug):
        print('BUG:' + str(new_bug['id']))

        bug_terms = new_bug['bag_of_word_stemmed'].split()
        bug_apis = self.get_direct_bug_apis(bug_terms)

        # TODO: remove 30 most common words from bug reports in VSM

        local_scores = pd.DataFrame(columns=['developer', 'score'])
        history_scores = pd.DataFrame(columns=['developer', 'score'])
        code_scores = pd.DataFrame(columns=['developer', 'score'])
        api_scores = pd.DataFrame(columns=['developer', 'score'])

        for index_, profile in self.profiles.items():
            history_experience = self.time_based_tfidf(
                profile.history,
                profile.h_f,
                bug_terms,
                new_bug['report_time'],
                'history')
            code_experience = self.time_based_tfidf(
                profile.code,
                profile.c_f,
                bug_terms,
                new_bug['report_time'],
                'code')
            api_experience = self.time_based_tfidf(
                profile.api,
                profile.a_f,
                bug_apis,
                new_bug['report_time'],
                'api')

            score = history_experience + code_experience + api_experience

            local_scores.loc[len(local_scores)] = [profile.name, score]

            history_scores.loc[len(history_scores)] = [profile.name, history_experience]
            code_scores.loc[len(code_scores)] = [profile.name, code_experience]
            api_scores.loc[len(api_scores)] = [profile.name, api_experience]

        # # add fallback of the project as Inbox
        # code_scores.loc[len(code_scores)] = [self.project.upper() + '-' + new_bug['component'] + '-' + 'Inbox', 0]
        # api_scores.loc[len(api_scores)] = [self.project.upper() + '-' + new_bug['component'] + '-' + 'Inbox', 0]

        alternate_scores = self.analysis.find_alternative_scores(history_scores, code_scores, api_scores)

        return [
            alternate_scores.sort_values(by='score', ascending=False)['developer'].tolist(),
            local_scores.sort_values(by='score', ascending=False)['developer'].tolist(),
            history_scores.sort_values(by='score', ascending=False),
            code_scores[code_scores['score'] != 0].sort_values(by='score', ascending=False),
            api_scores[api_scores['score'] != 0].sort_values(by='score', ascending=False),
        ]

    def time_based_tfidf_original(self, profile_terms, profile_frequency, bug_terms, bug_time, module):
        expertise = 0

        if type(bug_terms) is dict:
            weights = bug_terms.copy()
            bug_terms = bug_terms.keys()
        else:
            weights = {}

        for bug_term in bug_terms:
            if bug_term in profile_terms:
                temp = profile_terms[bug_term]
                tfidf = temp['frequency'] * math.log10(len(self.profiles) / self.dev_count(bug_term, module))

                difference_in_seconds = (bug_time - temp['date']).total_seconds()
                difference_in_days = difference_in_seconds / SECONDS_IN_A_DAY

                damped_difference_in_days = math.sqrt(difference_in_days)
                if difference_in_days == 0:
                    recency = float('inf')
                else:
                    recency = (1 / self.dev_count(bug_term, module)) + (1 / damped_difference_in_days)

                time_tf_idf = tfidf * recency * weights.get(bug_term, 1)
                expertise += time_tf_idf

        return expertise

    # A time-based approach to automatic bug report assignment
    # Ramin Shokripoura, John Anvik, Zarinah M. Kasiruna, Sima Zamania
    def time_based_tfidf(self, profile_terms, profile_frequency, bug_terms, bug_time, module):
        expertise = 0

        # different: this is only due different data-type for counts of apis the logic is still same as original
        if type(bug_terms) is dict:
            weights = bug_terms.copy()
            bug_terms = bug_terms.keys()
        else:
            weights = {}

        for bug_term in bug_terms:
            if bug_term in profile_terms:
                temp = profile_terms[bug_term]
                # different: this is due to difference in length of documents to normalize the frequencies
                tf = self.calculate_tf(temp['frequency'], profile_frequency)
                tfidf = tf * math.log10(len(self.profiles) / self.dev_count(bug_term, module))

                difference_in_seconds = (bug_time - temp['date']).total_seconds()
                difference_in_days = difference_in_seconds / SECONDS_IN_A_DAY

                # difference_in_days = (bug_time.date() - temp['date'].date()).days
                damped_difference_in_days = math.sqrt(difference_in_days)
                if difference_in_days == 0:
                    recency = float('inf')
                else:
                    recency = (1 / self.dev_count(bug_term, module)) + (1 / damped_difference_in_days)

                time_tf_idf = tfidf * recency * weights.get(bug_term, 1)
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

    # formula of jaccard similarity  -- used anymore for bug similarity
    def jaccard(self, list1, list2):
        intersection = len(list(set(list1).intersection(list2)))
        union = (len(list1) + len(list2)) - intersection
        return float(intersection) / union

    # formula of TF-IDF -- not used anymore for bug similarity
    def tf_idf(self, doc_a_terms, frequencies, bug_terms):
        total = 0
        for bug_term in bug_terms:
            if bug_term in doc_a_terms:
                tfidf = (frequencies[bug_term] / len(doc_a_terms)) * \
                        math.log10(len(self.previous_bugs) / self.bug_count(bug_term))
                total += tfidf
        return total

    def calculate_tf(self, term_frequency, profile_frequency):
        if term_frequency == 0:
            return 0

        return term_frequency / profile_frequency

    def bug_count(self, bug_term):
        counter = 0
        for index_, previous_bug in self.previous_bugs.items():
            if bug_term in previous_bug['bag_of_word_stemmed_split']:
                counter += 1
        return counter
