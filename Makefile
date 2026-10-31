PYTHON ?= python3
NMLC ?= nmlc
OPENTTD ?= ../../build/openttd

.PHONY: all catalog clean
all:
	$(PYTHON) tools/build.py --nmlc $(NMLC)
catalog: all
	$(PYTHON) tools/catalog.py
	$(PYTHON) tools/vehicle_catalog.py
	pdfunite build/NextGRF-Catalog.pdf build/NextGRF-Rail-Catalog.pdf build/NextGRF-Surface-Catalog.pdf build/NextGRF-Full-Catalog.pdf
clean:
	$(PYTHON) -c 'import shutil; shutil.rmtree("build", ignore_errors=True)'
