# CI 接入说明

## 本地流水线

```bash
bash scripts/ci_local.sh
```

支持环境变量：
- `RELEASE_ID`
- `BIZ_DATE`

## 内网流水线

```bash
export RULE_API_TOKEN=your_token
bash scripts/ci_intra.sh
```

支持环境变量：
- `RELEASE_ID`
- `BIZ_DATE`
- `RULE_API_TOKEN`（必填）

## 建议 CI 阶段

1. 安装依赖
2. 执行脚本（local/intra）
3. 归档 `reports/` 与 `generated/`
