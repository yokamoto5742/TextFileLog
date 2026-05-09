import subprocess


def build_executable():

    subprocess.run([
        "pyinstaller",
        "--name=TextFileLog",
        "--windowed",
        "--icon=assets/TextFileLog.ico",
        "--add-data", "utils/config.ini:.",
        "main.py"
    ])

    print(f"Executable built successfully.")


if __name__ == "__main__":
    build_executable()
