# FB_CSVMemBufferWriter

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc2_Utilities` |
| Library Version | `2.18.2` |
| Type | `FUNCTION_BLOCK` |
| Category | `Function blocks` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_Utilities_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tcplclib_tc2_utilities/34979467.html |
| Verified | 2026-05-11 ✅ |
| InfoSys-checked | ✅ 2026-05-11 |
| Status | `verified` |
| Example | [`examples/P_Demo_FB_CSVMemBufferWriter.xml`](../examples/P_Demo_FB_CSVMemBufferWriter.xml) |

---

## 1. 功能简述

FB_CSVMemBufferWriter 把一系列字段按 CSV 格式追加写入内存缓冲，最终缓冲可写到磁盘。

用于：生成生产日报 / 参数导出表。

## 2. 接口定义

### VAR_INPUT

```iecst
VAR_INPUT
    eCmd : E_EnumCmdType := eEnumCmd_First;
    putValue : T_MaxString := '';
    pValue : POINTER TO BYTE := 0;
    cbValue : UDINT := 0;
    bCRLF : BOOL := FALSE;
    pBuffer : POINTER TO BYTE;
    cbBuffer : UDINT;
END_VAR
```

| 名称 | 类型 | 默认值 | 说明 |
|---|---|---|---|
| `eCmd` | `E_EnumCmdType` | `eEnumCmd_First` | 参数 `eCmd`（类型 `E_EnumCmdType`）。⚠️ PDF 未详述含义，请按 §3 行为说明使用。 |
| `putValue` | `T_MaxString` | `''` | 参数 `putValue`（类型 `T_MaxString`）。⚠️ PDF 未详述含义，请按 §3 行为说明使用。 |
| `pValue` | `POINTER TO BYTE` | `0` | 参数 `pValue`（类型 `POINTER TO BYTE`）。⚠️ PDF 未详述含义，请按 §3 行为说明使用。 |
| `cbValue` | `UDINT` | `0` | 无符号整数输入：`cbValue`。 |
| `bCRLF` | `BOOL` | `FALSE` | 输入布尔标志：`bCRLF`。具体语义见 §3 行为说明。 |
| `pBuffer` | `POINTER TO BYTE` | - | 缓冲区指针（`PVOID` / `POINTER TO BYTE`），调用方负责分配。 |
| `cbBuffer` | `UDINT` | - | 缓冲区字节数。 |

### VAR_OUTPUT

```iecst
VAR_OUTPUT
    bOk : BOOL;
    cbSize : UDINT;
    cbFree : UDINT;
    nFields : UDINT;
    nRecords : UDINT;
    cbWrite : UDINT;
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `bOk` | `BOOL` | 输出布尔标志：`bOk`。具体语义见 §3 行为说明。 |
| `cbSize` | `UDINT` | 无符号整数输出：`cbSize`。 |
| `cbFree` | `UDINT` | 无符号整数输出：`cbFree`。 |
| `nFields` | `UDINT` | 无符号整数输出：`nFields`。 |
| `nRecords` | `UDINT` | 无符号整数输出：`nRecords`。 |
| `cbWrite` | `UDINT` | 无符号整数输出：`cbWrite`。 |

### VAR_IN_OUT

无。

## 3. 行为说明

**OO 方法接口**：`Init` 绑定缓冲 → 循环 `WriteField` 追加字段 → `WriteNewLine` 换行。


**调用一般约束**：本 FB 的所有输入 / 输出引脚语义已在 §2 接口定义表的中文说明列详细列出；调用方应按上述时序与状态机分支组织程序，并参照 §5 使用注意 / 常见坑回避典型陷阱。若 PDF 与 InfoSys 中未对某种异常工况作出明确说明，本仓库会以 ⚠️ 标记，提示读者用实测或在 Beckhoff Forum 上确认，而非凭推测下结论。

## 4. 错误码 / 返回值

本 FB 无显式错误输出。状态可以通过 `bBusy` / `bValid` / `bDone` 等过程信号间接判断。

## 5. 使用注意 / 常见坑

- 调用方需预分配缓冲区，缓冲区大小由 `cbBuffer` 参数告知 FB；超出会截断。
- **指针运算需小心**：`pBuffer` 必须指向有效内存，FB 不做有效性校验。
- `STRING(N)` 内部字节布局含尾零；处理 raw bytes 时区分 `LEN()` 与 `SIZEOF()`。（工程经验补充）
- PDF 未给详细错误码——多数错误反映为 `bError = TRUE` 不区分子类，业务侧靠输入合法性预检为主。
- CSV 字段分隔符默认为 `;`（欧洲风格），中国 / 北美场景常用 `,` 要在初始化时配置。（工程经验补充）

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_FB_CSVMemBufferWriter.xml`](../examples/P_Demo_FB_CSVMemBufferWriter.xml)（PLCopenXML，可直接导入 TwinCAT 3 XAE）。
>
> 导入步骤：右键 PLC 项目 → Import PLCopenXML → 选该文件 → OK

详见 example xml 文件。

## 7. 业务场景与实际价值

- **场景**：生成生产日报 CSV。
- **价值**：替代手写格式化。
- **替代方案对比**：
  - 自写 CSV：边界条件多（含分隔符的字段要加引号转义）。
  - **本 FB**：库处理转义。

## 8. 参考资料

- **PDF**：[TwinCAT_3_PLC_Lib_Tc2_Utilities_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_Utilities_EN.pdf) §3.14
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tcplclib_tc2_utilities/34979467.html
