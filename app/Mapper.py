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

    def is_by_different_author(self, author, change, component):
        if component != 'UI':
            return author

        commit_message = change['commit_bag_of_words'].split(',')
        if 'review' in commit_message:
            return author

        for potential_author in self.get_component_authors(component):
            parts = potential_author.split()
            for part in parts:
                if part.lower() in commit_message:
                    print(potential_author)
                    return potential_author

        return author
