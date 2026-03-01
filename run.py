import argparse
import subprocess
import sys
from pathlib import Path


SCRIPT_MAP = {
    "test": "test.py",
    "openrouter": "testopenrouter.py",
    "openai": "testopenai.py",
    "glm": "testGLM.py",
    "deepseek": "testDeepSeek.py",
}


def parse_args() -> tuple[argparse.Namespace, list[str]]:
    parser = argparse.ArgumentParser(
        description="统一运行入口：按 provider 选择对应测试脚本"
    )
    parser.add_argument(
        "provider",
        choices=SCRIPT_MAP.keys(),
        help="要运行的脚本类型：test/openrouter/openai/glm/deepseek",
    )
    return parser.parse_known_args()


def main() -> int:
    args, extra_args = parse_args()
    script_name = SCRIPT_MAP[args.provider]
    script_path = Path(__file__).resolve().parent / script_name

    if not script_path.exists():
        print(f"Script not found: {script_path}")
        return 1

    command = [sys.executable, str(script_path), *extra_args]
    print(f"Running: {' '.join(command)}")

    try:
        result = subprocess.run(command, check=False)
        return result.returncode
    except KeyboardInterrupt:
        print("Interrupted by user.")
        return 130


if __name__ == "__main__":
    raise SystemExit(main())
