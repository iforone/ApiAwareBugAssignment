class Analysis:
    def find_alternative_score(self, history_scores, fix_scores, code_scores, api_scores):
        total_scores = {'history': 0, 'fix': 0, 'api': 0, 'code': 0}
        scores = {}

        for index, row in history_scores[:10].iterrows():
            if str(row['score']) != 'nan':
                total_scores['history'] += row['score']
        for index, row in fix_scores[:10].iterrows():
            if str(row['score']) != 'nan':
                total_scores['fix'] += row['score']
        for index, row in code_scores[:10].iterrows():
            if str(row['score']) != 'nan':
                total_scores['api'] += row['score']
        for index, row in api_scores[:10].iterrows():
            if str(row['score']) != 'nan':
                total_scores['code'] += row['score']

        for index, row in history_scores[:10].iterrows():
            value = row['score']
            developer = row['developer']
            if str(developer) != 'nan':
                if str(value) == 'nan' or total_scores['history'] <= 0:
                    scores[developer] = scores.get(developer, 0) + 0
                else:
                    scores[developer] = scores.get(developer, 0) + (value * 100 / total_scores['history'])

        for index, row in fix_scores[:10].iterrows():
            value = row['score']
            developer = row['developer']
            if str(developer) != 'nan':
                if str(value) == 'nan' or total_scores['fix'] <= 0:
                    scores[developer] = scores.get(developer, 0) + 0
                else:
                    scores[developer] = scores.get(developer, 0) + (value * 100 / total_scores['fix']) / 1.05

        for index, row in api_scores[:10].iterrows():
            value = row['score']
            developer = row['developer']
            if str(developer) != 'nan':
                if str(value) == 'nan' or total_scores['api'] <= 0:
                    scores[developer] = scores.get(developer, 0) + 0
                else:
                    scores[developer] = scores.get(developer, 0) + (value * 100 / total_scores['api'])

        for index, row in code_scores[:10].iterrows():
            value = row['score']
            developer = row['developer']
            if str(developer) != 'nan':
                if str(value) == 'nan' or total_scores['code'] <= 0:
                    scores[developer] = scores.get(developer, 0) + 0
                else:
                    scores[developer] = scores.get(developer, 0) + (value * 100 / total_scores['code'])

        sort_items = sorted(scores.items(), key=lambda x: x[1], reverse=True)

        answer = []
        for s in sort_items:
            answer.append(s[0])

        return answer
