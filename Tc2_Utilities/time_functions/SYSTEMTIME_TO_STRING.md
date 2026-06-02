# SYSTEMTIME_TO_STRING

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc2_Utilities` |
| Library Version | `2.18.2` |
| Type | `FUNCTION` |
| Category | `Time functions` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_Utilities_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tcplclib_tc2_utilities/35155979.html |
| Verified | 2026-05-11 ✅ |
| InfoSys-checked | ✅ 2026-05-11 |
| Status | `verified` |
| Example | [`examples/P_Demo_SYSTEMTIME_TO_STRING.TcPOU`](../examples/P_Demo_SYSTEMTIME_TO_STRING.TcPOU) |

---

## 1. 功能简述

把 `TIMESTRUCT` 格式化为字符串 `YYYY-MM-DD-hh:mm:ss.xxx`（24 字节，用 `-` 分隔日期 / 时间，毫秒带小数点）。与 `STRING_TO_SYSTEMTIME` 互逆。

## 2. 接口定义

### 函数声明

```iecst
FUNCTION SYSTEMTIME_TO_STRING : STRING(24)
VAR_INPUT
    in : TIMESTRUCT;
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `in` | `TIMESTRUCT` | 待转换的 Windows 系统时间结构体 |

### 返回值

`STRING(24)` —— 见 §3 行为说明。

### VAR_IN_OUT

无。

## 3. 行为说明

格式严格固定：

- `YYYY` 年（1601 ~ 9999）4 位
- `-` 分隔
- `MM` 月（01 ~ 12）2 位
- `-` 分隔
- `DD` 日（01 ~ 31）2 位
- `-` 分隔（不是 `T`，**不是 ISO 8601**）
- `hh` 时（00 ~ 23）2 位
- `:` 分隔
- `mm` 分（00 ~ 59）2 位
- `:` 分隔
- `ss` 秒（00 ~ 59）2 位
- `.` 分隔
- `xxx` 毫秒（000 ~ 999）3 位

输出长度固定 23 字符，返回 `STRING(24)` 留 1 字节 NUL 终止符。

与 `SYSTEMTIME_TO_ISO8601` 不同的是本 FC 没有 TZD、不能选小数位精度。


注意本 FC 用 `-` 分隔日期和时间，**不是 ISO 8601**（ISO 8601 用 `T` 分隔）。它的字符串格式专为与 `STRING_TO_SYSTEMTIME` 互逆设计——在 PLC 内部往返、HMI 字段绑定、配置文件保存这类闭环场景里用本 FC 最直接；对外（REST / JSON / MQTT）要标准格式请改用 `SYSTEMTIME_TO_ISO8601`。

## 4. 错误码 / 返回值

返回类型 `STRING(24)`。函数无错误码 / 无 HRESULT；任意合法类型输入都有定义良好的返回值。详细边界与失败行为见 §5。

## 5. 使用注意 / 常见坑

- **用 `-` 分隔日期和时间不是 `T`**：不能当作 ISO 8601 字符串发给标准 JSON / REST API；要 ISO 8601 用 `SYSTEMTIME_TO_ISO8601`。
- **无错误返回**：`TIMESTRUCT` 字段越界（如 wMonth = 13）输出会含非法数字，调用方需先校验。
- **与 `STRING_TO_SYSTEMTIME` 互逆，但格式必须 23 字节**：解析端只接受这种特定格式。
- **字符串长度 23 字符**：23 个可见字符不含 NUL，正好填满 `STRING(24)` 容量。

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_SYSTEMTIME_TO_STRING.TcPOU`](../examples/P_Demo_SYSTEMTIME_TO_STRING.TcPOU)
>
> 导入步骤：右键 PLC 项目下 POUs 文件夹 → Add → Existing Item → 选该文件 → OK
> 详见 [`examples/README.md`](../examples/README.md)

```iecst
sTime := SYSTEMTIME_TO_STRING(FILETIME_TO_SYSTEMTIME(fileTime));
```

完整可导入例程见上方链接，里面有 场景 / 价值 / 验证步骤 三件套注释。

## 7. 业务场景与实际价值

- **场景**：PLC 写日志文件 / HMI 显示当前时间 / 报警消息加时间戳——需要稳定格式、字符串可比较可排序。
- **价值**：1 行调用完成 8 字段结构体到字符串拼接，避免手写 7 次数字 → 字符串补零 + 分隔符拼接。
- **替代方案对比**：用 `SYSTEMTIME_TO_ISO8601`（带 TZD 但分隔符是 `T`）/ 手写 `WORD_TO_STRING` + 补零（容易出错）/ 调用本 FC（推荐）。

## 8. 参考资料

- **PDF**：[TwinCAT_3_PLC_Lib_Tc2_Utilities_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_Utilities_EN.pdf) §4.1.21
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tcplclib_tc2_utilities/35155979.html
- **相关函数**：见 [`Tc2_Utilities README`](../README.md)（同类 time functions）
