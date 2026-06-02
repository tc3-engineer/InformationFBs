# FB_StringRingBuffer

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc2_Utilities` |
| Library Version | `2.18.2` |
| Type | `FUNCTION_BLOCK` |
| Category | `Function blocks` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_Utilities_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tcplclib_tc2_utilities/35024651.html |
| Verified | 2026-05-11 ✅ |
| InfoSys-checked | ✅ 2026-05-11 |
| Status | `verified` |
| Example | [`examples/P_Demo_FB_StringRingBuffer.TcPOU`](../examples/P_Demo_FB_StringRingBuffer.TcPOU) |

---

## 1. 功能简述

FB_StringRingBuffer 字符串专用环形缓冲——每条记录是 STRING(N)。

用于：HMI 消息历史、操作员输入历史。

## 2. 接口定义

### VAR_INPUT

```iecst
VAR_INPUT
    bOverwrite : BOOL;
    putValue : T_MaxString := '';
    pBuffer : POINTER TO BYTE;
    cbBuffer : UDINT;
END_VAR
```

| 名称 | 类型 | 默认值 | 说明 |
|---|---|---|---|
| `bOverwrite` | `BOOL` | - | 输入布尔标志：`bOverwrite`。具体语义见 §3 行为说明。 |
| `putValue` | `T_MaxString` | `''` | 参数 `putValue`（类型 `T_MaxString`）。⚠️ PDF 未详述含义，请按 §3 行为说明使用。 |
| `pBuffer` | `POINTER TO BYTE` | - | 缓冲区指针（`PVOID` / `POINTER TO BYTE`），调用方负责分配。 |
| `cbBuffer` | `UDINT` | - | 缓冲区字节数。 |

### VAR_OUTPUT

```iecst
VAR_OUTPUT
    bOk : BOOL;
    getValue : T_MaxString := '';
    nCount : UDINT;
    cbSize : UDINT;
END_VAR
```

| 名称 | 类型 | 默认值 | 说明 |
|---|---|---|---|
| `bOk` | `BOOL` | - | 输出布尔标志：`bOk`。具体语义见 §3 行为说明。 |
| `getValue` | `T_MaxString` | `''` | 参数 `getValue`（类型 `T_MaxString`）。⚠️ PDF 未详述含义，请按 §3 行为说明使用。 |
| `nCount` | `UDINT` | - | 无符号整数输出：`nCount`。 |
| `cbSize` | `UDINT` | - | 无符号整数输出：`cbSize`。 |

### VAR_IN_OUT

无。

## 3. 行为说明

**OO 方法**：`Init` 容量 + 字符串长度 → `Add` 追加字符串 → `Get` 取回。


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

> 配套可导入文件：[`examples/P_Demo_FB_StringRingBuffer.TcPOU`](../examples/P_Demo_FB_StringRingBuffer.TcPOU)（TwinCAT 3 原生 .TcPOU，可直接拖入 XAE 的 PLC POUs 文件夹）。
>
> 导入步骤：右键 PLC 项目下 POUs 文件夹 → Add → Existing Item → 选该文件 → OK

详见 example xml 文件。

## 7. 业务场景与实际价值

- **场景**：HMI 消息历史最近 100 条。
- **价值**：字符串专用，免转字节流。
- **替代方案对比**：
  - FB_MemRingBuffer：要自己处理字符串字节。
  - **本 FB**：直接 STRING。

## 8. 参考资料

- **PDF**：[TwinCAT_3_PLC_Lib_Tc2_Utilities_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_Utilities_EN.pdf) §3.58
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tcplclib_tc2_utilities/35024651.html
