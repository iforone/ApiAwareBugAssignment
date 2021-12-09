class Profile:
    def __init__(self, report_tokens, code_tokens, apis):
        self.report_tokens = report_tokens
        self.code_tokens = code_tokens
        self.apis = apis

    def update(self, report_tokens, code_tokens, apis):
        return self
