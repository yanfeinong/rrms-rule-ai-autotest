# RRMS Rule AI Autotest 运行手册

最后更新时间：2026-03-24
维护规则：后续所有启动命令、触发命令、执行步骤统一维护在本文件。

## 1. 基础说明

- 项目目录：`/Users/lizijie/yanfei-project/yanfeinong-projects/rrms-rule-ai-autotest`
- 默认入口：`run.py`
- 支持环境：`local` / `intra`

## 2. 常用命令

### 2.1 单步骤执行

```bash
python3 run.py --step parse --env local --biz-date 2026-03-19
python3 run.py --step case --env local --biz-date 2026-03-19
python3 run.py --step schema --env local --biz-date 2026-03-19
python3 run.py --step data --env local --biz-date 2026-03-19
python3 run.py --step execute --env local --biz-date 2026-03-19
python3 run.py --step compare --env local --biz-date 2026-03-19
python3 run.py --step report --env local --biz-date 2026-03-19
```

### 2.2 一键全流程

```bash
python3 run.py --all --env local --release R20260324 --biz-date 2026-03-19
```

## 3. 规则执行 API 触发命令

### 3.1 内网真实触发（customExec）

执行前需要准备：
- `config/api.intra.yaml` 已配置 customExec 地址
- 环境变量 `RULE_API_TOKEN`（如接口要求鉴权）

```bash
python3 run.py --step parse --env intra --biz-date 2026-03-19
python3 run.py --step case --env intra --biz-date 2026-03-19
python3 run.py --step execute --env intra --biz-date 2026-03-19
```

触发结果文件：
- `generated/api_execution_result.json`

## 4. CI 脚本命令

### 4.1 本地流水线

```bash
bash scripts/ci_local.sh
```

### 4.2 内网流水线

```bash
export RULE_API_TOKEN=your_token
bash scripts/ci_intra.sh
```

## 5. 常见产物路径

- 规则解析结果：`generated/rules_parsed.json`
- 测试案例：`generated/cases_generated.json`
- 测试表结构：`generated/generated_ddl.sql`
- 测试数据：`generated/generated_data.sql`
- API 触发结果：`generated/api_execution_result.json`
- 比对结果：`generated/comparison_result.json`
- 测试报告：`reports/report.md`、`reports/report.json`

## 6. 后续补充约定

后续新增以下类型信息时，必须追加到本文件：
- 新增启动命令
- 新增环境变量
- 新增执行入口
- 新增 CI 触发方式
- 新增排障命令
