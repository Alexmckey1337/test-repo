.PHONY: install install_local docs

install:
	pip install -r requirements/production.txt

install_local:
	pip install -r requirements/local.txt
	pip install -r docs/requirements.txt

docs:
	rm -rf ./docs/build/html/
	cd docs && sphinx-build -b html -d build/doctrees source build/html
	@xdg-open docs/build/html/index.html >& /dev/null || open docs/build/html/index.html >& /dev/null || true