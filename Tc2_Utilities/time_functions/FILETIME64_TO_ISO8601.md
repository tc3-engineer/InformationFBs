# FILETIME64_TO_ISO8601

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc2_Utilities` |
| Library Version | `2.18.2` |
| Type | `FUNCTION` |
| Category | `Time functions` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_Utilities_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tcplclib_tc2_utilities/10686718475.html |
| Verified | 2026-05-11 ✅ |
| InfoSys-checked | ✅ 2026-05-11 |
| Status | `verified` |
| Example | [`examples/P_Demo_FILETIME64_TO_ISO8601.TcPOU`](../examples/P_Demo_FILETIME64_TO_ISO8601.TcPOU) |

---

## 1. 功能简述

把 `T_FILETIME64` 时间格式化为 **ISO 8601 字符串**：`YYYY-MM-DDThh:mm:ss.xxxTZD`。带时区指示符 TZD（Z = UTC，或 ±hh:mm 的偏移），秒可显示 0 ~ 9 位小数。常用于日志记录、JSON 时间字段、跨系统时间交换。

## 2. 接口定义

### 函数声明

```iecst
FUNCTION FILETIME64_TO_ISO8601 : STRING(39)
VAR_INPUT
    fileTime : T_FILETIME64;
    nBias : INT;
    bUTC : BOOL;
    nPrecision : USINT(0..9);
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `fileTime` | `T_FILETIME64` | 待转换的 `T_FILETIME64` 时间 |
| `nBias` | `INT` | UTC 与本地时间的差值，分钟。公式：`UTC = 本地时间 + nBias` |
| `bUTC` | `BOOL` | 输入是 UTC 时间还是本地时间。TRUE = 输入是 UTC，FALSE = 输入是本地时间 |
| `nPrecision` | `USINT(0..9)` | 秒的小数位精度（0 ~ 9 位，9 = 纳秒） |

### 返回值

`STRING(39)` —— 见 §3 行为说明。

### VAR_IN_OUT

无。

## 3. 行为说明

ISO 8601 时间格式约定：

- `YYYY-MM-DD` 日期部分（4-2-2 位数字，`-` 分隔）
- `T` 分隔符（必须大写 T）
- `hh:mm:ss` 时间部分（24 小时制，`:` 分隔）
- `.xxx` 秒的小数部分（`nPrecision` 位，0 表示无小数）
- `TZD` 时区指示符：`Z` = UTC、`+hh:mm` / `-hh:mm` = 与 UTC 的偏移

函数按 `bUTC` 决定输出 TZD：若 `bUTC = TRUE` 输出 `Z`；若 `bUTC = FALSE` 按 `nBias` 计算并输出 `+02:00` 之类的偏移字符串。

返回 `STRING(39)` 是为了能容纳 9 位小数 + 时区的最长形式。

无错误码：输入 `T_FILETIME64` 超出公历可表示范围会得到无意义但格式正确的字符串。


本 FC 在工程中常作为日志 / 通讯接口的输出端：把 PLC 内部的 `T_FILETIME64` 时间戳一次性转成标准化、可被任何文本工具解析的 ISO 8601 字符串；前后衔接 `F_GetCurDateTime` 取时间、`fb_write_file` 写日志，构成一条完整的日志管线。

## 4. 错误码 / 返回值

返回类型 `STRING(39)`。函数无错误码 / 无 HRESULT；任意合法类型输入都有定义良好的返回值。详细边界与失败行为见 §5。

## 5. 使用注意 / 常见坑

- **`nBias` 用分钟、有正负**：UTC = 本地 + bias，所以东 8 区中国是 nBias = -480（注意负号），不是 +480。
- **`bUTC` 与 `nBias` 关系**：如果 `bUTC = TRUE`，`nBias` 仅决定 TZD 显示文本（Z），不影响日期 / 时间部分；如果 `bUTC = FALSE`，函数假设 `fileTime` 是本地时间，TZD 直接按 `nBias` 取反输出。
- **`nPrecision = 0` 时不输出小数点**：「2026-05-11T12:00:00Z」；`nPrecision = 3` → 「2026-05-11T12:00:00.123Z」。
- **长度 39 字节够用**：最长形如「YYYY-MM-DDThh:mm:ss.123456789+12:34」（35 字符），留 4 字节余量。
- **版本要求 ≥ 3.3.46.0**：较新的 Tc2_Utilities 版本才有，旧版需先升库。

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_FILETIME64_TO_ISO8601.TcPOU`](../examples/P_Demo_FILETIME64_TO_ISO8601.TcPOU)
>
> 导入步骤：右键 PLC 项目下 POUs 文件夹 → Add → Existing Item → 选该文件 → OK
> 详见 [`examples/README.md`](../examples/README.md)

```iecst
sISO := FILETIME64_TO_ISO8601(fileTime := ft, nBias := 0, bUTC := TRUE, nPrecision := 3);
```

完整可导入例程见上方链接，里面有 场景 / 价值 / 验证步骤 三件套注释。

## 7. 业务场景与实际价值

- **场景**：REST API / MQTT / JSON 接口要求时间字段用 ISO 8601；或者日志文件归档需要可被任何文本工具按字典序排序的时间戳格式。
- **价值**：1 行拿到 ISO 8601 字符串，连时区指示符、小数位都一起处理；手写至少要 sprintf + 拼接 + DST 判定 30+ 行代码。
- **替代方案对比**：手写 `SYSTEMTIME_TO_STRING` + 拼字符串（无 TZD、格式不够 ISO）/ 用 `DT_TO_STRING` + 加 T 加 Z（精度不足）/ 调用本 FC（推荐）。

## 8. 参考资料

- **PDF**：[TwinCAT_3_PLC_Lib_Tc2_Utilities_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_Utilities_EN.pdf) §4.1.13
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tcplclib_tc2_utilities/10686718475.html
- **相关函数**：见 [`Tc2_Utilities README`](../README.md)（同类 time functions）
