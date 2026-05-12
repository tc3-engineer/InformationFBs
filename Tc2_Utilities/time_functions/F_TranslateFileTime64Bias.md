# F_TranslateFileTime64Bias

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc2_Utilities` |
| Library Version | `2.18.2` |
| Type | `FUNCTION` |
| Category | `Time functions` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_Utilities_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tcplclib_tc2_utilities/10500926731.html |
| Verified | 2026-05-11 ✅ |
| InfoSys-checked | ✅ 2026-05-11 |
| Status | `verified` |
| Example | [`examples/P_Demo_F_TranslateFileTime64Bias.xml`](../examples/P_Demo_F_TranslateFileTime64Bias.xml) |

---

## 1. 功能简述

把输入时间按指定 bias（分钟）做时区偏移：方向由 `toUTC` 决定。可用于 UTC ↔ 本地时间互转。结合 `WEST_EUROPE_TZI` 等时区常量 + 当前夏令时判定可实现完整时区转换。

## 2. 接口定义

### 函数声明

```iecst
FUNCTION F_TranslateFileTime64Bias : T_FILETIME64
VAR_INPUT
    in : T_FILETIME64;
    bias : DINT;
    toUTC : BOOL;
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `in` | `T_FILETIME64` | 待转换的时间 |
| `bias` | `DINT` | UTC 与本地时间的差值，单位分钟（允许正负） |
| `toUTC` | `BOOL` | 转换方向。FALSE：UTC → 本地时间，公式 `本地时间 = UTC - bias`；TRUE：本地时间 → UTC，公式 `UTC = 本地时间 + bias` |

### 返回值

`T_FILETIME64` —— 见 §3 行为说明。

### VAR_IN_OUT

无。

## 3. 行为说明

函数对 `T_FILETIME64`（100ns 单位的 64 位时间戳）做加减 `bias × 60 × 10000000` 操作。

`bias` 由调用方提供，单位分钟，可正可负。`toUTC` 决定加还是减：

| `toUTC` | 含义 | 内部公式 |
|---|---|---|
| FALSE | UTC → 本地时间 | `本地 := UTC - bias` |
| TRUE | 本地时间 → UTC | `UTC := 本地 + bias` |

PDF 强调：输入用 `T_FILETIME64` 而非 `DT`，是为了在 online 模式下方便监视。多次连续转换（如 UTC → 本地 → ISO 字符串）建议尽量复用同一 `T_FILETIME64` 中间变量，避免反复格式互转开销。

常见配合：从 `FB_GetTimeZoneInformation` 拿 `ST_TimeZoneInformation`，按 DST 状态选 `bias + daylightBias` 或 `bias + standardBias`。

## 4. 错误码 / 返回值

返回类型 `T_FILETIME64`。函数语义详见 §3。某些 FC（返回 `WORD` / `T_FILETIME64` / `TOD` 的）以 0 作为「参数错误」哨兵值——调用方必须先检查 > 0；具体见 §5 使用注意。

## 5. 使用注意 / 常见坑

- **`bias` 单位是分钟，不是秒、不是小时**：德国（CET）= 60、（CEST）= 120、北京 = -480（注意负号）。
- **`toUTC` 方向不要搞反**：错误方向会得到双倍偏移的错误时间。
- **夏令时切换时段的 bias 不固定**：必须根据当前 DST 状态动态选择 standardBias 或 daylightBias；硬编码会在切换周出错。
- **输入是 `T_FILETIME64` 不是 `DT`**：PDF 解释是为了 online 可视化便利；想用 `DT` 输入须先 `DT_TO_FILETIME64` 再调用本 FC。

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_F_TranslateFileTime64Bias.xml`](../examples/P_Demo_F_TranslateFileTime64Bias.xml)
>
> 导入步骤：右键 PLC 项目 → Import PLCopenXML → 选该文件 → OK
> 详见 [`examples/README.md`](../examples/README.md)

```iecst
out := FILETIME64_TO_DT(F_TranslateFileTime64Bias(DT_TO_FILETIME64(in), bias, bToUTC));
```

完整可导入例程见上方链接，里面有 场景 / 价值 / 验证步骤 三件套注释。

## 7. 业务场景与实际价值

- **场景**：跨时区日志：PLC 用 UTC 记时间戳避免 DST 跳点，HMI 显示要切到操作员所在时区；或者 PLC 接收 NTP / 浏览器送来的本地时间想换算回 UTC 落盘。
- **价值**：1 行调用完成时区偏移；比手写 `fileTime - bias * 600000000` 安全（不会写错 100ns 系数 600000000）。
- **替代方案对比**：手写常量计算（容易写错系数）/ 用 `FB_SystemTimeToTzSpecificLocalTime`（更全但开销大、用 `TIMESTRUCT` 而非 `T_FILETIME64`）/ 调用本 FC（轻量、明确）。

## 8. 参考资料

- **PDF**：[TwinCAT_3_PLC_Lib_Tc2_Utilities_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_Utilities_EN.pdf) §4.1.10
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tcplclib_tc2_utilities/10500926731.html
- **相关函数**：见 [`Tc2_Utilities README`](../README.md)（同类 time functions）
