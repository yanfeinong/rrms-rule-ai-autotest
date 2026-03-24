from src.common import GENERATED_DIR, REPORTS_DIR, ensure_dirs, read_json, write_json


class ReportBuilder:
    def run(self) -> None:
        ensure_dirs()
        compare_payload = read_json(GENERATED_DIR / "comparison_result.json")
        summary = compare_payload.get("summary", {})
        details = compare_payload.get("details", [])

        md_lines = [
            "# 规则自动化测试报告",
            "",
            "## 汇总",
            f"- 总用例数: {summary.get('total', 0)}",
            f"- 通过数: {summary.get('passed', 0)}",
            f"- 失败数: {summary.get('failed', 0)}",
            f"- 通过率: {summary.get('pass_rate', 0)}%",
            "",
            "## 明细",
            "| rule_id | case_id | expected_pass | actual_pass | matched |",
            "|---|---|---:|---:|---|",
        ]
        for item in details:
            md_lines.append(
                f"| {item.get('rule_id','')} | {item.get('case_id','')} | "
                f"{item.get('expected_pass','')} | {item.get('actual_pass','')} | "
                f"{item.get('matched','')} |"
            )

        md_path = REPORTS_DIR / "report.md"
        md_path.write_text("\n".join(md_lines) + "\n", encoding="utf-8")

        json_path = REPORTS_DIR / "report.json"
        write_json(json_path, compare_payload)
        print(f"[report] 测试报告生成完成，输出: {md_path}, {json_path}")
