from src.common import GENERATED_DIR, ensure_dirs, read_json


class SchemaBuilder:
    def run(self) -> None:
        ensure_dirs()
        parsed = read_json(GENERATED_DIR / "rules_parsed.json")
        rules = parsed.get("rules", [])

        ddl_lines: list[str] = ["-- 自动生成测试表 DDL"]
        table_fields: dict[str, set[str]] = {}
        for rule in rules:
            table_name = f"rt_{rule['source_table']}"
            fields = rule.get("target_fields", [rule["target_field"]])
            table_fields.setdefault(table_name, set()).update(fields)

        for table_name, fields in table_fields.items():
            field_defs = "\n".join([f"  {name} STRING COMMENT '规则目标字段'," for name in sorted(fields)])
            ddl_lines.append(
                f"""
CREATE TABLE IF NOT EXISTS {{target_database}}.{table_name} (
  case_id STRING COMMENT '测试用例ID',
  row_id BIGINT COMMENT '行号',
{field_defs}
  expected_pass INT COMMENT '预期是否通过:1是0否',
  expected_reason STRING COMMENT '预期原因'
)
PARTITIONED BY (ds STRING)
STORED AS PARQUET;
""".strip()
            )

        output_path = GENERATED_DIR / "generated_ddl.sql"
        output_path.write_text("\n\n".join(ddl_lines) + "\n", encoding="utf-8")
        print(f"[schema] 测试表结构生成完成，输出: {output_path}")
