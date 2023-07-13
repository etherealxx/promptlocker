import os
import subprocess

# Create a virtual environment
venv_name = 'cxfreezevenv'
currentscript_dir = os.path.dirname(os.path.abspath(__file__))
venv_path = os.path.join(currentscript_dir, venv_name)

if os.path.exists(venv_path):
    print('venv already installed.')
    exit()

# Activate the virtual environment
print('building venv.')
subprocess.run(['python', '-m', 'venv', venv_path])

print('activating venv.')
activate_script = os.path.join(venv_path, 'Scripts', 'activate.bat')
# subprocess.run(activate_script, shell=True)

install_cmd = [activate_script, '&&', 'pip', 'install']

# Install the dependencies
dependencies = ['cx_Freeze']

requirement_path = os.path.join(currentscript_dir, "requirements.txt")
with open(requirement_path, "r") as file:
    for line in file:
        line = line.rstrip("\n")
        dependencies.append(line)

for dependency in dependencies:
    print(f'installing {dependency} on venv.')
    # subprocess.run(['pip', 'install', dependency])
    subprocess.run(install_cmd + [dependency], shell=True)

print('Dependencies installed successfully.')
