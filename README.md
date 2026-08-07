# 最优传输截面因子

**简体中文** | [English](README.en.md)

> 一句话定位：把点时截面特征视为加权经验分布，用一维单调最优传输构造可审计的股票因子。

## 这是什么

本 Skill 不训练黑盒模型，也不自动搜索任意公式。它把每个交易日的 `date × symbol` 特征截面与严格滞后的历史参考分布比较，输出 Wasserstein-1 距离、个股传输位移、分布压力和质量状态。首版主视角是预先声明行业内传输并做组内中心化，全市场传输只作为独立诊断。

项目配置的 PandaData-compatible 数据源可用于生成标准化输入；这是数据契约描述，不构成任何提供方的官方背书。MCP 不是运行依赖，本仓库不安装、登录、处理凭证或保存 token。

## 快速开始

```bash
python scripts/check_runtime.py
python scripts/normalize_panel.py tests/fixtures/minimal_panel/panel.json --feature feature_a --out /tmp/normalized.json
python scripts/compute_1d_ot.py tests/fixtures/minimal_panel/panel.json --feature feature_a --group-key industry --out /tmp/factor.json
python -m unittest discover -s tests -v
node scripts/validate-qsh-form.mjs SKILL.md
```

## 数学契约

对每个日期和预声明分组：

- 用正权重构造当前和历史 pooled empirical CDF；
- 历史窗口只使用 `< T` 的交易日，默认 252 日，至少 80 个有效日；
- 用 `W1(P,Q) = integral |F_P - F_Q| dx` 计算精确一维距离；
- 将个股当前值的质量中点分位数映射到参考分布，得到 `transport_target` 和 `transport_displacement`；
- 对预声明特征按固定权重组合 `transport_pressure`，缺失特征不动态换权。

传输位移是可证伪研究变量，不代表必然反转或交易方向。

## 边界

本 Skill 不替代 `skill-pandadata-api`、`skill-factor-evaluate`、IC/回测、组合优化、风险模型或数据质量审计；不训练 GNN、TCN、Transformer、Autoencoder，不自动挖掘公式，不使用未来数据，不输出投资建议。

## 状态

当前为 `draft`，registry `validation_level: listed`。Synthetic fixture 只验证算法机制，不代表真实 PandaData 验证。正式运行前必须确认返回 schema、披露可见日、样本切分、标签和成本。

## 许可证

GPL-3.0，见 [LICENSE](LICENSE)。
