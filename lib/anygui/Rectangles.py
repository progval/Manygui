class Rectangle:
    """
    A utility mixin with several geometric aliases for rectangular
    objects.

    Subclasses are assumed to support the set method with the same
    signature as Attrib. The only atomic attributes that are assumed
    are x, y, width, and height.

    Assigning to aliases other than width, height, size, and geometry
    will have the effect of moving the Rectangle. Assigning to width,
    height, or size will have the effect of resizing the Rectangle,
    while assigning to geometry may have the effect of both moving and
    resizing the Rectangle.

    Note that the attributes exposed by Rectangles are only aliases
    (implemented with Attrib accessors) and have no 'real existence'
    as Proxy attributes. They will therefore not be the subject of
    in-place modification, as per the Anygui Model-View-Controller
    architecture. In other words, if you assign a mutable value (for
    instance, a list) to a Rectangle's position, subsequently moving
    the Rectangle by other means will not modify the mutable value;
    the Rectangle won't even keep a reference to the original value.
    """
    
    # FIXME: Should perhaps use modify instead of set?
    
    # FIXME: What about naming? Should we use centerX etc? hCenter?
    # hcenter?  What about hmove etc?

    # FIXME: Rewrite mention of MVC

    def setBottom(self, bottom):
        self.set(y=bottom-self.height)

    def getBottom(self):
        return self.y + self.height

    def setBottomLeft(self, bottomLeft):
        x, y = bottomLeft
        y -= self.height
        self.set(x=x, y=y)

    def getBottomLeft(self):
        return self.x, self.getBottom()

    def setBottomRight(self, bottomRight):
        x, y = bottomRight
        x += self.width
        y += self.height
        self.set(x=x, y=y)

    def getBottomRight(self):
        return self.getRight(), self.getBottom()

    def setCenter(self, center):
        x, y = center
        x -= self.width / 2
        y -= self.height / 2
        self.set(x=x, y=y)

    def getCenter(self):
        return self.getCenterX(), self.getCenterY()

    def setCenterX(self, centerX):
        x = centerX - self.width / 2
        self.set(x=x)

    def getCenterX(self):
        return self.x + self.width / 2

    def setCenterY(self, centerY):
        y = centerY - self.height / 2
        self.set(y=y)

    def getCenterY(self):
        return self.y + self.height / 2

    def setGeometry(self, geometry):
        x, y, width, height = geometry
        self.set(x=x, y=y, width=width, height=height)

    def getGeometry(self):
        return self.x, self.y, self.width, self.height

    def setLeft(self, left):
        self.set(x=left)

    def getLeft(self):
        return self.x

    def setMidBottom(self, midBottom):
        x, y = midBottom
        x -= self.width / 2
        y -= self.height
        self.set(x=x, y=y)

    def getMidBottom(self):
        return self.getCenterX(), self.getBottom()

    def setMidLeft(self, midLeft):
        x, y = midLeft
        y -= self.height / 2
        self.set(x=x, y=y)

    def getMidLeft(self):
        return self.x, self.getCenterY()

    def setMidRight(self, midRight):
        x, y = midRight
        x -= self.width
        y -= self.height / 2
        self.set(x=x, y=y)

    def getMidRight(self):
        return self.getRight(), self.getCenterY()

    def setMidTop(self, midTop):
        x, y = midTop
        x -= self.width / 2
        self.set(x=x, y=y)

    def getMidTop(self):
        return self.getCenterX(), self.y

    def setRight(self, right):
        x = right
        x -= self.width
        self.set(x=x)

    def getRight(self):
        return self.x + self.width

    def setSize(self, size):
        w, h = size
        self.set(width=w, height=h)

    def getSize(self):
        return self.width, self.height

    def setTop(self, top):
        self.set(y=top)

    def getTop(self):
        return self.y

    def setTopLeft(self, topLeft):
        x, y = topLeft
        self.set(x=x, y=y)

    def getTopLeft(self):
        return self.x, self.y

    setPosition = setTopLeft

    getPosition = getTopLeft

    def setTopRight(self, topRight):
        x, y = topRight
        x += self.width
        self.set(x=x, y=y)

    def getTopRight(self):
        return self.x + self.width, self.y
