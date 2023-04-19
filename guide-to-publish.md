# How to publish to PyPi

1) If present delete dist folder

2) If not done yet, install build and twine via
```
pip install build twine
```
3) Update the version in ``modflowapi/version.py``

4) Re-create the wheels:
```
python -m build
```
5) Re-upload the new files:
```
twine upload dist/*
```
