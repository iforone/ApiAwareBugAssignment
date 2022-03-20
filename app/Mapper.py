from Profile import Profile


class Mapper:
    def __init__(self):
        self.components = {}

    def get_meaningful_component(self, original):
        # for tuning
        # everything that has more than 10
        if original == 'Platform-UI':
            return original
        if original == 'Platform-Doc':
            return original
        if original == 'Platform-Search':
            return original
        if original == 'Platform-SWT':
            return original
        # all JDTs:
        if original == 'JDT-Debug':
            return original
        if original == 'JDT-Core':
            return original
        if original == 'JDT-APT':
            return original
        if original == 'JDT-Text' or original == 'Platform-Text':
            return 'JDT-Text'

        return 'JDT-UI'

    def update_profile(self, assignee, component, module, terms):
        c = self.get_meaningful_component(component)

        if c not in self.components:
            self.components[c] = {}

        profiles = self.components[c]

        if assignee not in profiles:
            self.components[c][assignee] = Profile(assignee, {}, {}, {})

        # update module
        if module == 'history':
            self.components[c][assignee].update_history(terms)
        if module == 'code':
            self.components[c][assignee].update_code(terms)
        if module == 'api':
            self.components[c][assignee].update_api(terms)

    def get_profiles(self, component):
        c = self.get_meaningful_component(component)

        if c not in self.components:
            return {}
        else:
            return self.components[c]
