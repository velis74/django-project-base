Install pdflatex tool on your system.

To build documentation run:

cd TO REPOSITORY ROOT
pip install -r requirements.txt
cd docs
sphinx-build -b html source build
sphinx-build -b latex source build/latex -c source/conf.py
cd build/latex
pdflatex djangoprojectbase.tex
cd ../
cp build/latex/djangoprojectbase.pdf ./
