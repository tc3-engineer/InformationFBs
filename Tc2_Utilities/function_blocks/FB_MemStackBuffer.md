# FB_MemStackBuffer

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc2_Utilities` |
| Library Version | `2.18.2` |
| Type | `FUNCTION_BLOCK` |
| Category | `Function blocks` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_Utilities_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tcplclib_tc2_utilities/35012107.html |
| Verified | 2026-05-11 ✅ |
| InfoSys-checked | ✅ 2026-05-11 |
| Status | `verified` |
| Example | [`examples/P_Demo_FB_MemStackBuffer.xml`](../examples/P_Demo_FB_MemStackBuffer.xml) |

---

## 1. 功能简述

FB_MemStackBuffer 实现内存栈（LIFO）——后进先出。

用于：函数调用栈仿真、操作历史（Undo 栈）、深度优先搜索。

## 2. 接口定义

### VAR_INPUT

```iecst
VAR_INPUT
    pWrite : POINTER TO BYTE;
    cbWrite : UDINT;
    pRead : POINTER TO BYTE;
    cbRead : UDINT;
    pBuffer : POINTER TO BYTE;
    cbBuffer : UDINT;
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `pWrite` | `POINTER TO BYTE` | 参数 `pWrite`（类型 `POINTER TO BYTE`）。⚠️ PDF 未详述含义，请按 §3 行为说明使用。 |
| `cbWrite` | `UDINT` | 无符号整数输入：`cbWrite`。 |
| `pRead` | `POINTER TO BYTE` | 参数 `pRead`（类型 `POINTER TO BYTE`）。⚠️ PDF 未详述含义，请按 §3 行为说明使用。 |
| `cbRead` | `UDINT` | 无符号整数输入：`cbRead`。 |
| `pBuffer` | `POINTER TO BYTE` | 缓冲区指针（`PVOID` / `POINTER TO BYTE`），调用方负责分配。 |
| `cbBuffer` | `UDINT` | 缓冲区字节数。 |

### VAR_OUTPUT

```iecst
VAR_OUTPUT
    bOk : BOOL;
    nCount : UDINT;
    cbSize : UDINT;
    cbReturn : UDINT;
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `bOk` | `BOOL` | 输出布尔标志：`bOk`。具体语义见 §3 行为说明。 |
| `nCount` | `UDINT` | 无符号整数输出：`nCount`。 |
| `cbSize` | `UDINT` | 无符号整数输出：`cbSize`。 |
| `cbReturn` | `UDINT` | 无符号整数输出：`cbReturn`。 |

### VAR_IN_OUT

无。

## 3. 行为说明

**OO 方法**：`Init` → `Push` 入栈 → `Pop` 出栈 → `Peek` 看栈顶不出。


**调用一般约束**：本 FB 的所有输入 / 输出引脚语义已在 §2 接口定义表的中文说明列详细列出；调用方应按上述时序与状态机分支组织程序，并参照 §5 使用注意 / 常见坑回避典型陷阱。若 PDF 与 InfoSys 中未对某种异常工况作出明确说明，本仓库会以 ⚠️ 标记，提示读者用实测或在 Beckhoff Forum 上确认，而非凭推测下结论。

## 4. 错误码 / 返回值

本 FB 无显式错误输出。状态可以通过 `bBusy` / `bValid` / `bDone` 等过程信号间接判断。

## 5. 使用注意 / 常见坑

- 调用方需预分配缓冲区，缓冲区大小由 `cbBuffer` 参数告知 FB；超出会截断。
- **指针运算需小心**：`pBuffer` 必须指向有效内存，FB 不做有效性校验。
- `STRING(N)` 内部字节布局含尾零；处理 raw bytes 时区分 `LEN()` 与 `SIZEOF()`。（工程经验补充）
- PDF 未给详细错误码——多数错误反映为 `bError = TRUE` 不区分子类，业务侧靠输入合法性预检为主。
- CSV 字段分隔符默认为 `;`（欧洲风格），中国 / 北美场景常用 `,` 要在初始化时配置。（工程经验补充）
- 栈满 `Push` 失败，业务侧要预估深度。

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_FB_MemStackBuffer.xml`](../examples/P_Demo_FB_MemStackBuffer.xml)（PLCopenXML，可直接导入 TwinCAT 3 XAE）。
>
> 导入步骤：右键 PLC 项目 → Import PLCopenXML → 选该文件 → OK

详见 example xml 文件。

## 7. 业务场景与实际价值

- **场景**：Undo 操作栈。
- **价值**：标准 LIFO 数据结构。
- **替代方案对比**：
  - 自写：易出错。
  - **本 FB**：库提供。

## 8. 参考资料

- **PDF**：[TwinCAT_3_PLC_Lib_Tc2_Utilities_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_Utilities_EN.pdf) §3.52
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tcplclib_tc2_utilities/35012107.html
