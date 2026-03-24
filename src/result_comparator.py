from src.common import GENERATED_DIR, ensure_dirs, read_json, write_json


class ResultComparator:
    def run(self) -> None:
        ensure_dirs()
        cases_payload = read_json(GENERATED_DIR / "cases_generated.json")
        actual_payload = read_json(GENERATED_DIR / "api_execution_result.json")

        expected_map: dict[str, int] = {}
        for rule_item in cases_payload.get("rule_cases", []):
            for case in rule_item.get("cases", []):
                expected_map[case["case_id"]] = int(case["expected_pass"])

        results = actual_payload.get("results", [])
        details: list[dict[str, object]] = []
        pass_count = 0
        fail_count = 0

        for item in results:
            case_id = item.get("case_id", "")
            expected = expected_map.get(case_id)
            actual = int(item.get("actual_pass", -1))
            matched = expected == actual
            if matched:
                pass_count += 1
            else:
                fail_count += 1
            details.append(
                {
                    "rule_id": item.get("rule_id"),
                    "case_id": case_id,
                    "expected_pass": expected,
                    "actual_pass": actual,
                    "matched": matched,
                    "actual_reason": item.get("actual_reason", ""),
                }
            )

        summary = {
            "total": len(details),
            "passed": pass_count,
            "failed": fail_count,
            "pass_rate": round((pass_count / len(details) * 100), 2) if details else 0,
        }
        output = {"summary": summary, "details": details}
        output_path = GENERATED_DIR / "comparison_result.json"
        write_json(output_path, output)
        print(f"[compare] 结果比对完成，输出: {output_path}")
