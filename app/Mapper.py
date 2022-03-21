from Profile import Profile


class Mapper:
    def __init__(self, project):
        self.components = {}
        self.project = project

    # v3: includes all major components
    def get_meaningful_component(self, original):
        if self.project == 'JDT':
            # all major components of the JDT project
            if original == 'JDT-Debug':
                return original
            if original == 'Platform-UI':
                return original
            if original == 'Platform-Search':
                return original
            if original == 'JDT-Core':
                return original
            if original == ' Platform-Text' or original == 'Platform-Text':  # Platform-Text or JDT-Text
                return 'JDT-Text'

            return 'JDT-UI'

        return 'NONE'

    # # V1: problem? does not cover all majors
    # if original == 'Platform-UI':
    #     return original
    # if original == 'Platform-Doc':
    #     return original
    # if original == 'JDT-Core':
    #     return original
    # if original == 'JDT-APT':
    #     return original
    # if original == 'JDT-Text':
    #     return original

    # # V2: problem? is unrealistically detailed
    # if original.startswith('Platform'):
    #     return original
    # if not original.startswith('JDT'):
    #     return original
    # if original == 'JDT-Debug':
    #     return original
    # if original == 'JDT-Core':
    #     return original
    # if original == 'JDT-APT':
    #     return original
    # if original == 'JDT-Text':
    #     return original
    # if original == 'JDT-Doc':
    #     return original
    # return 'JDT-UI'

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
