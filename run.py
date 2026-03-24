import argparse
from pathlib import Path

from src.rule_text_parser import RuleTextParser
from src.case_generator import CaseGenerator
from src.schema_builder import SchemaBuilder
from src.data_generator import DataGenerator
from src.rule_api_client import RuleApiClient
from src.result_comparator import ResultComparator
from src.report_builder import ReportBuilder


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="RRMS 规则 AI 自动化测试入口")
    parser.add_argument("--step", choices=["parse", "case", "schema", "data", "execute", "compare", "report"])
    parser.add_argument("--all", action="store_true", help="执行全流程")
    parser.add_argument("--env", default="local", choices=["local", "intra"])
    parser.add_argument("--release", default="R00000000")
    parser.add_argument("--biz-date", default="1970-01-01")
    parser.add_argument("--no-llm", action="store_true", help="禁用大模型，走模板化逻辑")
    return parser


def run_step(step: str, env: str, biz_date: str) -> None:
    if step == "parse":
        RuleTextParser().run()
    elif step == "case":
        CaseGenerator().run()
    elif step == "schema":
        SchemaBuilder().run()
    elif step == "data":
        DataGenerator().run()
    elif step == "execute":
        RuleApiClient(env=env, biz_date=biz_date).run()
    elif step == "compare":
        ResultComparator().run()
    elif step == "report":
        ReportBuilder().run()


def main() -> None:
    args = build_parser().parse_args()
    if not args.step and not args.all:
        raise SystemExit("请指定 --step 或 --all")

    Path("generated").mkdir(exist_ok=True)
    Path("reports").mkdir(exist_ok=True)

    if args.all:
        for step_name in ["parse", "case", "schema", "data", "execute", "compare", "report"]:
            run_step(step_name, args.env, args.biz_date)
        print("全流程执行完成")
        return

    run_step(args.step, args.env, args.biz_date)
    print(f"步骤执行完成: {args.step}")


if __name__ == "__main__":
    main()
