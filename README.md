# rrms-rule-ai-autotest

规则自动化测试最小闭环项目（MVP）。

## MVP 流程

1. 读取文字规则与环境配置
2. 生成测试案例与测试表结构
3. 生成测试数据 SQL
4. 调用规则校验 API
5. 比对预期与实际结果
6. 输出测试报告

## 目录结构

- `config/` 环境与 API 配置
- `input/` 规则输入
- `src/` 核心代码
- `generated/` 自动生成 SQL
- `reports/` 执行报告
- `scripts/` 预留脚本

## 快速开始

```bash
python3 run.py --step parse --env local
python3 run.py --all --env local --release R20260324 --biz-date 2026-03-24
```

## CI

- 本地 CI 脚本：`bash scripts/ci_local.sh`
- 内网 CI 脚本：`bash scripts/ci_intra.sh`
- 详细说明：`docs/CI_INTEGRATION.md`
