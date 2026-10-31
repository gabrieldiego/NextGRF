PYTHON ?= python3
NMLC ?= nmlc
OPENTTD ?= ../../build/openttd

.PHONY: all clean
all:
	$(PYTHON) tools/build.py --nmlc $(NMLC)
clean:
	$(PYTHON) -c 'import shutil; shutil.rmtree("build", ignore_errors=True)'
