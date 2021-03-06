.PHONY: install install_local docs collectstatic

APP?=vocrm
CONTAINER_IMAGE?=reg.sobsam.com/${APP}
TAG?=latest

install:
	pip install -r requirements/production.txt

install_local:
	pip install -r requirements/local.txt
	pip install -r docs/requirements.txt

docs:
	rm -rf ./docs/build/html/
	cp CHANGELOG.rst docs/source/
	cd docs && sphinx-build -b html -d build/doctrees source build/docs
	@xdg-open docs/build/docs/README.html >& /dev/null || open docs/docs/html/README.html >& /dev/null || true

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

build:
	docker build -t $(CONTAINER_IMAGE):$(TAG) .

push: build
	docker push $(CONTAINER_IMAGE):$(TAG)

clean:
	rm -rf ./**/*.pyc
	rm -rf ./**/__pycache__

test: clean
	docker-compose -f dev.yml run --rm django python manage.py test
