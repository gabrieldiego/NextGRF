PYTHON ?= python3
NMLC ?= nmlc
OPENTTD ?= ../../build/openttd

.PHONY: all check catalog test install clean
all:
	$(PYTHON) tools/build.py --nmlc $(NMLC)
catalog: all
	$(PYTHON) tools/catalog.py
	$(PYTHON) tools/vehicle_catalog.py
	pdfunite build/NextGRF-Catalog.pdf build/NextGRF-Rail-Catalog.pdf build/NextGRF-Surface-Catalog.pdf build/NextGRF-Full-Catalog.pdf
check:
	$(PYTHON) -m unittest discover -s tests -v
test: all check
	$(PYTHON) tools/smoke_test.py --openttd $(OPENTTD)
	$(PYTHON) tools/rail_smoke.py --openttd $(OPENTTD)
	$(PYTHON) tools/surface_smoke.py --openttd $(OPENTTD)
install: all
	$(PYTHON) tools/install.py
clean:
	$(PYTHON) -c 'import shutil; shutil.rmtree("build", ignore_errors=True)'
