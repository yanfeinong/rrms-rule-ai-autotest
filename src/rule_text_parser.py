import re
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

    def _extract_between(self, text: str, start: str, end: str) -> str:
        start_idx = text.find(start)
        if start_idx < 0:
            return ""
        start_idx += len(start)
        end_idx = text.find(end, start_idx)
        if end_idx < 0:
            return text[start_idx:].strip()
        return text[start_idx:end_idx].strip()

    def _parse_object(self, obj_text: str) -> tuple[str, str]:
        clean = obj_text.strip().replace("【", "").replace("】", "")
        if "." not in clean:
            raise ValueError(f"对象格式错误，应为 库.表.字段: {obj_text}")
        parts = [p.strip() for p in clean.split(".") if p.strip()]
        if len(parts) < 2:
            raise ValueError(f"对象格式错误，应至少包含 表.字段: {obj_text}")
        source_table = parts[-2]
        target_field = parts[-1]
        return source_table, target_field

    def _parse_text_rules(self, text: str) -> dict[str, Any]:
        lines = [line.rstrip() for line in text.splitlines()]
        blocks: list[list[str]] = []
        current: list[str] = []
        started = False
        for line in lines:
            if line.strip().startswith("规则ID："):
                started = True
                if current:
                    blocks.append(current)
                current = [line]
            elif started:
                if line.strip() or current:
                    current.append(line)
        if current:
            blocks.append(current)

        rules: list[dict[str, Any]] = []
        for block in blocks:
            block_text = "\n".join(block)
            rule_id = self._extract_between(block_text, "规则ID：", "\n")
            rule_name = self._extract_between(block_text, "规则名：", "\n")
            expression = self._extract_between(block_text, "表达式：", "\n")
            obj_text = self._extract_between(block_text, "对象：", "\n")
            desc_text = self._extract_between(block_text, "说明：", "\n")
            exec_rule_id = self._extract_between(block_text, "执行规则ID：", "\n") or rule_id

            source_table, target_field = self._parse_object(obj_text)

            semantics = {
                "empty_values": ["", " ", "空"],
                "null_values_not_empty": [None, "NULL", "null"],
                "case_sensitive": True,
            }
            if re.search(r"大小写不敏感", block_text):
                semantics["case_sensitive"] = False

            rule = {
                "rule_id": rule_id,
                "exec_rule_id": exec_rule_id,
                "rule_name": rule_name,
                "source_table": source_table,
                "target_field": target_field,
                "target_fields": self._parse_target_fields(target_field),
                "expression": expression,
                "description": desc_text,
                "semantics": semantics,
            }
            self._validate_rule(rule)
            rules.append(rule)

        if not rules:
            raise ValueError("rules_text.md 未解析到有效规则，请检查格式")
        return {"release_id": "TEXT_INPUT", "rules": rules}

    def run(self) -> None:
        ensure_dirs()
        text_input_path = INPUT_DIR / "rules_text.md"
        if text_input_path.exists():
            text_content = text_input_path.read_text(encoding="utf-8").strip()
            if "规则ID：" in text_content:
                output = self._parse_text_rules(text_content)
                output_path = GENERATED_DIR / "rules_parsed.json"
                write_json(output_path, output)
                print(f"[parse] 从 rules_text.md 解析完成，输出: {output_path}")
                return

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
