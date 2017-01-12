.PHONY: install install_local docs collectstatic

install:
	pip install -r requirements/production.txt

install_local:
	pip install -r requirements/local.txt
	pip install -r docs/requirements.txt

docs:
	rm -rf ./docs/build/html/
	cd docs && sphinx-build -b html -d build/doctrees source build/html
	@xdg-open docs/build/html/index.html >& /dev/null || open docs/build/html/index.html >& /dev/null || true

collectstatic:
	python manage.py collectstatic --noinput --settings edem.settings.base
	gulp scripts less font images
	bower install
