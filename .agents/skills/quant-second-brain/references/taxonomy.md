# Quantitative Finance Domain Entity Taxonomy

This reference specifies the 10 core entity classes and typed relationships used across the Quantitative Finance Knowledge Base.

## Entity Classes

1. **`Strategy:`**: Systematic trading rules, alpha signals, execution logic (e.g. `Strategy:Delta_Engine`, `Strategy:MFIN_Crypto_Momentum`).
2. **`Model:`**: Mathematical, neural network, or stochastic models (e.g. `Model:Deep_Inception_Network`, `Model:Heston_Stochastic_Volatility`).
3. **`Formula:`**: Objective functions, loss functions, stochastic equations (e.g. `Formula:Sharpe_Ratio_Objective`, `Formula:Copula_Dependency`).
4. **`Regime:`**: Environmental market conditions (e.g. `Regime:High_Volatility_Crypto`, `Regime:Bear_Market_2022`).
5. **`AssetClass:`**: Instruments and market sectors (e.g. `AssetClass:Cryptocurrency`, `AssetClass:FX_Derivatives`).
6. **`Metric:`**: Risk and performance measures (e.g. `Metric:Sharpe_Ratio`, `Metric:Max_Drawdown_99`).
7. **`Indicator:`**: Signal inputs (e.g. `Indicator:Exponential_Moving_Average`, `Indicator:ATR_14`, `Indicator:Google_Trends_Volume`).
8. **`Finding:`**: Verified conclusions and backtest results (e.g. `Finding:MFIN_Uncorrelated_Crypto_Sharpe`).
9. **`Dataset:`**: Input features and market data feeds (e.g. `Dataset:Binance_1m_Klines`, `Dataset:Bitcoin_Hashrate`).
10. **`Paper:`**: Canonical paper node derived from arXiv ID or file stem (e.g. `Paper:arXiv:2501.06032`).

## Relationship Types

* `PROPOSES`: `Paper` -> `Strategy` / `Model`
* `EXTENDS`: `Strategy` / `Model` -> Prior `Model` / `Strategy`
* `TESTED_ON`: `Strategy` -> `AssetClass` / `Dataset`
* `USES_FORMULA`: `Paper` / `Strategy` -> `Formula`
* `IN_CATEGORY`: `Paper` -> `Category`
* `AUTHORED_BY`: `Paper` -> `Author`
* `CITES`: `Paper` -> `Paper`
