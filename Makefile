PYTHON ?= python3
NMLC ?= nmlc
OPENTTD ?= ../../build/openttd

.PHONY: all catalog clean
all:
	$(PYTHON) tools/build.py --nmlc $(NMLC)
catalog: all
	$(PYTHON) tools/catalog.py
clean:
	$(PYTHON) -c 'import shutil; shutil.rmtree("build", ignore_errors=True)'
