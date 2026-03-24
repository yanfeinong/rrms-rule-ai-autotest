# RRMS Rule AI Autotest 实施清单

最后更新时间：2026-03-24
维护规则：每次实施步骤有变化，必须同步更新本文件。

## 当前目标（MVP）

实现最小闭环：
1. 输入多条文字规则
2. 指定目标 Hive 测试库
3. 自动设计测试案例与测试表结构
4. 自动生成测试数据
5. 自动调用规则校验 API
6. 自动比对结果并输出测试报告

## 里程碑状态

- [x] M0-01 新建独立项目目录
- [x] M0-02 初始化基础目录结构（config/input/src/generated/reports/scripts）
- [x] M0-03 初始化 Git 仓库
- [x] M0-04 初始化 Python 项目基础文件

## 详细步骤清单

### M1 输入与配置

- [x] M1-01 定义规则输入文件格式（`input/rules_input.yaml`）
- [x] M1-02 定义本地环境配置（`config/env.local.yaml`）
- [x] M1-03 定义内网环境配置（`config/env.intra.yaml`）
- [x] M1-04 定义本地 API 配置（`config/api.local.yaml`）
- [x] M1-05 定义内网 API 配置（`config/api.intra.yaml`）

### M2 核心模块开发

- [x] M2-01 `RuleTextParser`：文字规则转结构化规则
- [x] M2-02 `CaseGenerator`：生成通过/失败/边界场景
- [x] M2-03 `SchemaBuilder`：按规则集合设计测试表结构与 DDL
- [x] M2-04 `DataGenerator`：生成测试数据 SQL
- [x] M2-05 `RuleApiClient`：触发执行与查询结果（支持 local mock_mode）
- [x] M2-06 `ResultComparator`：预期值与实际值比对
- [x] M2-07 `ReportBuilder`：生成 `report.md` 和 `report.json`

### M3 编排与运行

- [x] M3-01 实现统一入口（`run.py`）
- [x] M3-02 支持单步骤执行（`--step`）
- [x] M3-03 支持一键全量执行（`--all`）
- [x] M3-04 增加 `--env`、`--release`、`--biz-date` 参数
- [x] M3-05 增加 `--no-llm` 降级模式

### M4 验证与交付

- [x] M4-01 使用 1 条规则跑通本地冒烟
- [x] M4-02 使用 3-10 条规则跑通批量执行
- [x] M4-03 生成首版测试报告样例
- [x] M4-04 预留内网 CI 接入脚本与说明

## 变更记录

- 2026-03-24：创建实施清单与基础目录结构。
- 2026-03-24：完成项目骨架初始化、配置模板与运行入口。
- 2026-03-24：完成 Git 初始化，落地规则解析/用例生成/DDL 生成/测试数据生成，并已本地验证通过。
- 2026-03-24：完成 API 调用、结果比对、报告生成模块，实现本地 mock 全流程跑通。
- 2026-03-24：扩展为 4 条规则批量执行并验证通过，新增 CI 脚本与接入文档。
- 2026-03-24：修复 IsNotNullComb 组合非空规则，支持多字段解析、组合场景用例、DDL 多列与多列造数。
- 2026-03-24：补充 IsNotNullComb 空值边界场景（''、NULL、'NULL'、' '），并支持生成真实 NULL SQL。
- 2026-03-24：抽取非空类规则通用空值模板，IsNotNull 与 IsNotNullComb 自动继承空值边界场景。
- 2026-03-24：非空模板改为按 semantics 动态取值，并修正优先覆盖 '' 与 ' ' 场景。
- 2026-03-24：接入 customExec 规则执行接口，支持按规则逐条触发并按 biz_date 传参。
- 2026-03-24：新增运行手册 docs/RUNBOOK.md，统一维护启动与触发命令。
- 2026-03-24：新增自然语言规则入口 input/rules_text.md，parse 支持文本规则优先解析。
- 2026-03-24：文本规则支持不填写对象信息，自动从表达式推断字段并生成测试表名。
