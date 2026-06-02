# SYSTEMTIME_TO_FILETIME64

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc2_Utilities` |
| Library Version | `2.18.2` |
| Type | `FUNCTION` |
| Category | `Time functions` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_Utilities_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tcplclib_tc2_utilities/10501106571.html |
| Verified | 2026-05-11 ✅ |
| InfoSys-checked | ✅ 2026-05-11 |
| Status | `verified` |
| Example | [`examples/P_Demo_SYSTEMTIME_TO_FILETIME64.TcPOU`](../examples/P_Demo_SYSTEMTIME_TO_FILETIME64.TcPOU) |

---

## 1. 功能简述

把 `TIMESTRUCT`（毫秒精度）转换为 64 位 `T_FILETIME64`（100ns 精度）。**忽略 wDayOfWeek 字段**；输入年份必须在 1601 ~ 30827 之间。

## 2. 接口定义

### 函数声明

```iecst
FUNCTION SYSTEMTIME_TO_FILETIME64 : T_FILETIME64
VAR_INPUT
    systemTime : TIMESTRUCT;
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `systemTime` | `TIMESTRUCT` | 待转换的 Windows 系统时间结构体 |

### 返回值

`T_FILETIME64` —— 见 §3 行为说明。

### VAR_IN_OUT

无。

## 3. 行为说明

函数按 `TIMESTRUCT` 各字段（年 / 月 / 日 / 时 / 分 / 秒 / 毫秒，**wDayOfWeek 被忽略**）计算自 1601-01-01 UTC 起的 100ns 累计数，结果赋给 `T_FILETIME64`。

返回值 0 表示参数错误（年份越界 / 月日不合法等）；> 0 表示有效的 file time。

与 `FILETIME64_TO_SYSTEMTIME` 互逆——先后调用应能精确还原（包括毫秒，但 100ns 以下精度无意义因为输入只有毫秒）。

版本要求：Tc2_Utilities ≥ 3.3.44.0 + TwinCAT v3.1.4024。

## 4. 错误码 / 返回值

返回类型 `T_FILETIME64`。函数语义详见 §3。某些 FC（返回 `WORD` / `T_FILETIME64` / `TOD` 的）以 0 作为「参数错误」哨兵值——调用方必须先检查 > 0；具体见 §5 使用注意。

## 5. 使用注意 / 常见坑

- **0 = 错误**：必须检查返回值 > 0；PDF 把 0 列为错误，但严格说 0 也是 1601-01-01 00:00:00 这一合法 file time——保险起见调用前自己校验输入合法。
- **`wDayOfWeek` 字段被忽略**：可以填 0，函数不依赖它也不会校验它。
- **年份范围 1601 ~ 30827**：超出此范围视为错误，`TIMESTRUCT` 形式上能表达到 9999 但本 FC 上限更高（30827）。
- **与 `SYSTEMTIME_TO_DT` 行为不同**：本 FC 截断 100ns 以下精度而非四舍五入；毫秒以上完整保留。

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_SYSTEMTIME_TO_FILETIME64.TcPOU`](../examples/P_Demo_SYSTEMTIME_TO_FILETIME64.TcPOU)
>
> 导入步骤：右键 PLC 项目下 POUs 文件夹 → Add → Existing Item → 选该文件 → OK
> 详见 [`examples/README.md`](../examples/README.md)

```iecst
fileTime := SYSTEMTIME_TO_FILETIME64(systemTime);
```

完整可导入例程见上方链接，里面有 场景 / 价值 / 验证步骤 三件套注释。

## 7. 业务场景与实际价值

- **场景**：PLC 接收 HMI 设定的时间（`TIMESTRUCT` 字段形式）后存入数据库；或者跨任务传时间戳——`T_FILETIME64` 比 `TIMESTRUCT` 占空间小且方便做减法算时间差。
- **价值**：1 行调用完成 8 字段结构体到 64 位整数的折算，保留毫秒精度；手写要算 1601 起算 100ns 数 + 闰年判定 + 月长查表。
- **替代方案对比**：用 `SYSTEMTIME_TO_DT` + `DT_TO_FILETIME64`（丢毫秒）/ 手写常量计算（极易错）/ 调用本 FC（推荐）。

## 8. 参考资料

- **PDF**：[TwinCAT_3_PLC_Lib_Tc2_Utilities_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_Utilities_EN.pdf) §4.1.19
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tcplclib_tc2_utilities/10501106571.html
- **相关函数**：见 [`Tc2_Utilities README`](../README.md)（同类 time functions）
