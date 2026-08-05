.PHONY: install pipeline pipeline-offline dashboard test preflight syntax clean

install:
	python -m pip install --upgrade pip
	python -m pip install -r requirements-dev.txt

pipeline:
	python src/main.py

pipeline-offline:
	python src/main.py --offline

dashboard:
	python -m streamlit run app.py

test:
	python -m pytest -q

preflight:
	python src/main.py --offline
	python src/preflight.py

syntax:
	python -m py_compile app.py src/main.py src/dashboard_utils.py src/preflight.py src/gtm_demo.py src/snowflake_adapter.py

clean:
	rm -rf __pycache__ src/__pycache__ tests/__pycache__ .pytest_cache
