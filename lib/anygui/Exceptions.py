#
#   Exceptions.py - GUI exception classes
#

# FIXME: Remove unused exceptions. Clean up code.

class Cancel(Exception):
    """Exception raised when user cancels an operation."""
    pass

class Quit(Exception):
    """Exception raised to exit the main event loop."""
    pass

class Error(StandardError):
    """Common base-class of other error-classes."""
    def __init__(self, obj, mess):
        self.obj = obj
        self.mess = mess

    def __str__(self):
        return "%s: %s" % (self.obj, self.mess)

class InternalError(Error):
    def __str__(self):
        return "%s: Internal error: %s" % (self.obj, self.mess)

class SyncError(Exception): pass

class UnimplementedMethod(Error): # Use NotImplementedError instead
    """The method should have been implemented."""
    def __init__(self, obj, meth_name):
        self.obj = obj
        self.mess = "%s.%s not implemented" % \
                    (obj.__class__.__name__, meth_name)

class ArgumentError(Error):
    def __init__(self, obj, meth_name, arg_name, value):
        self.obj = obj
        self.meth_name = meth_name
        self.arg_name = arg_name
        self.value = value

    def __str__(self):
        return "%s: Invalid value %s for argument %s of method %s", \
               (self.obj, self.value, self.arg_name, self.meth_name)

class SetAttributeError(AttributeError):
    def __init__(self, obj, attr):
        self.obj = obj
        self.attr = attr
    def __str__(self):
        return "Attribute '%s' of %s cannot be set" % (self.attr, self.obj)

class GetAttributeError(AttributeError):
    def __init__(self, obj, attr):
        self.obj = obj
        self.attr = attr
    def __str__(self):
        return "Attribute '%s' of %s cannot be read" % (self.attr, self.obj)
