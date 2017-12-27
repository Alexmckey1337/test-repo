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

static:
	rm -rf ./public/static/
	python manage.py collectstatic --noinput --settings edem.settings.base
	bower install
	npm install
	gulp build
	npm run development
	rm -rf ./node_modules/

collectstatic:
	rm -rf ./public/static/
	bower install
	npm install
	npm run build
	rm -rf ./node_modules/
