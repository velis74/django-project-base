Install pdflatex tool on your system. Jure 8.10.2021: I found this not necessary when building either pdf or html targets

To build documentation run:

cd TO REPOSITORY ROOT
pip install -r requirements.txt
cd docs
sphinx-build -b html source build
sphinx-build -b pdf source .

