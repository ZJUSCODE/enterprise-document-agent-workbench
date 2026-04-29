from fastapi.testclient import TestClient

from app.main import app


def test_upload_create_task_and_wait_for_approval() -> None:
    with TestClient(app) as client:
        upload = client.post(
            "/api/files/upload",
            data={"actor": "pytest"},
            files={
                "file": (
                    "contract.txt",
                    "合同编号: CT-2026-0417\n甲方: 上海示例科技有限公司\n乙方: 北京流程自动化服务有限公司\n生效日期: 2026年4月17日",
                    "text/plain",
                )
            },
        )
        assert upload.status_code == 201
        file_id = upload.json()["id"]

        created = client.post(
            "/api/tasks",
            json={"file_id": file_id, "template_id": "contract_review", "submitted_by": "pytest", "priority": 5},
        )
        assert created.status_code == 201
        task_id = created.json()["id"]

        detail = client.get(f"/api/tasks/{task_id}")
        assert detail.status_code == 200
        payload = detail.json()
        assert payload["status"] == "waiting_approval"
        assert payload["progress"] == 95
        assert payload["generated_artifact_key"]
        assert payload["approvals"][0]["status"] == "pending"
        assert len(payload["summary"]["agent_trace"]["steps"]) >= 6

        artifact = client.get(f"/api/tasks/{task_id}/export")
        assert artifact.status_code == 200
        assert "Contract Review Memo" in artifact.text

        docx_artifact = client.get(f"/api/tasks/{task_id}/export?format=docx")
        assert docx_artifact.status_code == 200
        assert docx_artifact.content.startswith(b"PK")

        pdf_artifact = client.get(f"/api/tasks/{task_id}/export?format=pdf")
        assert pdf_artifact.status_code == 200
        assert pdf_artifact.content.startswith(b"%PDF")
        assert pdf_artifact.headers["content-type"] == "application/pdf"

        revised = client.patch(
            f"/api/tasks/{task_id}/result",
            json={
                "revised_by": "reviewer.pytest",
                "comment": "补充人工修订字段",
                "extracted_fields": {
                    **payload["extracted_fields"],
                    "manual_review_note": "字段已复核",
                },
                "anomalies": [],
            },
        )
        assert revised.status_code == 200
        revised_payload = revised.json()
        assert revised_payload["status"] == "waiting_approval"
        assert revised_payload["result_version"] == 2
        assert revised_payload["extracted_fields"]["manual_review_note"] == "字段已复核"

        versions = client.get(f"/api/tasks/{task_id}/versions")
        assert versions.status_code == 200
        assert [version["version"] for version in versions.json()] == [1, 2]

        rag = client.post("/api/rag/query", json={"question": "合同的生效日期是什么？", "top_k": 3})
        assert rag.status_code == 200
        assert rag.json()["hits"]
