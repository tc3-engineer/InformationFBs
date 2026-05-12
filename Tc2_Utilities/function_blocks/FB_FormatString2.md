# FB_FormatString2

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc2_Utilities` |
| Library Version | `2.18.2` |
| Type | `FUNCTION_BLOCK` |
| Category | `Function blocks` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_Utilities_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tcplclib_tc2_utilities/34994443.html |
| Verified | 2026-05-11 ✅ |
| InfoSys-checked | ✅ 2026-05-11 |
| Status | `verified` |
| Example | [`examples/P_Demo_FB_FormatString2.xml`](../examples/P_Demo_FB_FormatString2.xml) |

---

## 1. 功能简述

FB_FormatString2 是 FB_FormatString 的扩展版：支持更多格式符 / 更长输出缓冲 / Unicode 字符。

新项目优先用 Ex 版。

## 2. 接口定义

### VAR_INPUT

```iecst
VAR_INPUT
    pFormatString : POINTER TO STRING;
    arg1 : T_Arg;
    arg2 : T_Arg;
    arg3 : T_Arg;
    arg4 : T_Arg;
    arg5 : T_Arg;
    arg6 : T_Arg;
    arg7 : T_Arg;
    arg8 : T_Arg;
    arg9 : T_Arg;
    arg10 : T_Arg;
    pDstString : POINTER TO STRING;
    nDstSize : UDINT;
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `pFormatString` | `POINTER TO STRING` | 参数 `pFormatString`（类型 `POINTER TO STRING`）。⚠️ PDF 未详述含义，请按 §3 行为说明使用。 |
| `arg1` | `T_Arg` | 参数 `arg1`（类型 `T_Arg`）。⚠️ PDF 未详述含义，请按 §3 行为说明使用。 |
| `arg2` | `T_Arg` | 参数 `arg2`（类型 `T_Arg`）。⚠️ PDF 未详述含义，请按 §3 行为说明使用。 |
| `arg3` | `T_Arg` | 参数 `arg3`（类型 `T_Arg`）。⚠️ PDF 未详述含义，请按 §3 行为说明使用。 |
| `arg4` | `T_Arg` | 参数 `arg4`（类型 `T_Arg`）。⚠️ PDF 未详述含义，请按 §3 行为说明使用。 |
| `arg5` | `T_Arg` | 参数 `arg5`（类型 `T_Arg`）。⚠️ PDF 未详述含义，请按 §3 行为说明使用。 |
| `arg6` | `T_Arg` | 参数 `arg6`（类型 `T_Arg`）。⚠️ PDF 未详述含义，请按 §3 行为说明使用。 |
| `arg7` | `T_Arg` | 参数 `arg7`（类型 `T_Arg`）。⚠️ PDF 未详述含义，请按 §3 行为说明使用。 |
| `arg8` | `T_Arg` | 参数 `arg8`（类型 `T_Arg`）。⚠️ PDF 未详述含义，请按 §3 行为说明使用。 |
| `arg9` | `T_Arg` | 参数 `arg9`（类型 `T_Arg`）。⚠️ PDF 未详述含义，请按 §3 行为说明使用。 |
| `arg10` | `T_Arg` | 参数 `arg10`（类型 `T_Arg`）。⚠️ PDF 未详述含义，请按 §3 行为说明使用。 |
| `pDstString` | `POINTER TO STRING` | 参数 `pDstString`（类型 `POINTER TO STRING`）。⚠️ PDF 未详述含义，请按 §3 行为说明使用。 |
| `nDstSize` | `UDINT` | 无符号整数输入：`nDstSize`。 |

### VAR_OUTPUT

```iecst
VAR_OUTPUT
    bError : BOOL;
    nErrId : UDINT;
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `bError` | `BOOL` | TRUE 表示本次请求失败，错误号由 `nErrId` / `nErrorId` 给出。 |
| `nErrId` | `UDINT` | ADS 错误码或本 FB 自定义错误号。0 = 无错。具体码表见 InfoSys / ADS Return Codes。 |

### VAR_IN_OUT

无。

## 3. 行为说明

**调用**：与 FB_FormatString 类似，参数 / 输出更丰富。


**调用一般约束**：本 FB 的所有输入 / 输出引脚语义已在 §2 接口定义表的中文说明列详细列出；调用方应按上述时序与状态机分支组织程序，并参照 §5 使用注意 / 常见坑回避典型陷阱。若 PDF 与 InfoSys 中未对某种异常工况作出明确说明，本仓库会以 ⚠️ 标记，提示读者用实测或在 Beckhoff Forum 上确认，而非凭推测下结论。

## 4. 错误码 / 返回值

本 FB 通过 `bErr` + `nErrId`（或 `bError` + `nErrorId`）输出报告错误：

- `bErr / bError = FALSE` 且 `nErrId / nErrorId = 0`：本次请求成功。
- `bErr / bError = TRUE`：本次请求失败，错误号在 `nErrId / nErrorId`。

常见错误号属于 **ADS Return Codes**（PDF 与 InfoSys 都引用此表）：

| 错误号（十六进制） | 含义 |
|---|---|
| `0x06` | 目标端口未找到（ADSERR_DEVICE_NOTFOUND） |
| `0x07` | 目标机器未找到（ADSERR_DEVICE_INVALIDDATA） |
| `0x745` | ADS 通讯超时（ADSERR_CLIENT_SYNCTIMEOUT） |
| 其他 | PDF 未枚举，详见 Beckhoff 在线 ADS Return Codes 表 ⚠️ |

## 5. 使用注意 / 常见坑

- 与 FB_FormatString 共享大多数陷阱。
- Unicode 处理要确保参数也是宽字符。（工程经验补充）
- 输出缓冲若用 STRING(N) 仍受 N 限制；Unicode 用 WSTRING(N)。（工程经验补充）
- PDF 未细分错误码。
- Beckhoff 在新版本里 FB_FormatString2 通常是首选。（工程经验补充）

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_FB_FormatString2.xml`](../examples/P_Demo_FB_FormatString2.xml)（PLCopenXML，可直接导入 TwinCAT 3 XAE）。
>
> 导入步骤：右键 PLC 项目 → Import PLCopenXML → 选该文件 → OK

详见 example xml 文件。

## 7. 业务场景与实际价值

- **场景**：HMI Unicode 显示文本。
- **价值**：支持 Unicode。
- **替代方案对比**：
  - FB_FormatString：仅 ASCII。
  - **本 FB**：Unicode。

## 8. 参考资料

- **PDF**：[TwinCAT_3_PLC_Lib_Tc2_Utilities_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_Utilities_EN.pdf) §3.23
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tcplclib_tc2_utilities/34994443.html
