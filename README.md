# 📈 自動暗号資産トレーディング戦略 － 日利 +1% を目指すバックテスト検証




## 🧠 プロジェクト概要
このリポジトリでは、Pythonベースで構築した自動売買戦略の検証を行います。
目標は、複利ベースで日利 +1%（年利 +3780%） を達成できるロジックを構築・シミュレーションすることです。
対象は Bybit のUSDT建て銘柄で、シンプルかつ実用性の高い戦略を目指します。

## 🎯 目的
自動売買戦略のENTRY/EXITロジックをPythonで実装

1年間の複利ベースのバックテストを実施

以下の条件を満たす戦略を検証：

年間収益：3780%以上

手数料（往復0.12%）とスリッページ込み

勝率・最大ドローダウン・最終利益・収益曲線の出力

過剰最適化を避けた、再現可能なロジック

## 🛠 使用技術
Python

pandas / numpy / matplotlib / ta（テクニカル分析）

検証環境

Google Colab / Jupyter Notebook / ローカルPC（任意）

サポート可能

バックテストツール（Freqtradeなど）

シミュレーション用のBOTスクリプト

TP/SL/トレーリング設定

## ✅ 成果物
ENTRY/EXIT条件を記述したPythonコード（コメント付き）

複利ベースのバックテスト結果

勝率 / トレード数 / 最大ドローダウン（％）/ 年間リターン

エクイティカーブと統計レポート付きグラフ

使用したインジケーターや戦略の説明資料（日本語）
![Equity Curve](https://raw.githubusercontent.com/Sasu8823/bybit_strategy_project/main/results/1pct_per_day_equity_curve.png)
![Equity Curve](https://github.com/Sasu8823/bybit_strategy_project/blob/main/results/advanced_strategy_results.png)
## ⚠ 注意事項
グラフや収益の捏造は禁止

過学習による実運用で使えない戦略は不採用

ロジックは再現可能かつ安定性重視

## 📌 このプロジェクトの目的
「寝ていても利益が出る」完全自動売買BOTの戦略部分を見つけることが目的です。
BOT本体はすでに完成しており、有効な戦略が見つかれば即運用に入ります。
日利+1%を目指す本気の検証に挑戦します。
