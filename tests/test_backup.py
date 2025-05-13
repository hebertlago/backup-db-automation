import os

def test_script_exists():
    assert os.path.exists("backup.py"), "O arquivo backup.py não foi encontrado."

def test_requirements_exists():
    assert os.path.exists("requirements.txt"), "O arquivo requirements.txt não foi encontrado."