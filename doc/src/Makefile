all: pdf ps html text

pdf: ../anygui.pdf

ps: ../anygui.ps

html: ../anygui.html

text: ../anygui.txt

clean:
	rm -f *.aux *.toc *.log *~

distclean: clean
	rm -f ../*.html ../*.pdf ../*.ps *.tex ../*.txt

../anygui.pdf: anygui.tex anygui.sty
	pdflatex anygui
	pdflatex anygui
	mv anygui.pdf ..

../anygui.ps: ../anygui.pdf
	pdf2ps ../anygui.pdf ../anygui.ps

anygui.tex: anygui.xml min2tex.xsl
	xalan -IN anygui.xml -XSL min2tex.xsl -OUT anygui.tex

../anygui.html: anygui.xml min2html.xsl
	xalan -IN anygui.xml -XSL min2html.xsl -OUT anygui.html
	mv anygui.html ..

anygui.lynx.html: anygui.xml min2lynx.xsl
	xalan -IN anygui.xml -XSL min2lynx.xsl -OUT anygui.lynx.html

../anygui.txt: anygui.lynx.html
	lynx -dump -nolist anygui.lynx.html > anygui.txt
	rm anygui.lynx.html
	mv anygui.txt ..
