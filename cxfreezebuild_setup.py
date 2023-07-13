import os
curdir = os.getcwd()
os.chdir(os.path.join(curdir, "cxfreezevenv"))

from cx_Freeze import setup, Executable
import sys

# 👇github maindirectory, assuming the setup.py is outside the venv directory
currentscript_dir = os.path.dirname(os.path.abspath(__file__))

# venv_dir = os.path.join(currentscript_dir, "cxfreezevenv") # replaces directory_above
# directory_above = os.path.dirname(currentscript_dir)
build_folder = os.path.join(currentscript_dir, "promptlocker_build")
pltk_path = os.path.join(currentscript_dir, "promptlocker.py")
plicon_path = os.path.join(currentscript_dir, "promptlockericon.ico")

os.makedirs(build_folder, exist_ok=True)

build_exe_options = {
    "build_exe": build_folder,
    "includes": ["pl_crypt"],
    "path": sys.path + [currentscript_dir],
    "optimize": 2,
    "include_files": plicon_path,
} #    "packages": ["tkinter", "tkinterdnd2", "PIL"]

base = "Win32GUI" if sys.platform == "win32" else None

setup(name = "Promptlocker" ,
      version = "0.0.3" ,
      description = "" , 
      options={"build_exe": build_exe_options},
      executables = [Executable(pltk_path, \
                                base=base, target_name="promptlocker", \
                                icon=plicon_path)])