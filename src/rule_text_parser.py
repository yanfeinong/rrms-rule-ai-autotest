from typing import Any

from src.common import GENERATED_DIR, INPUT_DIR, ensure_dirs, read_yaml, write_json


class RuleTextParser:
    REQUIRED_FIELDS = ["rule_id", "rule_name", "source_table", "target_field", "expression"]

    def _validate_rule(self, rule: dict[str, Any]) -> None:
        missing = [field for field in self.REQUIRED_FIELDS if not rule.get(field)]
        if missing:
            raise ValueError(f"规则缺少必填字段: {missing}, rule={rule}")

    def _parse_target_fields(self, target_field: str) -> list[str]:
        return [item.strip() for item in target_field.split(",") if item.strip()]

    def run(self) -> None:
        ensure_dirs()
        input_path = INPUT_DIR / "rules_input.yaml"
        payload = read_yaml(input_path)
        if not payload or "rules" not in payload:
            raise ValueError("rules_input.yaml 缺少 rules 字段")

        rules = payload.get("rules", [])
        if not isinstance(rules, list) or not rules:
            raise ValueError("rules_input.yaml 的 rules 必须为非空列表")

        parsed_rules: list[dict[str, Any]] = []
        for rule in rules:
            self._validate_rule(rule)
            parsed_rules.append(
                {
                    "rule_id": rule["rule_id"],
                    "exec_rule_id": rule.get("exec_rule_id", rule["rule_id"]),
                    "rule_name": rule["rule_name"],
                    "source_table": rule["source_table"],
                    "target_field": rule["target_field"],
                    "target_fields": self._parse_target_fields(rule["target_field"]),
                    "expression": rule["expression"],
                    "description": rule.get("description", ""),
                    "semantics": rule.get("semantics", {}),
                }
            )

        output = {"release_id": payload.get("release_id", "UNKNOWN"), "rules": parsed_rules}
        output_path = GENERATED_DIR / "rules_parsed.json"
        write_json(output_path, output)
        print(f"[parse] 规则解析完成，输出: {output_path}")
