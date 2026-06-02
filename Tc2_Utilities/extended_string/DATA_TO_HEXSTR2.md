# DATA_TO_HEXSTR2

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc2_Utilities` |
| Library Version | `2.18.2` |
| Type | `FUNCTION` |
| Category | `Extended STRING functions` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_Utilities_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tcplclib_tc2_utilities/14612463115.html |
| Verified | 2026-05-12 ✅ |
| InfoSys-checked | ✅ 2026-05-12 |
| Status | `verified` |
| Example | [`examples/P_Demo_DATA_TO_HEXSTR2.TcPOU`](../examples/P_Demo_DATA_TO_HEXSTR2.TcPOU) |

---

## 1. 功能简述

把任意二进制数据（结构体、数组、原始字节流）转换为可读的十六进制字符串；支持大小写选择、超长截断标记 `'.'`，比 `DATA_TO_HEXSTR` 更安全（输出有显式 size 限制，不会缓冲溢出）。

`Extended STRING functions` 这一组（PDF 4.2.x）是 Beckhoff 在 `Tc2_Standard` 之上扩展的"长字符串友好"版本：`Tc2_Standard` 里的同名函数（`CONCAT` / `FIND` / `INSERT` / `LEN` 等）受 IEC 61131-3 早期 STRING(255) 限制，处理超过 255 字符的串会**静默截断或返回错误结果**；本组的 `*2` 后缀函数全部接受 `POINTER TO STRING` + 显式 `nDstSize`，允许任意长度，并返回 `BOOL` / 字符数明确告知是否完整完成。

## 2. 接口定义

### VAR_INPUT

```iecst
VAR_INPUT
    pSrcData : POINTER TO BYTE;
    nSrcSize : UDINT;
    pDstHexStr : POINTER TO STRING;
    nDstSize : UDINT;
    bLoCase : BOOL;
END_VAR
```

| 名称 | 类型 | 默认值 | 说明（中文） |
|---|---|---|---|
| `pSrcData` | `POINTER TO BYTE` | — | 待转换的二进制数据起始地址；用 `ADR(buf)` 取。 |
| `nSrcSize` | `UDINT` | — | 源数据字节数；用 `SIZEOF(buf)` 取。 |
| `pDstHexStr` | `POINTER TO STRING` | — | 目标十六进制字符串地址；用 `ADR(sHex)` 取。 |
| `nDstSize` | `UDINT` | — | 目标缓冲区字节数；含 null 终结符位置。 |
| `bLoCase` | `BOOL` | — | `TRUE` = 用小写 `abcdef`；`FALSE` = 用大写 `ABCDEF`。 |

### 返回值

| 类型 | 说明（中文） |
|---|---|
| `UDINT` | 成功转换的源字节数。若目标空间不够，会在结果串末尾添加 `'.'` 标识截断，返回的字节数 < `nSrcSize`。 |

## 3. 行为说明

函数无状态。逐字节读 `pSrcData[0..nSrcSize-1]`，每字节按 `bLoCase` 选择 `[0-9A-F]` 或 `[0-9a-f]` 字符集格式化为两个 hex 字符并追加到 `pDstHexStr`。字节之间用单空格分隔（如 `'AB CD 01 23'`）。若累计写入长度（含分隔符）超过 `nDstSize - 2`（要保留位置写 `'.'` 和 null），停止并写入 `'.'` 表示截断，再写 null 终结符。返回值为**已成功转换的源字节数**——业务侧用 `LEN(sHex) > 0` 不够准确，应判断**返回值 == `nSrcSize`** 才是完全转换。

## 4. 错误码 / 返回值

返回 `UDINT`：成功转换的源字节数。若目标空间不够，会在结果串末尾添加 `'.'` 标识截断，返回的字节数 < `nSrcSize`。

⚠️ 本函数不通过 HRESULT 报错——所有错误均通过返回值的特殊值（`FALSE` / `0`）表达；调用方必须始终判返回值，不能假定调用总成功。

## 5. 使用注意 / 常见坑

- 返回值是**源字节数**不是目标字符数。判断完整：`F_NbReturned = nSrcSize`，不是 `LEN(sHex) > 0`。
- **两字符 + 一空格 ≈ 每源字节 3 字符**。声明目标 STRING 大小 ≥ `nSrcSize * 3 + 2`（包含末尾 `'.'` 截断标识 + null）。
- 结果串末尾 `'.'` 表示截断——业务侧应检查 `pDstHexStr^` 是否以 `.` 结尾来识别。
- `DATA_TO_HEXSTR`（不带 2）是旧版，源大小固定限制，**不推荐新代码使用**；本 `2` 版本支持显式 `nDstSize` 边界。
- `bLoCase` 选项主要影响哈希值显示风格；MD5/SHA 习惯小写、TwinCAT 内部日志习惯大写。
- 可以转结构体：`DATA_TO_HEXSTR2(ADR(stRecord), SIZEOF(stRecord), ...)`，但要注意 padding 字节也会被打印。
- ⚠️ PDF / InfoSys 未列错误返回（如 `nDstSize = 0`）；建议调用前断言 `nDstSize >= 4`。

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_DATA_TO_HEXSTR2.TcPOU`](../examples/P_Demo_DATA_TO_HEXSTR2.TcPOU)（TwinCAT 3 原生 .TcPOU，可直接拖入 XAE 的 PLC POUs 文件夹）
>
> 导入步骤：右键 PLC 项目下 POUs 文件夹 → Add → Existing Item → 选该文件 → OK
> 详见 [`examples/README.md`](../examples/README.md)

## 7. 业务场景与实际价值

- **场景**：把 EtherCAT 从站的 CoE 对象字典对象（任意字节流）转为 hex 字符串写入日志，便于诊断协议级问题。
- **价值**：替代手写 `FOR i := 0 TO N DO sHex := CONCAT(sHex, ...)` 的 30 行代码；本函数 1 行调用，O(N) 时间且带 size 保护。
- **替代方案对比**：`DATA_TO_HEXSTR`：旧版无显式 nDstSize；`HEXSTR_TO_DATA2`：反向（hex → 数据）；手写 MEMCPY + 格式化：易写错。

## 8. 参考资料

- **PDF**：[TwinCAT_3_PLC_Lib_Tc2_Utilities_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_Utilities_EN.pdf) 第 4.2.3 节
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tcplclib_tc2_utilities/14612463115.html
- **相关函数**：见同库 `extended_string/` 目录下其他 `*2` 版本扩展函数
