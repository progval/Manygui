<?xml version="1.0"?>

<!DOCTYPE stylesheet [
<!ENTITY copy "&#169;">
]>

<xsl:stylesheet
  version="1.0"
  xmlns:xsl="http://www.w3.org/1999/XSL/Transform">

  <xsl:output method="html" encoding="iso-8859-1"/>

  <xsl:strip-space elements="*"/>

  <xsl:template match="/">
    <html>
      <xsl:apply-templates/>
    </html>
  </xsl:template>

  <xsl:template match="document">
    <head>
      <title>
	<xsl:value-of select="title"/>
      </title>
      <style>
	<xsl:text>
body                    { color: #000000;
                          background-color: #ffffff;
                          margin: 2.0cm }

a:active                { color: #ff0000; }
a:visited               { color: #551a8b; }
a:link                  { color: #0000bb; }

h1, h2, h3, h4, h5, h6,
.author, .date          { font-family: avantgarde, sans-serif;
                          font-weight: bold; }
h2, h3, h4, h5, h6      { margin-left: -0.75cm; }
<!--
h1                      { font-size: 180% }
h2                      { font-size: 150% }
h3, h4                  { font-size: 120% }
-->
code                    { font-family: monospace }
.verbatim               { color: #00008b }
h1, .author, .date      { text-align: center }
.date                   { padding-bottom: 2cm }
	</xsl:text>
      </style>
    </head>
    <body>
      <!--
      <xsl:text>\frontmatter{</xsl:text>
      <xsl:value-of select="@version"/>
      <xsl:text>}&#x000A;</xsl:text>
      -->
      <xsl:apply-templates/>
    </body>
  </xsl:template>
  
  <xsl:template match="document/title">
    <h1>
      <xsl:apply-templates/>
    </h1>
  </xsl:template>

  <xsl:template match="document/author">
    <p class="author">
      <xsl:apply-templates/>
    </p>
  </xsl:template>

  <xsl:template match="document/date">
    <p class="date">
      <xsl:apply-templates/>
    </p>
  </xsl:template>

  <xsl:template match="document/section/title">
    <h2>
      <xsl:number level="multiple" count="section"/>
      <xsl:text>. </xsl:text>
      <xsl:apply-templates/>
    </h2>
  </xsl:template>
  
  <xsl:template match="document/section/section/title">
    <h3>
      <xsl:number level="multiple" count="section"/>
      <xsl:text> </xsl:text>
      <xsl:apply-templates/>
    </h3>
  </xsl:template>

  <xsl:template match="document/section/section/section/title">
    <h4>
      <xsl:number level="multiple" count="section"/>
      <xsl:text> </xsl:text>
      <xsl:apply-templates/>
    </h4>
  </xsl:template>
  
  <xsl:template match="document/section/section/section/section/title">
    <h5>
      <xsl:number level="multiple" count="section"/>
      <xsl:text> </xsl:text>
      <xsl:apply-templates/>
    </h5>
  </xsl:template>

  <xsl:template match="para">
    <p>
      <xsl:apply-templates/>
    </p>
  </xsl:template>

  <xsl:template match="codelisting">
    <dl><dd><pre class="verbatim"> <!-- lib.css ... -->
      <xsl:text>&#x000A;</xsl:text>
      <xsl:apply-templates/>
    </pre></dd></dl>
  </xsl:template>

  <xsl:template match="codelisting/line">
    <xsl:apply-templates/>
    <xsl:text>&#x000A;</xsl:text>
  </xsl:template>

  <xsl:template match="emphasis">
    <em>
      <xsl:apply-templates/>
    </em>
  </xsl:template>

  <xsl:template match="strong">
    <b>
      <xsl:apply-templates/>
    </b>
  </xsl:template>

  <xsl:template match="name">
    <em>
      <xsl:apply-templates/>
    </em>
  </xsl:template>

  <xsl:template match="code">
    <code>
      <xsl:apply-templates/>
    </code>
  </xsl:template>

  <xsl:template match="url">
    <code>
      <xsl:element name="a">
	<xsl:attribute name="href">
	  <xsl:value-of select="."/>
	</xsl:attribute>
	<xsl:apply-templates/>
      </xsl:element>
    </code>
  </xsl:template>

  <xsl:template match="copyright">
    <xsl:text>&copy;</xsl:text>
  </xsl:template>

</xsl:stylesheet>
