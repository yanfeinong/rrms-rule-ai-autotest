from src.common import GENERATED_DIR, ensure_dirs, read_json


class DataGenerator:
    def _build_row_select(
        self,
        case_id: str,
        row_id: int,
        target_fields: list[str],
        row_data: dict[str, object],
        expected_pass: int,
        reason: str,
    ) -> str:
        columns = [f"'{case_id}'", str(row_id)]
        for field in target_fields:
            value = row_data.get(field, "")
            if value is None:
                columns.append("NULL")
            else:
                safe_value = str(value).replace("'", "''")
                columns.append(f"'{safe_value}'")
        columns.append(str(expected_pass))
        columns.append(f"'{reason}'")
        return "SELECT " + ", ".join(columns)

    def run(self) -> None:
        ensure_dirs()
        payload = read_json(GENERATED_DIR / "cases_generated.json")
        sql_lines: list[str] = ["-- 自动生成测试数据 SQL"]

        for rule_item in payload.get("rule_cases", []):
            table_name = f"rt_{rule_item['source_table']}"
            target_fields = rule_item.get("target_fields", [rule_item["target_field"]])
            for case in rule_item["cases"]:
                selects: list[str] = []
                reason = case["scenario"].replace("'", "''")

                if "sample_rows" in case:
                    sample_rows = case["sample_rows"]
                    for idx, row_data in enumerate(sample_rows, start=1):
                        selects.append(
                            self._build_row_select(
                                case_id=case["case_id"],
                                row_id=idx,
                                target_fields=target_fields,
                                row_data=row_data,
                                expected_pass=case["expected_pass"],
                                reason=reason,
                            )
                        )
                else:
                    values = case["sample_values"]
                    field = target_fields[0]
                    for idx, value in enumerate(values, start=1):
                        selects.append(
                            self._build_row_select(
                                case_id=case["case_id"],
                                row_id=idx,
                                target_fields=target_fields,
                                row_data={field: value},
                                expected_pass=case["expected_pass"],
                                reason=reason,
                            )
                        )
                sql_lines.append(
                    f"INSERT INTO TABLE {{target_database}}.{table_name} PARTITION (ds='{{biz_date}}')\n"
                    + "\nUNION ALL\n".join(selects)
                    + ";"
                )

        output_path = GENERATED_DIR / "generated_data.sql"
        output_path.write_text("\n\n".join(sql_lines) + "\n", encoding="utf-8")
        print(f"[data] 测试数据生成完成，输出: {output_path}")
