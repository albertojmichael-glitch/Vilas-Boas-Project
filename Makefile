.PHONY: setup test lint format run

setup:
	python3 -m venv venv
	./venv/bin/pip install -U pip
	./venv/bin/pip install -r requirements-dev.txt

test:
	./venv/bin/pytest tests/ -v

lint:
	./venv/bin/mypy .
	./venv/bin/black --check .

format:
	./venv/bin/black .

run:
	./venv/bin/python app.py

git add .
git commit -m "style: formatando codigo com o Black"
git pushdf