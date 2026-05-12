import argparse
import os
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parent
LOCAL_PACKAGES = ROOT / ".python"

sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(LOCAL_PACKAGES))


def main() -> int:
    parser = argparse.ArgumentParser(description="Run Feedback Admin API")
    parser.add_argument("--host", default=os.getenv("HOST", "127.0.0.1"))
    parser.add_argument("--port", type=int, default=int(os.getenv("PORT", "8000")))
    args = parser.parse_args()

    try:
        import uvicorn
    except ModuleNotFoundError:
        print("uvicorn олдсонгүй. Эхлээд backend dependencies суулгана уу:")
        print(
            r'& "C:\Program Files\PostgreSQL\18\pgAdmin 4\python\python.exe" '
            r"-m pip install -r requirements.txt --target .python"
        )
        return 1

    uvicorn.run("app.main:app", host=args.host, port=args.port)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
