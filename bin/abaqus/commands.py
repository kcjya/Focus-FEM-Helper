

class Commands:
    def __init__(self, parent=None):
        super(Commands, self).__init__(parent)
        self.parent = self.parent()

    def hello(self):
        print("hello")


