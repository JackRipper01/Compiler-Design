class EXPRESSION:

    def check(self):
        pass

    def infer_type(self):
        pass

    def eval(self):
        pass

class PROGRAM(EXPRESSION):
    def __init__(self, exps):
        self.exp_list=exps