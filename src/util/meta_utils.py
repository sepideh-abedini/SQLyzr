import inspect


def get_all_subclasses(cls):
    subclasses = set()
    subclasses.update(cls.__subclasses__())
    subclasses = set(filter(lambda sc: not inspect.isabstract(sc), subclasses))
    for subclass in subclasses.copy():
        subclasses.update(get_all_subclasses(subclass))
    return subclasses
