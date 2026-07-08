.PHONY: install pipeline dashboard syntax clean

install:
	python -m pip install --upgrade pip
	pip install -r requirements.txt

pipeline:
	python src/main.py

dashboard:
	streamlit run app.py

syntax:
	python -m py_compile src/main.py app.py

clean:
	rm -rf __pycache__ src/__pycache__ tests/__pycache__ .pytest_cache
