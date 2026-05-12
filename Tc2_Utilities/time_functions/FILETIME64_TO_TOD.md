# FILETIME64_TO_TOD

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc2_Utilities` |
| Library Version | `2.18.2` |
| Type | `FUNCTION` |
| Category | `Time functions` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_Utilities_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tcplclib_tc2_utilities/16285524619.html |
| Verified | 2026-05-11 ✅ |
| InfoSys-checked | ✅ 2026-05-11 |
| Status | `verified` |
| Example | [`examples/P_Demo_FILETIME64_TO_TOD.xml`](../examples/P_Demo_FILETIME64_TO_TOD.xml) |

---

## 1. 功能简述

从 `T_FILETIME64` 提取「一天内时间」（Time Of Day，`TOD` 类型，即 00:00:00.000 ~ 23:59:59.999 范围）。失败（fileTime 最高位为 1）时返回 0。

## 2. 接口定义

### 函数声明

```iecst
FUNCTION FILETIME64_TO_TOD : TOD
VAR_INPUT
    fileTime : T_FILETIME64;
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `fileTime` | `T_FILETIME64` | 待转换的 `T_FILETIME64` 时间 |

### 返回值

`TOD` —— 见 §3 行为说明。

### VAR_IN_OUT

无。

## 3. 行为说明

函数计算 `fileTime` 对 86400 秒（一天）取模后的部分，得到当日 00:00:00 起的累计时间，单位毫秒，类型 `TOD`。

`TOD`（TIME_OF_DAY，等价于 `TIME_OF_DAY` 标准 IEC 类型）只表达 24 小时内的时刻，无日期信息。常用于按时间段触发（每天 18:00 启动夜班定时器）。

**失败条件与 `FILETIME64_TO_SYSTEMTIME` 一致**：fileTime 最高位为 1 时返回 0。函数本身无错误码，但 PDF 明确说 0 既可能是「凌晨 00:00:00」也可能是「转换失败」——调用方需先校验输入合理性。

## 4. 错误码 / 返回值

返回类型 `TOD`。函数语义详见 §3。某些 FC（返回 `WORD` / `T_FILETIME64` / `TOD` 的）以 0 作为「参数错误」哨兵值——调用方必须先检查 > 0；具体见 §5 使用注意。

## 5. 使用注意 / 常见坑

- **0 返回值有歧义**：0 既可能表示 「TOD#00:00:00」（合法的一天开始）也可能表示「转换失败」。先用 `FILETIME64_TO_DT` 或独立校验 fileTime 有效再调本 FC 才安全。
- **精度到毫秒**：`TOD` 的精度是毫秒，与 `TIMESTRUCT.wMilliseconds` 一致；100ns 部分被丢弃。
- **配合定时触发**：用 `F_GetCurDateTime()` 拿当前 `T_FILETIME64`，转 TOD 后比较 `>= TOD#18:00:00.000` 可做「每日 6 点启动」触发。
- **版本要求 TwinCAT v3.1.4024.0 + Tc2_Utilities ≥ 3.7.3.0**：相对较新的版本才有。

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_FILETIME64_TO_TOD.xml`](../examples/P_Demo_FILETIME64_TO_TOD.xml)
>
> 导入步骤：右键 PLC 项目 → Import PLCopenXML → 选该文件 → OK
> 详见 [`examples/README.md`](../examples/README.md)

```iecst
timeOfDay := FILETIME64_TO_TOD(timeAsFileTime);
```

完整可导入例程见上方链接，里面有 场景 / 价值 / 验证步骤 三件套注释。

## 7. 业务场景与实际价值

- **场景**：PLC 上的「每天 6 点出班次报表」、「每天 22 点开启省电模式」等按时间段触发的逻辑——只需要时刻不需要日期。
- **价值**：1 行调用完成「取出一天内时间」，避免手写 `wHour * 3600000 + wMinute * 60000 + wSecond * 1000 + wMilliseconds` 拼装 `TOD`。
- **替代方案对比**：走 `FILETIME64_TO_SYSTEMTIME` 再手拼 TOD（多步、易出错）/ 调用本 FC（推荐）。

## 8. 参考资料

- **PDF**：[TwinCAT_3_PLC_Lib_Tc2_Utilities_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_Utilities_EN.pdf) §4.1.15
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tcplclib_tc2_utilities/16285524619.html
- **相关函数**：见 [`Tc2_Utilities README`](../README.md)（同类 time functions）
