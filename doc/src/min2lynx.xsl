<?xml version="1.0"?>

<!DOCTYPE stylesheet [
<!ENTITY copy "&#169;">
]>

<xsl:stylesheet
  version="1.0"
  xmlns:xsl="http://www.w3.org/1999/XSL/Transform">

  <xsl:output method="html"/>

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
    <div align="center">
      <xsl:apply-templates/>
    </div>
  </xsl:template>

  <xsl:template match="document/date">
    <div align="center">
      <xsl:apply-templates/>
    </div>
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
    <pre>
      <xsl:text>&#x000A;&#x000A;</xsl:text>
      <xsl:apply-templates/>
    </pre>
  </xsl:template>

  <xsl:template match="codelisting/line">
    <xsl:text>      </xsl:text>
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
      <xsl:apply-templates/>
    </code>
  </xsl:template>

  <xsl:template match="copyright">
    <xsl:text>&copy;</xsl:text>
  </xsl:template>

</xsl:stylesheet>