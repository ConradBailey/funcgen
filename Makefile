NPROC := $(shell nproc)

sure: typecheck lint test coverage

test:
	tox -c tox.ini -p $(NPROC)

lint:
	pylint --rcfile .pylintrc funcgen

typecheck:
	pytype --config .pytyperc funcgen

coverage:
	pytest --cov-config .coveragerc --cov=funcgen

.PHONY: docs
docs: doctest
	cd docs && make clean && make html

doctest:
	cd docs && make doctest

publish: sure docs
	python3 setup.py sdist bdist_wheel
	twine upload dist/*
	rm -fr build dist .egg funcgen.egg-info

clean:
	rm -fr build dist .egg funcgen.egg-info
