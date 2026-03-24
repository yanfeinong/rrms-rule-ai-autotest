from typing import Any

from src.common import GENERATED_DIR, ensure_dirs, read_json, write_json


class CaseGenerator:
    def _rule_semantics(self, rule: dict[str, Any]) -> tuple[list[Any], list[Any]]:
        semantics = rule.get("semantics", {}) or {}
        empty_values = semantics.get("empty_values", ["", "空"])
        # 兼容用户补充场景：空格字符串
        if " " not in empty_values:
            empty_values = [*empty_values, " "]

        null_values_not_empty = semantics.get("null_values_not_empty", [None, "NULL", "null"])
        if "null" not in null_values_not_empty:
            null_values_not_empty = [*null_values_not_empty, "null"]
        return empty_values, null_values_not_empty

    def _pick_empty_pair(self, empty_values: list[Any]) -> tuple[Any, Any]:
        empty_a = "" if "" in empty_values else (empty_values[0] if empty_values else "")
        empty_b = " " if " " in empty_values else ("空" if "空" in empty_values else empty_a)
        return empty_a, empty_b

    def _pick_null_like_pair(self, null_values_not_empty: list[Any]) -> tuple[Any, Any]:
        non_none_values = [v for v in null_values_not_empty if v is not None]
        null_like_a = non_none_values[0] if non_none_values else "NULL"
        null_like_b = non_none_values[1] if len(non_none_values) > 1 else "null"
        return null_like_a, null_like_b

    def _build_not_null_common_cases(self, rule: dict[str, Any], field_names: list[str]) -> list[dict[str, Any]]:
        # 通用空值语义模板：从每条规则 semantics 动态读取
        if not field_names:
            raise ValueError(f"非空规则字段不能为空: {rule}")
        empty_values, null_values_not_empty = self._rule_semantics(rule)
        empty_a, empty_b = self._pick_empty_pair(empty_values)
        null_like_a, null_like_b = self._pick_null_like_pair(null_values_not_empty)

        if len(field_names) == 1:
            f1 = field_names[0]
            return [
                {
                    "case_id": f"{rule['rule_id']}_FAIL_001",
                    "scenario": "空字符串与空格字符串，视为空值，应失败",
                    "expected_pass": 0,
                    "sample_rows": [{f1: empty_a}, {f1: empty_b}],
                },
                {
                    "case_id": f"{rule['rule_id']}_PASS_001",
                    "scenario": "普通非空字符串，应通过",
                    "expected_pass": 1,
                    "sample_rows": [{f1: "v1"}],
                },
                {
                    "case_id": f"{rule['rule_id']}_PASS_002",
                    "scenario": "NULL/null 字符串不算空值，应通过",
                    "expected_pass": 1,
                    "sample_rows": [{f1: null_like_a}, {f1: null_like_b}],
                },
                {
                    "case_id": f"{rule['rule_id']}_PASS_003",
                    "scenario": "真实 NULL 按说明不算空值，应通过",
                    "expected_pass": 1,
                    "sample_rows": [{f1: None}],
                },
            ]

        f1, f2 = field_names[0], field_names[1]
        return [
            {
                "case_id": f"{rule['rule_id']}_FAIL_001",
                "scenario": "组合字段全部为空字符串/空字面量，应失败",
                "expected_pass": 0,
                "sample_rows": [
                    {f1: empty_a, f2: empty_a},
                    {f1: empty_b, f2: empty_a},
                ],
            },
            {
                "case_id": f"{rule['rule_id']}_PASS_001",
                "scenario": "组合字段至少一个非空，应通过",
                "expected_pass": 1,
                "sample_rows": [
                    {f1: "商品A", f2: ""},
                    {f1: "", f2: "SKU-001"},
                ],
            },
            {
                "case_id": f"{rule['rule_id']}_PASS_002",
                "scenario": "null/NULL 不算空值，应通过",
                "expected_pass": 1,
                "sample_rows": [
                    {f1: null_like_a, f2: empty_a},
                    {f1: null_like_b, f2: empty_b},
                ],
            },
            {
                "case_id": f"{rule['rule_id']}_FAIL_002",
                "scenario": "空字符串+空格字符串组合，视为空值，应失败",
                "expected_pass": 0,
                "sample_rows": [
                    {f1: empty_a, f2: empty_b},
                    {f1: empty_b, f2: empty_a},
                ],
            },
            {
                "case_id": f"{rule['rule_id']}_PASS_003",
                "scenario": "NULL 字符串与空值组合，NULL 不算空值，应通过",
                "expected_pass": 1,
                "sample_rows": [
                    {f1: null_like_a, f2: empty_b},
                    {f1: empty_a, f2: null_like_a},
                ],
            },
            {
                "case_id": f"{rule['rule_id']}_PASS_004",
                "scenario": "真实 NULL 与字符串空格混合场景，NULL 不算空值，应通过",
                "expected_pass": 1,
                "sample_rows": [
                    {f1: None, f2: " "},
                ],
            },
        ]

    def _build_default_cases(self, rule: dict[str, Any]) -> list[dict[str, Any]]:
        field = rule["target_field"]
        expression = rule["expression"]
        target_fields = rule.get("target_fields", [field])

        if expression.startswith("IsNotAllTheSame("):
            return [
                {
                    "case_id": f"{rule['rule_id']}_PASS_001",
                    "scenario": f"{field} 存在多个不同值",
                    "expected_pass": 1,
                    "sample_values": ["alipay", "wechat", "bank"],
                },
                {
                    "case_id": f"{rule['rule_id']}_FAIL_001",
                    "scenario": f"{field} 全部相同",
                    "expected_pass": 0,
                    "sample_values": ["alipay", "alipay", "alipay"],
                },
                {
                    "case_id": f"{rule['rule_id']}_PASS_002",
                    "scenario": f"{field} 大小写差异",
                    "expected_pass": 1,
                    "sample_values": ["alipay", "Alipay"],
                },
            ]

        if expression.startswith("IsNotNullComb("):
            if len(target_fields) < 2:
                raise ValueError(f"IsNotNullComb 规则至少需要2个字段: {rule}")
            return self._build_not_null_common_cases(rule, target_fields)

        if expression.startswith("IsNotNull("):
            return self._build_not_null_common_cases(rule, target_fields[:1])

        # 兜底用例：后续可扩展更多规则函数模板
        return [
            {
                "case_id": f"{rule['rule_id']}_PASS_001",
                "scenario": "默认通过场景",
                "expected_pass": 1,
                "sample_values": ["v1", "v2"],
            },
            {
                "case_id": f"{rule['rule_id']}_FAIL_001",
                "scenario": "默认失败场景",
                "expected_pass": 0,
                "sample_values": ["v1", "v1"],
            },
        ]

    def run(self) -> None:
        ensure_dirs()
        parsed_path = GENERATED_DIR / "rules_parsed.json"
        parsed = read_json(parsed_path)
        rules = parsed.get("rules", [])

        case_output: dict[str, Any] = {"release_id": parsed.get("release_id", "UNKNOWN"), "rule_cases": []}
        for rule in rules:
            case_output["rule_cases"].append(
                {
                    "rule_id": rule["rule_id"],
                    "exec_rule_id": rule.get("exec_rule_id", rule["rule_id"]),
                    "source_table": rule["source_table"],
                    "target_field": rule["target_field"],
                    "target_fields": rule.get("target_fields", [rule["target_field"]]),
                    "cases": self._build_default_cases(rule),
                }
            )

        output_path = GENERATED_DIR / "cases_generated.json"
        write_json(output_path, case_output)
        print(f"[case] 测试案例生成完成，输出: {output_path}")
