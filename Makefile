PYTHON ?= python

.PHONY: install
install:
	$(PYTHON) setup.py install

.PHONY: clean
clean:
	$(PYTHON) setup.py clean --all

.PHONY: test
test:
	./test/utils/run_tests.sh
