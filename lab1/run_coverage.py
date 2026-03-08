import subprocess
import sys

def main():
    print("=== Запуск тестов с измерением покрытия ===")


    cmd_run = [sys.executable, "-m", "coverage", "run", "-m", "pytest"]
    print("Выполняется:", " ".join(cmd_run))
    result = subprocess.run(cmd_run, capture_output=True, text=True)
    print(result.stdout)
    print(result.stderr)


    cmd_report = [sys.executable, "-m", "coverage", "report", "-m"]
    print("\n=== Отчет по покрытию ===")
    result2 = subprocess.run(cmd_report, capture_output=True, text=True)
    print(result2.stdout)
    print(result2.stderr)



if __name__ == "__main__":
    main()