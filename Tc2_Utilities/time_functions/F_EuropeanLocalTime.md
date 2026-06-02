# F_EuropeanLocalTime

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc2_Utilities` |
| Library Version | `2.18.2` |
| Type | `FUNCTION` |
| Category | `Time functions` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_Utilities_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tcplclib_tc2_utilities/17349225867.html |
| Verified | 2026-05-11 ✅ |
| InfoSys-checked | ✅ 2026-05-11 |
| Status | `verified` |
| Example | [`examples/P_Demo_F_EuropeanLocalTime.TcPOU`](../examples/P_Demo_F_EuropeanLocalTime.TcPOU) |

---

## 1. 功能简述

把 UTC 时间（`TIMESTRUCT` 格式）按欧洲夏令时规则转换为本地时间（`TIMESTRUCT` 格式），并通过 `bDaylightSavingTime` 输出当前是否处于夏令时。**仅适用于欧洲时区**，不能用于其他地区。

## 2. 接口定义

### 函数声明

```iecst
FUNCTION F_EuropeanLocalTime : TIMESTRUCT
VAR_INPUT
    UTC : TIMESTRUCT;
    UTC_Offset : INT;
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `UTC` | `TIMESTRUCT` | UTC 时间（结构化系统时间格式） |
| `UTC_Offset` | `INT` | 时区偏移，单位分钟 |

### VAR_OUTPUT

```iecst
VAR_OUTPUT
    bDaylightSavingTime : BOOL;
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `bDaylightSavingTime` | `BOOL` | TRUE 表示当前处于夏令时（CEST），FALSE 表示标准时间（CET） |

### 返回值

`TIMESTRUCT` —— 见 §3 行为说明。

### VAR_IN_OUT

无。

## 3. 行为说明

函数内置欧洲（CEST/CET）夏令时切换规则——夏令时从 3 月最后一个周日 01:00 UTC 到 10 月最后一个周日 01:00 UTC。函数据此判断输入 UTC 是否落在夏令时区间。

输出的本地时间 = UTC + UTC_Offset/分钟 +（夏令时区间内额外 60 分钟）。同时 `bDaylightSavingTime` 输出反映该判定。

与功能更全的 `FB_SystemTimeToTzSpecificLocalTime`（任意时区）相比，本 FC 的优势是**计算开销小**（不需要传 `ST_TimeZoneInformation` 结构体也不需要 FB 实例），适合小型控制器或者欧洲专用项目。

## 4. 错误码 / 返回值

返回类型 `TIMESTRUCT`。函数无错误码 / 无 HRESULT；任意合法类型输入都有定义良好的返回值。详细边界与失败行为见 §5。

## 5. 使用注意 / 常见坑

- **仅限欧洲**：北美 DST 切换在不同月份（3 月第 2 周日 → 11 月第 1 周日），用本 FC 会得到错误结果。北美 / 全球场景必须用 `FB_SystemTimeToTzSpecificLocalTime`。
- **`UTC_Offset` 用分钟单位**：德国（CET 区）= 60，非 1 也非 3600。常见错误是误用小时数。
- **输入必须是真 UTC**：如果输入已经是本地时间，结果会被二次偏移成毫无意义的时间。
- **夏令时切换日的歧义时间**：10 月切换日 02:00-03:00 本地时间出现两次，函数返回的是切换后那一次（与 Windows 行为一致）。

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_F_EuropeanLocalTime.TcPOU`](../examples/P_Demo_F_EuropeanLocalTime.TcPOU)
>
> 导入步骤：右键 PLC 项目下 POUs 文件夹 → Add → Existing Item → 选该文件 → OK
> 详见 [`examples/README.md`](../examples/README.md)

```iecst
out := F_EuropeanLocalTime(UTC := in, UTC_Offset := 60, bDaylightSavingTime => bSummerTime);
```

完整可导入例程见上方链接，里面有 场景 / 价值 / 验证步骤 三件套注释。

## 7. 业务场景与实际价值

- **场景**：欧洲（德国 / 法国 / 西班牙 / 意大利 ...）现场的 HMI 显示，把 PLC 内部用 UTC 记录的时间戳按当前夏令时规则转成操作员能看懂的本地时间。
- **价值**：无需声明 FB 实例、无需准备 `ST_TimeZoneInformation` 结构体，1 行调用拿到本地时间 + DST 标志；适合在小循环里频繁调用做实时显示。
- **替代方案对比**：用 `FB_SystemTimeToTzSpecificLocalTime`（全球通用但开销大）/ 手写 DST 规则（容易写错欧洲变更日）/ 调用本 FC（欧洲专用最简）。

## 8. 参考资料

- **PDF**：[TwinCAT_3_PLC_Lib_Tc2_Utilities_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_Utilities_EN.pdf) §4.1.3
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tcplclib_tc2_utilities/17349225867.html
- **相关函数**：见 [`Tc2_Utilities README`](../README.md)（同类 time functions）
