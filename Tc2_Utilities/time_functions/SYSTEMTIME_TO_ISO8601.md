# SYSTEMTIME_TO_ISO8601

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc2_Utilities` |
| Library Version | `2.18.2` |
| Type | `FUNCTION` |
| Category | `Time functions` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_Utilities_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tcplclib_tc2_utilities/10686615819.html |
| Verified | 2026-05-11 ✅ |
| InfoSys-checked | ✅ 2026-05-11 |
| Status | `verified` |
| Example | [`examples/P_Demo_SYSTEMTIME_TO_ISO8601.TcPOU`](../examples/P_Demo_SYSTEMTIME_TO_ISO8601.TcPOU) |

---

## 1. 功能简述

把 `TIMESTRUCT` 格式化为 ISO 8601 字符串 `YYYY-MM-DDThh:mm:ss.xxxTZD`。`TZD` 为 `Z`（UTC）或 `±hh:mm`（本地时间的偏移）。本 FC 与 `FILETIME64_TO_ISO8601` 输出格式一致，差别只是输入类型。

## 2. 接口定义

### 函数声明

```iecst
FUNCTION SYSTEMTIME_TO_ISO8601 : STRING(39)
VAR_INPUT
    systemTime : TIMESTRUCT;
    nBias : INT;
    bUTC : BOOL;
    nPrecision : USINT(0..9);
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `systemTime` | `TIMESTRUCT` | 输入时间（系统时间结构体格式） |
| `nBias` | `INT` | UTC 与本地时间的差值，分钟。`UTC = 本地时间 + nBias` |
| `bUTC` | `BOOL` | 输入是 UTC 还是本地时间 |
| `nPrecision` | `USINT(0..9)` | 秒的小数位精度（0 ~ 9 位） |

### 返回值

`STRING(39)` —— 见 §3 行为说明。

### VAR_IN_OUT

无。

## 3. 行为说明

ISO 8601 格式规则（同 `FILETIME64_TO_ISO8601`）：日期 `YYYY-MM-DD`，T 大写分隔，时间 `hh:mm:ss[.xxx]`，TZD 为 `Z`（bUTC=TRUE 时）或 `±hh:mm`（按 nBias 派生）。

`nPrecision` 控制秒后小数位数：0 不输出小数点，1 ~ 9 输出对应位数（注意 `TIMESTRUCT.wMilliseconds` 精度只到 3 位，更高位会被零填充）。

返回 `STRING(39)`，足够容纳最长形式「YYYY-MM-DDThh:mm:ss.123456789+12:34」。

版本要求：Tc2_Utilities ≥ 3.3.46.0。


本 FC 与 `FILETIME64_TO_ISO8601` 的区别只在输入类型——前者吃 `TIMESTRUCT`、后者吃 `T_FILETIME64`，输出格式完全相同。工程中如果数据来源已经是 `TIMESTRUCT`（如从 `FB_LocalSystemTime` 输出），直接用本 FC 更省一次类型转换；如果是 `T_FILETIME64`（如 Windows 日志时间戳）则用 `FILETIME64_TO_ISO8601` 更直接。

## 4. 错误码 / 返回值

返回类型 `STRING(39)`。函数无错误码 / 无 HRESULT；任意合法类型输入都有定义良好的返回值。详细边界与失败行为见 §5。

## 5. 使用注意 / 常见坑

- **nPrecision > 3 会零填充**：`TIMESTRUCT` 只到毫秒，`nPrecision = 6` 时多余 3 位为 「000」（不是真实纳秒）。
- **bUTC 与 nBias 关系同 `FILETIME64_TO_ISO8601`**：bUTC = TRUE 时 TZD 固定为 `Z`，nBias 仅在 bUTC = FALSE 时影响 TZD 输出。
- **中国时区写法**：北京时间（本地时间）+ nBias = -480 + bUTC = FALSE → 输出 「...+08:00」（因为 UTC = 本地 + (-480) → 本地比 UTC 早 480 分钟 = +8 小时）。
- **与 `SYSTEMTIME_TO_STRING` 区别**：`SYSTEMTIME_TO_STRING` 输出 「YYYY-MM-DD-hh:mm:ss.xxx」（用 `-` 分隔日期和时间，无 TZD），本 FC 输出标准 ISO 8601（用 `T` 分隔，带 TZD）。

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_SYSTEMTIME_TO_ISO8601.TcPOU`](../examples/P_Demo_SYSTEMTIME_TO_ISO8601.TcPOU)
>
> 导入步骤：右键 PLC 项目下 POUs 文件夹 → Add → Existing Item → 选该文件 → OK
> 详见 [`examples/README.md`](../examples/README.md)

```iecst
sISO := SYSTEMTIME_TO_ISO8601(systemTime, nBias := 0, bUTC := TRUE, nPrecision := 3);
```

完整可导入例程见上方链接，里面有 场景 / 价值 / 验证步骤 三件套注释。

## 7. 业务场景与实际价值

- **场景**：MQTT / OPC UA / REST API 推送时间字段；或者要求时间戳「按字典序排序就是按时间排序」的日志归档（ISO 8601 是这种特性的标准）。
- **价值**：1 行调用得到带时区的标准时间字符串；手写要拼字符串 + 处理 TZD 计算 + DST 判定 50+ 行。
- **替代方案对比**：走 `SYSTEMTIME_TO_FILETIME64` + `FILETIME64_TO_ISO8601`（多 1 步）/ 手写 ISO 拼字符串（容易出错）/ 调用本 FC（推荐）。

## 8. 参考资料

- **PDF**：[TwinCAT_3_PLC_Lib_Tc2_Utilities_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_Utilities_EN.pdf) §4.1.20
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tcplclib_tc2_utilities/10686615819.html
- **相关函数**：见 [`Tc2_Utilities README`](../README.md)（同类 time functions）
