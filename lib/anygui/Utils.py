'Anygui utilities.'

# To be phased out with the place() method
def flatten(seq):
    '''Flatten a sequence. If seq is not a sequence, return [seq].
    If seq is empty, return [].'''
    try:
        if len(seq) > 0:
            seq[0]
    except:
        return [seq]
    result = []
    for item in seq:
        result += flatten(item)
    return result


class Bunch:
    def __init__(self, **kwds):
        self.__dict__.update(kwds)

class Options(Bunch): pass
