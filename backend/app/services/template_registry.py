BUILTIN_TEMPLATES = [
    {
        "id": "contract_review",
        "name": "Contract Review Memo",
        "description": "Structured contract extraction, risk summary, and approval memo.",
        "document_type": "contract",
        "output_format": "markdown",
        "version": "1.0.0",
        "body": """# Contract Review Memo

Document: {{ file.original_filename }}
Task: {{ task.id }}
Detected type: {{ task.classified_as }}

## Executive Summary
{{ summary.brief }}

## Key Points
{% for point in summary.key_points %}
- {{ point }}
{% endfor %}

## Extracted Fields
{% for key, value in fields.items() %}
- {{ key }}: {{ value }}
{% endfor %}

## Review Flags
{% for anomaly in anomalies %}
- [{{ anomaly.severity }}] {{ anomaly.message }}
{% else %}
- No review flags detected.
{% endfor %}
""",
    },
    {
        "id": "invoice_summary",
        "name": "Invoice Processing Sheet",
        "description": "Invoice field extraction and payment review output.",
        "document_type": "invoice",
        "output_format": "markdown",
        "version": "1.0.0",
        "body": """# Invoice Processing Sheet

Source file: {{ file.original_filename }}
Task: {{ task.id }}

## Payment Fields
{% for key, value in fields.items() %}
- {{ key }}: {{ value }}
{% endfor %}

## Summary
{{ summary.brief }}

## Exceptions
{% for anomaly in anomalies %}
- [{{ anomaly.severity }}] {{ anomaly.message }}
{% else %}
- No exception.
{% endfor %}
""",
    },
    {
        "id": "general_brief",
        "name": "General Document Brief",
        "description": "Generic structured summary for documents without a dedicated template.",
        "document_type": "general",
        "output_format": "markdown",
        "version": "1.0.0",
        "body": """# Document Brief

Source file: {{ file.original_filename }}

## Summary
{{ summary.brief }}

## Key Points
{% for point in summary.key_points %}
- {{ point }}
{% endfor %}

## Structured Fields
{% for key, value in fields.items() %}
- {{ key }}: {{ value }}
{% endfor %}

## Review Flags
{% for anomaly in anomalies %}
- [{{ anomaly.severity }}] {{ anomaly.message }}
{% else %}
- No review flags detected.
{% endfor %}
""",
    },
]
