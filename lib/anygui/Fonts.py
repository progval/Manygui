
class Font:
    "This class represents font typeface, size, and style."

    legalFaces = 'serif sansserif monospaced'.split()
	
    def __init__(self, size=12, bold=0, italic=0, underline=0, face='serif'):
        # public mode variables
        d = self.__dict__
        d["bold"] = bold
        d["italic"] = italic
        d["underline"] = underline

        # public font size (points)
        d["size"] = size

        # typeface -- a name, interpreted by the Canvas
        assert face is None or face in self.legalFaces
        d["face"] = face
	
    def __cmp__(self, other):
        """Compare two fonts to see if they're the same."""
        if self.face == other.face and self.size == other.size and \
           self.bold == other.bold and self.italic == other.italic \
           and self.underline == other.underline:
            return 0
        else:
            return 1

    def __repr__(self):
        return "Font(%d,%d,%d,%d,%s)" % (self.size, self.bold, self.italic, \
                                         self.underline, repr(self.face))

    def __setattr__(self, name, value):
        raise TypeError, "anygui.Font has read-only attributes"
