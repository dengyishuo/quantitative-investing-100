#!/usr/bin/env Rscript

# 双均线策略的 R 课程产物。仅用于研究教学。

args <- commandArgs(trailingOnly = TRUE)

get_arg <- function(flag, default) {
  index <- which(args == flag)
  if (length(index) == 0L) {
    return(default)
  }
  index <- index[[1L]]
  if (index == length(args)) {
    stop(paste(flag, "后缺少参数值"))
  }
  args[[index + 1L]]
}

input_path <- get_arg("--input", "input/price.csv")
daily_output <- get_arg("--daily-output", "output/r_daily.csv")
metrics_output <- get_arg("--metrics-output", "output/r_metrics.csv")
short_window <- as.integer(get_arg("--short", "20"))
long_window <- as.integer(get_arg("--long", "60"))
fee <- as.numeric(get_arg("--fee", "0.0005"))
periods <- as.integer(get_arg("--periods", "252"))

if (!is.finite(short_window) || !is.finite(long_window) ||
    short_window <= 0L || short_window >= long_window) {
  stop("窗口必须满足 0 < short < long")
}
if (!is.finite(fee) || fee < 0 || !is.finite(periods) || periods <= 0L) {
  stop("fee 必须非负，periods 必须为正")
}

df <- read.csv(input_path, stringsAsFactors = FALSE)
missing_columns <- setdiff(c("date", "close"), names(df))
if (length(missing_columns) > 0L) {
  stop(paste("输入缺少字段:", paste(missing_columns, collapse = ", ")))
}

df <- df[, c("date", "close")]
df$date <- as.Date(df$date)
df$close <- as.numeric(df$close)
df <- df[order(df$date), ]
df <- df[!duplicated(df$date), ]
row.names(df) <- NULL

if (anyNA(df$date) || anyNA(df$close) || any(!is.finite(df$close)) ||
    any(df$close <= 0)) {
  stop("date 必须有效，close 必须为非缺失的正数")
}
if (nrow(df) < long_window) {
  stop(paste("数据至少需要", long_window, "行"))
}

roll_mean <- function(x, n) {
  as.numeric(stats::filter(x, rep(1 / n, n), sides = 1))
}

df$ret <- c(NA_real_, diff(df$close) / head(df$close, -1L))
df$ma_short <- roll_mean(df$close, short_window)
df$ma_long <- roll_mean(df$close, long_window)
df$signal <- as.numeric(df$ma_short > df$ma_long)
df$signal[is.na(df$signal)] <- 0

# t 日收盘后才知道 signal，因此 t+1 日的仓位滞后一日。
df$position <- c(0, head(df$signal, -1L))
df$turnover <- c(0, abs(diff(df$position)))
df$strategy_ret <- df$position * df$ret - fee * df$turnover
df$strategy_ret[is.na(df$strategy_ret)] <- 0
df$equity <- cumprod(1 + df$strategy_ret)

n <- nrow(df)
total_return <- tail(df$equity, 1) - 1
ann_return <- tail(df$equity, 1)^(periods / n) - 1
ann_vol <- stats::sd(df$strategy_ret) * sqrt(periods)
sharpe <- if (is.finite(ann_vol) && ann_vol > 0) {
  mean(df$strategy_ret) * periods / ann_vol
} else {
  NA_real_
}
peak <- cummax(df$equity)
max_drawdown <- min(df$equity / peak - 1)

metrics <- data.frame(
  metric = c(
    "total_return",
    "ann_return",
    "ann_vol",
    "sharpe",
    "max_drawdown"
  ),
  value = c(total_return, ann_return, ann_vol, sharpe, max_drawdown),
  stringsAsFactors = FALSE
)

dir.create(dirname(daily_output), recursive = TRUE, showWarnings = FALSE)
dir.create(dirname(metrics_output), recursive = TRUE, showWarnings = FALSE)
write.csv(df, daily_output, row.names = FALSE, na = "")
write.csv(metrics, metrics_output, row.names = FALSE, na = "")
print(metrics, row.names = FALSE)

