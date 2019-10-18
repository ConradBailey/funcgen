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
docs:
	cd docs && make clean && make html
