example:
	python example/app.py

test:
	nosetests -s --pdb --with-coverage --cover-package=flask_canvas

docs:
	cd docs && make html

.PHONY: example docs
