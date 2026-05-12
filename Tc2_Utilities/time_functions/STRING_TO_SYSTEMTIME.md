# STRING_TO_SYSTEMTIME

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc2_Utilities` |
| Library Version | `2.18.2` |
| Type | `FUNCTION` |
| Category | `Time functions` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_Utilities_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tcplclib_tc2_utilities/35157515.html |
| Verified | 2026-05-11 ✅ |
| InfoSys-checked | ✅ 2026-05-11 |
| Status | `verified` |
| Example | [`examples/P_Demo_STRING_TO_SYSTEMTIME.xml`](../examples/P_Demo_STRING_TO_SYSTEMTIME.xml) |

---

## 1. 功能简述

把 23 字节的字符串 `«YYYY-MM-DD-hh:mm:ss.xxx»` 解析为 `TIMESTRUCT`。与 `SYSTEMTIME_TO_STRING` 互逆。常用于从配置文件 / HMI 输入框 / 上位机消息里读时间。

## 2. 接口定义

### 函数声明

```iecst
FUNCTION STRING_TO_SYSTEMTIME : TIMESTRUCT
VAR_INPUT
    in : STRING(23);
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `in` | `STRING(23)` | 待解析的字符串，格式必须是 `«YYYY-MM-DD-hh:mm:ss.xxx»`（YYYY: 1601-9999，MM: 01-12，DD: 01-31，hh: 00-23，mm: 00-59，ss: 00-59，xxx: 000-999） |

### 返回值

`TIMESTRUCT` —— 见 §3 行为说明。

### VAR_IN_OUT

无。

## 3. 行为说明

函数按位置切分字符串（年 4 位、月 2 位、日 2 位、时 2 位、分 2 位、秒 2 位、毫秒 3 位，固定分隔符 `-` `-` `:` `:` `:` `.`）后逐字段转 `WORD` 填进 `TIMESTRUCT`。

注意分隔符模式严格——日和时之间是 `-`（连字符），不是 `:` 或空格；秒和毫秒之间是 `.`。任何分隔符不一致 / 字段位数不对 / 数字范围越界都会导致结果不可预测。

PDF 未明确「非法字符串如何报错」——实测可能返回部分填充 / 全 0 的 `TIMESTRUCT`，**调用方必须自己保证字符串格式正确**，不要靠返回值检测。

## 4. 错误码 / 返回值

返回类型 `TIMESTRUCT`。函数无错误码 / 无 HRESULT；任意合法类型输入都有定义良好的返回值。详细边界与失败行为见 §5。

## 5. 使用注意 / 常见坑

- **格式极其严格**：必须 23 字节，`-` `-` `:` `:` `:` `.` 这 6 个分隔符在固定位置，**多 1 字节少 1 字节都解析失败**。
- **与 `STRING_TO_DT` 不同**：`DT` 用 `«DT#YYYY-MM-DD-hh:mm:ss»` 格式（带 `DT#` 前缀，无毫秒），本 FC 用纯 `«YYYY-MM-DD-hh:mm:ss.xxx»`（无前缀，有毫秒）。两种格式不通用。
- **没有错误返回**：PDF 未规定非法输入的行为，**调用前必须自己用 `LEN` 检查字符串长度 = 23**。（工程经验补充）
- **与 ISO 8601 不一样**：ISO 8601 用 `T` 分隔日期和时间，本 FC 用 `-`，不能直接喂 ISO 8601 字符串。

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_STRING_TO_SYSTEMTIME.xml`](../examples/P_Demo_STRING_TO_SYSTEMTIME.xml)
>
> 导入步骤：右键 PLC 项目 → Import PLCopenXML → 选该文件 → OK
> 详见 [`examples/README.md`](../examples/README.md)

```iecst
systemTime := STRING_TO_SYSTEMTIME('2026-05-11-12:34:56.789');
```

完整可导入例程见上方链接，里面有 场景 / 价值 / 验证步骤 三件套注释。

## 7. 业务场景与实际价值

- **场景**：上位机 / HMI 通过文本协议下发时间设定值；或者从 CSV 配置文件读取计划维护时间字符串需要还原成 PLC 能用的结构体。
- **价值**：1 行调用完成 23 字节字符串到 8 字段结构体的解析；手写要 7 次 `STRING_TO_INT` + 边界检查 30+ 行。
- **替代方案对比**：用 `MID` + `STRING_TO_INT` 手拼 7 个字段（更啰嗦）/ 走中间 `DT` 类型（精度丢毫秒）/ 调用本 FC（推荐）。

## 8. 参考资料

- **PDF**：[TwinCAT_3_PLC_Lib_Tc2_Utilities_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_Utilities_EN.pdf) §4.1.17
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tcplclib_tc2_utilities/35157515.html
- **相关函数**：见 [`Tc2_Utilities README`](../README.md)（同类 time functions）
