from timefunc import timefunc_modulename


class ExampleClass:
    @timefunc_modulename(__name__)
    def __init__(self):
        pass

    @timefunc_modulename(__name__)
    def classfunc(self):
        pass
