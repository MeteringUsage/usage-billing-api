def test_metric_crud(client):
    created = client.post(
        "/billable-metrics",
        json={
            "name": "LLM output tokens",
            "code": "llm_tokens",
            "metric_type": "metered",
            "aggregation_type": "sum",
            "aggregate_property": "tokens_out",
        },
    )
    assert created.status_code == 201
    body = created.json()
    assert body["code"] == "llm_tokens"
    assert body["id"] is not None

    listed = client.get("/billable-metrics")
    assert listed.status_code == 200
    assert listed.json()["meta"]["total_count"] == 1

    fetched = client.get("/billable-metrics/llm_tokens")
    assert fetched.status_code == 200
    assert fetched.json()["name"] == "LLM output tokens"

    updated = client.patch(
        "/billable-metrics/llm_tokens",
        json={"description": "Generated tokens"},
    )
    assert updated.status_code == 200
    assert updated.json()["description"] == "Generated tokens"

    missing = client.get("/billable-metrics/missing")
    assert missing.status_code == 404

    deleted = client.delete("/billable-metrics/llm_tokens")
    assert deleted.status_code == 200
    assert client.get("/billable-metrics/llm_tokens").status_code == 404
