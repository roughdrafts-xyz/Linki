compile: main.py
	rm -rf build/
	rm -rf dist/
	pyinstaller -F main.py