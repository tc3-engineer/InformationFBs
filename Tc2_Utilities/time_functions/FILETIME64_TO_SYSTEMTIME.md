# FILETIME64_TO_SYSTEMTIME

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc2_Utilities` |
| Library Version | `2.18.2` |
| Type | `FUNCTION` |
| Category | `Time functions` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_Utilities_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tcplclib_tc2_utilities/10501062667.html |
| Verified | 2026-05-11 ✅ |
| InfoSys-checked | ✅ 2026-05-11 |
| Status | `verified` |
| Example | [`examples/P_Demo_FILETIME64_TO_SYSTEMTIME.xml`](../examples/P_Demo_FILETIME64_TO_SYSTEMTIME.xml) |

---

## 1. 功能简述

把 64 位 `T_FILETIME64`（100ns 精度）转换为 `TIMESTRUCT`（毫秒精度，按年月日时分秒毫秒展开的结构体）。**如果 `T_FILETIME64` 的最高位为 1（数值超出公历范围）转换失败，所有结构体字段被置为 0**。

## 2. 接口定义

### 函数声明

```iecst
FUNCTION FILETIME64_TO_SYSTEMTIME : TIMESTRUCT
VAR_INPUT
    fileTime : T_FILETIME64;
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `fileTime` | `T_FILETIME64` | 待转换的 `T_FILETIME64` 时间 |

### 返回值

`TIMESTRUCT` —— 见 §3 行为说明。

### VAR_IN_OUT

无。

## 3. 行为说明

函数把 64 位时间戳拆分为年 / 月 / 日 / 时 / 分 / 秒 / 毫秒并填进 `TIMESTRUCT`：

- 基准从 1601-01-01 UTC 开始
- 100ns 累计计数除以 10000 得到毫秒
- 自动计算 `wDayOfWeek`（0 = Sunday Windows 约定）

**失败条件（PDF 明确）**：如果 fileTime 的最高位（bit 63）为 1，则 64 位有符号表示是负数（在公历语义上无效，因为 1601 起算不应该为负），转换被拒绝并返回所有字段为 0 的 `TIMESTRUCT`。

与 `FILETIME64_TO_DT` 相比，本 FC 保留毫秒精度；与 `FILETIME64_TO_ISO8601` 相比，本 FC 输出结构体便于程序访问单个字段。

## 4. 错误码 / 返回值

返回类型 `TIMESTRUCT`。函数无错误码 / 无 HRESULT；任意合法类型输入都有定义良好的返回值。详细边界与失败行为见 §5。

## 5. 使用注意 / 常见坑

- **失败时返回全 0 `TIMESTRUCT`**：必须检查 `result.wYear > 0` 才能信任结果，不要把全 0 当成「1601-01-01 00:00:00」使用。
- **毫秒在 wMilliseconds 字段**：100ns 单位的精度在 `TIMESTRUCT` 里折算到毫秒（即丢弃了 1ms 以下的精度）。
- **版本要求 ≥ 3.3.44.0**：旧版只有 32 位的 `FILETIME_TO_SYSTEMTIME`。
- **与 `SYSTEMTIME_TO_FILETIME64` 互逆**：先后调用应能精确还原（毫秒以上精度）。

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_FILETIME64_TO_SYSTEMTIME.xml`](../examples/P_Demo_FILETIME64_TO_SYSTEMTIME.xml)
>
> 导入步骤：右键 PLC 项目 → Import PLCopenXML → 选该文件 → OK
> 详见 [`examples/README.md`](../examples/README.md)

```iecst
timeAsSystemTime := FILETIME64_TO_SYSTEMTIME(timeAsFileTime);
```

完整可导入例程见上方链接，里面有 场景 / 价值 / 验证步骤 三件套注释。

## 7. 业务场景与实际价值

- **场景**：需要按字段访问时间（年、月、日、时、分、秒、毫秒），如 HMI 表格显示、按月分类归档、报警时间打印。
- **价值**：1 行调用拿到 8 个分解字段（含 wDayOfWeek），保留毫秒精度；手写要 100+ 行（含闰年 / 月长 / 星期计算）。
- **替代方案对比**：用 `FILETIME64_TO_DT` 再 `DT_TO_SYSTEMTIME`（丢毫秒）/ 手写分解（极易出错）/ 调用本 FC（推荐）。

## 8. 参考资料

- **PDF**：[TwinCAT_3_PLC_Lib_Tc2_Utilities_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_Utilities_EN.pdf) §4.1.14
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tcplclib_tc2_utilities/10501062667.html
- **相关函数**：见 [`Tc2_Utilities README`](../README.md)（同类 time functions）
