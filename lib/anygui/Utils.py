'Anygui utilities.'

def import_weakref():
    '''Try to import and import weakref. If it is not available,
    provide a dummy implementation.'''
    try:
        import weakref
        return weakref
    except ImportError:
        from warnings import warn
        warn('weakref module not available')
        class weakref:
            class ref:
                def __init__(self,obj):
                    self.obj = obj
                def __call__(self):
                    return self.obj
        return weakref

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
