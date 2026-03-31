import subprocess
import sys

def main():
    executable = "c:/Program Files/Python312/python.exe"
    result = subprocess.run([executable, "-m", "pytest", "tests/test_security.py", "-v"], capture_output=True, text=True, encoding='utf-8')
    with open("test_output.txt", "w", encoding="utf-8") as f:
        f.write(result.stdout)
        f.write("\nSTDERR:\n")
        f.write(result.stderr)
    print("Done")

if __name__ == "__main__":
    main()
