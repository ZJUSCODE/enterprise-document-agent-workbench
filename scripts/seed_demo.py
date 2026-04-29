from pathlib import Path

import httpx


API_BASE = "http://localhost:8000/api"
ROOT = Path(__file__).resolve().parents[1]


def main() -> None:
    with httpx.Client(timeout=60) as client:
        templates = client.get(f"{API_BASE}/templates").json()
        template_id = templates[0]["id"] if templates else "contract_review"
        uploaded_ids = []
        for sample in [ROOT / "samples" / "contract_sample.txt", ROOT / "samples" / "invoice_sample.csv"]:
            with sample.open("rb") as handle:
                response = client.post(
                    f"{API_BASE}/files/upload",
                    data={"actor": "seed.demo"},
                    files={"file": (sample.name, handle, "text/plain")},
                )
                response.raise_for_status()
                uploaded_ids.append(response.json()["id"])
        response = client.post(
            f"{API_BASE}/tasks/batch",
            json={"file_ids": uploaded_ids, "template_id": template_id, "submitted_by": "seed.demo", "priority": 5},
        )
        response.raise_for_status()
        print({"created_tasks": [task["id"] for task in response.json()]})


if __name__ == "__main__":
    main()
