class Action:
    """This class describe an action of the program."""

    def __init__(self, name, priority, target):
        self.name = name
        self.priority = priority
        self.target = target

    def run(self, context):
        self.target(context=context)
