import json

import httpx


API_BASE = "http://localhost:8000/api"


def main() -> None:
    response = httpx.get(f"{API_BASE}/metrics/evaluation", timeout=30)
    response.raise_for_status()
    print(json.dumps(response.json(), ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
