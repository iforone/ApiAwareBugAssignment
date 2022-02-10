class Mapper:
    def __init__(self):
        self.components = {}

    def update(self, author, component):
        if component not in self.components:
            self.components[component] = set()

        self.components[component].add(author)

    # this set is updated all the time
    # author are only considering contributing authors up to the given moment
    def get_component_authors(self, component):
        if component not in self.components:
            return set()

        return self.components[component]