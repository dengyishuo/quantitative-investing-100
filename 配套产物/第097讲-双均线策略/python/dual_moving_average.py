#!/usr/bin/env python3
"""双均线策略的 Python 课程产物。仅用于研究教学。"""

from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="运行无前视偏差的双均线策略")
    parser.add_argument("--input", default="input/price.csv")
    parser.add_argument("--daily-output", default="output/python_daily.csv")
    parser.add_argument("--metrics-output", default="output/python_metrics.csv")
    parser.add_argument("--short", type=int, default=20)
    parser.add_argument("--long", type=int, default=60)
    parser.add_argument("--fee", type=float, default=0.0005)
    parser.add_argument("--periods", type=int, default=252)
    return parser.parse_args()


def load_prices(path: str, long_window: int) -> pd.DataFrame:
    df = pd.read_csv(path)
    missing = {"date", "close"} - set(df.columns)
    if missing:
        raise ValueError(f"输入缺少字段: {sorted(missing)}")

    df = df.loc[:, ["date", "close"]].copy()
    df["date"] = pd.to_datetime(df["date"], errors="raise")
    df["close"] = pd.to_numeric(df["close"], errors="raise")
    df = df.sort_values("date").drop_duplicates("date", keep="first")
    df = df.reset_index(drop=True)

    if df["close"].isna().any() or (df["close"] <= 0).any():
        raise ValueError("close 必须为非缺失的正数")
    if len(df) < long_window:
        raise ValueError(f"数据至少需要 {long_window} 行")
    return df


def run_strategy(
    df: pd.DataFrame, short_window: int, long_window: int, fee: float
) -> pd.DataFrame:
    result = df.copy()
    result["ret"] = result["close"].pct_change(fill_method=None)
    result["ma_short"] = result["close"].rolling(short_window).mean()
    result["ma_long"] = result["close"].rolling(long_window).mean()

    result["signal"] = (result["ma_short"] > result["ma_long"]).astype(float)
    result["position"] = result["signal"].shift(1).fillna(0.0)
    result["turnover"] = result["position"].diff().abs().fillna(0.0)
    result["strategy_ret"] = (
        result["position"] * result["ret"] - fee * result["turnover"]
    ).fillna(0.0)
    result["equity"] = (1.0 + result["strategy_ret"]).cumprod()
    return result


def calculate_metrics(result: pd.DataFrame, periods: int) -> pd.DataFrame:
    n = len(result)
    total_return = result["equity"].iloc[-1] - 1.0
    ann_return = result["equity"].iloc[-1] ** (periods / n) - 1.0
    ann_vol = result["strategy_ret"].std(ddof=1) * periods**0.5
    sharpe = (
        result["strategy_ret"].mean() * periods / ann_vol
        if ann_vol > 0
        else float("nan")
    )
    peak = result["equity"].cummax()
    max_drawdown = (result["equity"] / peak - 1.0).min()
    return pd.DataFrame(
        {
            "metric": [
                "total_return",
                "ann_return",
                "ann_vol",
                "sharpe",
                "max_drawdown",
            ],
            "value": [total_return, ann_return, ann_vol, sharpe, max_drawdown],
        }
    )


def ensure_parent(path: str) -> None:
    Path(path).parent.mkdir(parents=True, exist_ok=True)


def main() -> None:
    args = parse_args()
    if not 0 < args.short < args.long:
        raise ValueError("窗口必须满足 0 < short < long")
    if args.fee < 0 or args.periods <= 0:
        raise ValueError("fee 必须非负，periods 必须为正")

    prices = load_prices(args.input, args.long)
    result = run_strategy(prices, args.short, args.long, args.fee)
    metrics = calculate_metrics(result, args.periods)

    ensure_parent(args.daily_output)
    ensure_parent(args.metrics_output)
    result.to_csv(args.daily_output, index=False, float_format="%.15g")
    metrics.to_csv(args.metrics_output, index=False, float_format="%.15g")
    print(metrics.to_string(index=False))


if __name__ == "__main__":
    main()

