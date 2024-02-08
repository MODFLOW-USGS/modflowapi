import os

try:
    import isort

    print(f"isort version: {isort.__version__}")
except ModuleNotFoundError:
    print("isort not installed\n\tInstall using pip install isort")

try:
    import black

    print(f"black version: {black.__version__}")
except ModuleNotFoundError:
    print("black not installed\n\tInstall using pip install black")

# uncomment if/when isort used
# print("running isort...")
# os.system("isort -v ../modflowapi")

print("running black...")
os.system("black -v ../modflowapi")
