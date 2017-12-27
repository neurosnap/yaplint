dev:
	pip install -e packages/yaplint_core
	pip install -e packages/yaplint
	pip install -e packages/require_spaces
	pip install -e packages/blank_lines
	pip install -e packages/basic_reporter

test:
	pytest packages -vv

clean:
	find ./packages -name "__pycache__" -type d -delete
	find ./packages -name "*.egg.info" -type d -delete

ex:
	python packages/yaplint/yaplint.py --path=packages/yaplint_core/fixtures/runner_one --rules="require_spaces,blank_lines"
