<?xml version="1.0"?>

<xsl:stylesheet
  version="1.0"
  xmlns:xsl="http://www.w3.org/1999/XSL/Transform">

  <xsl:output method="text" indent="no"/>

  <xsl:strip-space elements="*"/>

  <xsl:template match="/">
    <xsl:text>\documentclass[a4paper]{article}&#x000A;</xsl:text>
    <xsl:text>\usepackage{anygui}&#x000A;</xsl:text>
    <xsl:apply-templates/>
  </xsl:template>

  <xsl:template match="document">
    <xsl:text>\title{</xsl:text>
    <xsl:value-of select="title"/>
    <xsl:text>}&#x000A;</xsl:text>
    
    <xsl:text>\author{</xsl:text>
    <xsl:value-of select="author"/>
    <xsl:text>}&#x000A;</xsl:text>
    
    <xsl:text>\date{</xsl:text>
    <xsl:value-of select="date"/>
    <xsl:text>}&#x000A;</xsl:text>

    <xsl:text>\begin{document}&#x000A;</xsl:text>
    <xsl:text>\frontmatter{</xsl:text>
    <xsl:value-of select="@version"/>
    <xsl:text>}&#x000A;</xsl:text>
    <xsl:apply-templates/>
    <xsl:text>\end{document}</xsl:text>
  </xsl:template>
  
  <xsl:template match="document/title">
    <!-- intentionally empty -->
  </xsl:template>

  <xsl:template match="document/author">
    <!-- intentionally empty -->
  </xsl:template>

  <xsl:template match="document/date">
    <!-- intentionally empty -->
  </xsl:template>

  <xsl:template match="document/section/title">
    <xsl:text>\section{</xsl:text>
    <xsl:apply-templates/>
    <xsl:text>}&#x000A;</xsl:text>
  </xsl:template>

  <xsl:template match="document/section/section/title">
    <xsl:text>\subsection{</xsl:text>
    <xsl:apply-templates/>
    <xsl:text>}&#x000A;</xsl:text>
  </xsl:template>

  <xsl:template match="document/section/section/section/title">
    <xsl:text>\subsubsection{</xsl:text>
    <xsl:apply-templates/>
    <xsl:text>}&#x000A;</xsl:text>
  </xsl:template>
  
  <xsl:template match="document/section/section/section/section/title">
    <xsl:text>\subsubsubsection{</xsl:text>
    <xsl:apply-templates/>
    <xsl:text>}&#x000A;</xsl:text>
  </xsl:template>

  <xsl:template match="para">
    <xsl:text>&#x000A;</xsl:text>
    <xsl:apply-templates/>
    <xsl:text>&#x000A;</xsl:text>
  </xsl:template>

  <xsl:template match="codelisting">
    <xsl:text>\begin{verbatim}</xsl:text>
    <xsl:apply-templates/>
    <xsl:text>\end{verbatim}</xsl:text>
  </xsl:template>

  <xsl:template match="codelisting/line">
    <xsl:apply-templates/>
    <xsl:text>&#x000A;</xsl:text>
  </xsl:template>

  <xsl:template match="emphasis">
    <xsl:text>\emph{</xsl:text>
    <xsl:apply-templates/>
    <xsl:text>}</xsl:text>
  </xsl:template>

  <xsl:template match="strong">
    <xsl:text>\textbf{</xsl:text>
    <xsl:apply-templates/>
    <xsl:text>}</xsl:text>
  </xsl:template>

  <xsl:template match="name">
    <xsl:text>\emph{</xsl:text>
    <xsl:apply-templates/>
    <xsl:text>}</xsl:text>
  </xsl:template>

  <xsl:template match="code">
    <xsl:text>\verb|</xsl:text>
    <xsl:apply-templates/>
    <xsl:text>|</xsl:text>
  </xsl:template>

  <xsl:template match="//title/url | //para/url | //emphasis/url">
    <xsl:text>\url{</xsl:text>
    <xsl:apply-templates/>
    <xsl:text>}</xsl:text>
  </xsl:template>

  <xsl:template match="//line/url">
    <xsl:apply-templates/>
  </xsl:template>

  <xsl:template match="copyright">
    <xsl:text>\copyright{}</xsl:text>
  </xsl:template>

  <xsl:template match="apiname">
    <xsl:text>{\tt\bf </xsl:text>
      <xsl:value-of select="."/>
    <xsl:text>}</xsl:text>
  </xsl:template>

  <xsl:template match="var">
    <xsl:text>\textit{</xsl:text>
      <xsl:value-of select="."/>
    <xsl:text>}</xsl:text>
  </xsl:template> 

</xsl:stylesheet>