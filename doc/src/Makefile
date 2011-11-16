all: pdf ps html text

pdf: ../manygui.pdf

ps: ../manygui.ps

html: ../manygui.html

text: ../manygui.txt

clean:
	rm -f *.aux *.toc *.log *~

distclean: clean
	rm -f ../*.html ../*.pdf ../*.ps *.tex ../*.txt temp.xml

../manygui.pdf: manygui.tex manygui.sty
	pdflatex manygui
	pdflatex manygui
	mv manygui.pdf ..

../manygui.ps: ../manygui.pdf
	pdf2ps ../manygui.pdf ../manygui.ps

manygui.tex: temp.xml min2tex.xsl
	xalan -IN temp.xml -XSL min2tex.xsl -OUT manygui.tex

../manygui.html: temp.xml min2html.xsl
	xalan -IN temp.xml -XSL min2html.xsl -OUT manygui.html
	mv manygui.html ..

manygui.lynx.html: temp.xml min2lynx.xsl
	xalan -IN temp.xml -XSL min2lynx.xsl -OUT manygui.lynx.html

../manygui.txt: manygui.lynx.html
	lynx -dump -nolist manygui.lynx.html > manygui.txt
	rm manygui.lynx.html
	mv manygui.txt ..

temp.xml: manygui.xml api_reference.xml copyrightholders.xml installation.xml introduction.xml using_manygui.xml
	python insertdate.py manygui.xml > temp.xml