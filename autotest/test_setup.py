import os
import shutil
import pytest


@pytest.mark.order(0)
def test_setup():
    if os.path.exists("temp"):
        shutil.rmtree("temp")
    os.mkdir("temp")
