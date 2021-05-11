# How to publish to PyPi

1) If present delete dist folder

2) If not done yet, install twine via
```
pip install twine
```
3) Update the version number in the setup.py file.

4) Re-create the wheels:
```
python setup.py sdist bdist_wheel
```
5) Re-upload the new files:
```
twine upload dist/*
```