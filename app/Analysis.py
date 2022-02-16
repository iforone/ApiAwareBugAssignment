import pandas as pd


class Analysis:
    def find_alternative_scores(self, history_scores, fix_scores, code_scores, api_scores):
        # top 10 with each measure is chosen
        history_scores = history_scores.sort_values(by='score', ascending=False).head(10)
        fix_scores = fix_scores.sort_values(by='score', ascending=False).head(10)
        code_scores = code_scores.sort_values(by='score', ascending=False).head(10)
        api_scores = api_scores.sort_values(by='score', ascending=False).head(10)

        total_scores = {'history': 0, 'fix': 0, 'code': 0, 'api': 0}
        scores = {}

        for index, row in history_scores.iterrows():
            if str(row['score']) != 'nan':
                total_scores['history'] += row['score']
        for index, row in fix_scores.iterrows():
            if str(row['score']) != 'nan':
                total_scores['fix'] += row['score']
        for index, row in code_scores.iterrows():
            if str(row['score']) != 'nan':
                total_scores['code'] += row['score']
        for index, row in api_scores.iterrows():
            if str(row['score']) != 'nan':
                total_scores['api'] += row['score']

        for index, row in history_scores.iterrows():
            value = row['score']
            developer = row['developer']
            if str(developer) != 'nan':
                if str(value) == 'nan' or total_scores['history'] <= 0:
                    scores[developer] = scores.get(developer, 0) + 0
                else:
                    scores[developer] = scores.get(developer, 0) + (value * 100 / total_scores['history'])

        for index, row in fix_scores.iterrows():
            value = row['score']
            developer = row['developer']
            if str(developer) != 'nan':
                if str(value) == 'nan' or total_scores['fix'] <= 0:
                    scores[developer] = scores.get(developer, 0) + 0
                else:
                    scores[developer] = scores.get(developer, 0) + (value * 100 / total_scores['fix']) / 1.05

        for index, row in code_scores.iterrows():
            value = row['score']
            developer = row['developer']
            if str(developer) != 'nan':
                if str(value) == 'nan' or total_scores['code'] <= 0:
                    scores[developer] = scores.get(developer, 0) + 0
                else:
                    scores[developer] = scores.get(developer, 0) + (value * 100 / total_scores['code'])

        for index, row in api_scores.iterrows():
            value = row['score']
            developer = row['developer']
            if str(developer) != 'nan':
                if str(value) == 'nan' or total_scores['api'] <= 0:
                    scores[developer] = scores.get(developer, 0) + 0
                else:
                    scores[developer] = scores.get(developer, 0) + (value * 100 / total_scores['api'])

        df = pd.DataFrame(columns=['developer', 'score'])
        for i, v in scores.items():
            df.loc[len(df)] = [i, v]

        return df
