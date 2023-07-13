#update the export script and run the installer builder
import os, subprocess, shlex
currentscript_dir = os.path.dirname(os.path.abspath(__file__))
setupscript_path = os.path.join(currentscript_dir, "innosetup_exportscript.iss")
pltk_path = os.path.join(currentscript_dir, "promptlocker.py")
plicon_path = os.path.join(currentscript_dir, "promptlockericon.ico")
build_folder = os.path.join(currentscript_dir, "promptlocker_build")
setupoutput_path = os.path.join(currentscript_dir, "promptlocker_installer")

program_files_x86_path = os.environ.get("PROGRAMFILES(X86)")
iscc_path = os.path.join(program_files_x86_path, "Inno Setup 6\ISCC.exe")

if not os.path.isfile(iscc_path):
    print("ISCC doesn't exist. (Install Inno Setup first?)")
    exit()

pl_version = ""

# Get version
with open(pltk_path, 'r', encoding='utf-8') as file:
    pl_lines = file.readlines()

for line in pl_lines:
    if line.startswith("pl_version = "):
        pl_version =line.partition("=")[2].strip()
        break

lines = ""

def readsetuplines():
    global lines
    with open(setupscript_path, 'r', encoding='utf-8') as file:
        lines = file.readlines()

# Update the file version, icon path, and remove every Source path
def cleansetuplines(reset=""):
    global lines
    print("Updating the Installer script.")
    with open(setupscript_path, 'w', encoding='utf-8') as file:
        for line in lines:
            if line.startswith('#define MyAppVersion'):
                line = f'#define MyAppVersion {pl_version}\n'
            elif line.startswith('SetupIconFile='):
                if reset:
                    print("Cleaning paths in Installer script after using.")
                    line = f'SetupIconFile=""\n'
                else:
                    line = f'SetupIconFile="{plicon_path}"\n'
            elif line.startswith('OutputDir='):
                if reset:
                    print("Cleaning paths in Installer script after using.")
                    line = f'OutputDir=""\n'
                else:
                    line = f'OutputDir="{setupoutput_path}"\n'
            elif line.startswith('Source:'):
                continue

            file.write(line)

readsetuplines()

# Make backup
backup_filename = setupscript_path + ".bak"
if os.path.exists(backup_filename):
    os.remove(backup_filename)
os.rename(setupscript_path, setupscript_path + ".bak")

cleansetuplines()

readsetuplines()

sourceline_beginning = f'Source: "{build_folder}\\'
sourceline_end = '; DestDir: "{app}"; Flags: ignoreversion'

# Filling the Source paths
print("Adding paths on the Installer script.")
with open(setupscript_path, 'w', encoding='utf-8') as file:
    for line in lines:
        file.write(line)
        if line.startswith('[Files]'):
            file.write(sourceline_beginning + '{#MyAppExeName}"'+ sourceline_end + "\n")
            for filename in os.listdir(build_folder):
                filepath = os.path.join(build_folder, filename)
                if os.path.isfile(filepath):
                    if filename != "promptlocker.exe":
                        file.write(sourceline_beginning + f'{filename}"'+ sourceline_end + "\n")
                elif os.path.isdir(filepath):
                    file.write(sourceline_beginning + f'{filename}\*"'+ f'; DestDir: "{{app}}\{filename}"; Flags: ignoreversion recursesubdirs createallsubdirs' + "\n")

# Running the installer building script
print("Building the installer.\n")
# subprocess.run(f'"{iscc_path}" {setupscript_path}', shell=True)
print()

logfile_path = os.path.join(currentscript_dir, "buildinstaller_log.txt")
if os.path.exists(logfile_path):
    os.remove(logfile_path)

command = shlex.split(f"\"{iscc_path}\" \"{setupscript_path}\"")
print(command)
process = subprocess.Popen(command, stdout=subprocess.PIPE, universal_newlines=True)

# Open the file in append mode to save the output
with open(logfile_path, 'a') as file:
    # Read and write the output line by line
    for line in process.stdout:
        file.write(line)
        print(line, end='')

# Cleaning all paths from the installer setup script
cleansetuplines("reset")


