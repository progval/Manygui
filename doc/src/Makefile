all: pdf ps html text

pdf: ../anygui.pdf

ps: ../anygui.ps

html: ../anygui.html

text: ../anygui.txt

clean:
	rm -f *.aux *.toc *.log *~

distclean: clean
	rm -f ../*.html ../*.pdf ../*.ps *.tex ../*.txt temp.xml

../anygui.pdf: anygui.tex anygui.sty
	pdflatex anygui
	pdflatex anygui
	mv anygui.pdf ..

../anygui.ps: ../anygui.pdf
	pdf2ps ../anygui.pdf ../anygui.ps

anygui.tex: temp.xml min2tex.xsl
	xalan -IN temp.xml -XSL min2tex.xsl -OUT anygui.tex

../anygui.html: temp.xml min2html.xsl
	xalan -IN temp.xml -XSL min2html.xsl -OUT anygui.html
	mv anygui.html ..

anygui.lynx.html: temp.xml min2lynx.xsl
	xalan -IN temp.xml -XSL min2lynx.xsl -OUT anygui.lynx.html

../anygui.txt: anygui.lynx.html
	lynx -dump -nolist anygui.lynx.html > anygui.txt
	rm anygui.lynx.html
	mv anygui.txt ..

temp.xml: anygui.xml api_reference.xml copyrightholders.xml installation.xml introduction.xml using_anygui.xml
	python insertdate.py anygui.xml > temp.xml