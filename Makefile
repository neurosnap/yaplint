dev:
	pip install -r requirements.txt
	pip install -r requirements_dev.txt
	pip install -U -e packages/yaplint_core
	pip install -U -e packages/yaplint
	pip install -U -e packages/require_spaces
	pip install -U -e packages/blank_lines
	pip install -U -e packages/basic_reporter

test:
	pytest packages -vv

clean:
	find ./packages -name "__pycache__" -type d -delete
	find ./packages -name "*.egg.info" -type d -delete

ex:
	python packages/yaplint/yaplint.py --path=packages/yaplint_core/fixtures/runner_one --rules="require_spaces,blank_lines"
