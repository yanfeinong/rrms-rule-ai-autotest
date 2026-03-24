import os
from typing import Any
from typing import Optional

import requests

from src.common import GENERATED_DIR, ROOT_DIR, ensure_dirs, read_json, read_yaml, write_json


class RuleApiClient:
    def __init__(self, env: str = "local", biz_date: str = "1970-01-01") -> None:
        self.env = env
        self.biz_date = biz_date

    def _build_headers(self, token_env: Optional[str]) -> dict[str, str]:
        headers = {"Content-Type": "application/json"}
        if token_env:
            token = os.getenv(token_env, "")
            if token:
                headers["Authorization"] = f"Bearer {token}"
        return headers

    def _mock_execution_result(self, cases_payload: dict[str, Any]) -> dict[str, Any]:
        results: list[dict[str, Any]] = []
        for rule_item in cases_payload.get("rule_cases", []):
            for case in rule_item.get("cases", []):
                results.append(
                    {
                        "rule_id": rule_item["rule_id"],
                        "case_id": case["case_id"],
                        "actual_pass": case["expected_pass"],
                        "actual_reason": "mock_mode: 使用预期值回填",
                    }
                )
        return {"mode": "mock", "results": results}

    def _build_trigger_payload(self, trigger_cfg: dict[str, Any], rule_item: dict[str, Any]) -> dict[str, Any]:
        template = trigger_cfg.get("payload_template", {})
        payload = dict(template)

        if payload.get("ruleId_from") == "rule.exec_rule_id":
            payload["ruleId"] = rule_item.get("exec_rule_id", rule_item.get("rule_id"))
            payload.pop("ruleId_from", None)

        if payload.get("checkDataTime_from") == "runtime.biz_date":
            payload["checkDataTime"] = self.biz_date
            payload.pop("checkDataTime_from", None)

        return payload

    def run(self) -> None:
        ensure_dirs()
        api_cfg = read_yaml(ROOT_DIR / "config" / f"api.{self.env}.yaml")
        case_payload = read_json(GENERATED_DIR / "cases_generated.json")

        if api_cfg.get("mock_mode", False):
            output = self._mock_execution_result(case_payload)
            output_path = GENERATED_DIR / "api_execution_result.json"
            write_json(output_path, output)
            print(f"[execute] mock 模式执行完成，输出: {output_path}")
            return

        trigger_cfg = api_cfg.get("trigger", {})
        result_cfg = api_cfg.get("result", {})
        headers = self._build_headers(trigger_cfg.get("token_env"))

        trigger_records: list[dict[str, Any]] = []
        for rule_item in case_payload.get("rule_cases", []):
            payload = self._build_trigger_payload(trigger_cfg, rule_item)
            resp = requests.request(
                method=trigger_cfg.get("method", "POST"),
                url=trigger_cfg["url"],
                headers=headers,
                json=payload,
                timeout=30,
            )
            resp.raise_for_status()
            trigger_records.append(
                {
                    "rule_id": rule_item.get("rule_id"),
                    "exec_rule_id": rule_item.get("exec_rule_id", rule_item.get("rule_id")),
                    "request_payload": payload,
                    "response": resp.json(),
                }
            )

        output_path = GENERATED_DIR / "api_execution_result.json"
        if result_cfg.get("enabled", False):
            query_headers = self._build_headers(result_cfg.get("token_env"))
            all_results: list[dict[str, Any]] = []
            for item in trigger_records:
                job_id = item["response"].get("job_id")
                query_resp = requests.request(
                    method=result_cfg.get("method", "POST"),
                    url=result_cfg["url"],
                    headers=query_headers,
                    json={"job_id": job_id},
                    timeout=30,
                )
                query_resp.raise_for_status()
                query_data = query_resp.json()
                all_results.extend(query_data.get("results", []))
            write_json(output_path, {"mode": "api", "trigger_records": trigger_records, "results": all_results})
        else:
            # 没有结果查询接口时，先输出触发记录，结果列表留空等待后续接入
            write_json(output_path, {"mode": "api-trigger-only", "trigger_records": trigger_records, "results": []})
        print(f"[execute] API 执行完成，输出: {output_path}")
