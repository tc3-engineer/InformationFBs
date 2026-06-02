# BYTEARR_TO_MAXSTRING

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc2_Utilities` |
| Library Version | `2.18.2` |
| Type | `FUNCTION` |
| Category | `Functions` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_Utilities_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tcplclib_tc2_utilities/35073035.html |
| Verified | 2026-05-12 ✅ |
| InfoSys-checked | ✅ 2026-05-12 |
| Status | `verified` |
| Example | [`examples/P_Demo_BYTEARR_TO_MAXSTRING.TcPOU`](../examples/P_Demo_BYTEARR_TO_MAXSTRING.TcPOU) |

---

## 1. 功能简述

把字节数组的 ASCII 码逐字节复制成 `T_MaxString`（默认 STRING(255)）；与 `MAXSTRING_TO_BYTEARR` 构成可逆对。

本函数属于 `Tc2_Utilities` 库的 `Functions` 类别（PDF 第 4 章）——这一类是不带状态的纯函数集合：CRC / 校验和 / 哈希、字符串与字节流互转、GUID 处理、各种基本类型与传输格式之间的桥接。它们是 PLC 通信、日志、配置文件处理的底层零件，多数在 `Tc2_Standard` 之外补充 Beckhoff 工业自动化场景下的常用工具。

## 2. 接口定义

### VAR_INPUT

```iecst
VAR_INPUT
    in : ARRAY[0..MAX_STRING_LENGTH] OF BYTE;
END_VAR
```

| 名称 | 类型 | 默认值 | 说明（中文） |
|---|---|---|---|
| `in` | `ARRAY[0..MAX_STRING_LENGTH] OF BYTE` | — | 源字节数组（默认大小为 STRING(255) 对应 256 字节）。 |

### 返回值

| 类型 | 说明（中文） |
|---|---|
| `T_MaxString` | 详见 §3 行为说明。|

### VAR_OUTPUT

无（本符号是 `FUNCTION`，结果通过返回值传出）。

### 返回值

| 类型 | 说明（中文） |
|---|---|
| `T_MaxString` | 拼接得到的字符串（`STRING(255)`），不含末尾 `16#00`。 |

### VAR_OUTPUT

无（本符号是 `FUNCTION`，结果通过返回值传出）。

## 3. 行为说明

函数无状态、立即返回。逐字节从 `in[0]` 起复制到目标 STRING 缓冲，直到遇到 null 字节（0x00）或扫满数组长度 `MAX_STRING_LENGTH`。null 字节作为 STRING 终结符；遇 null 后即使数组未扫完也立即停止。**这意味着含 0x00 的二进制字节数组不能完整复制——前缀部分被当成 STRING 解读、后半丢失**。配套反向函数 `MAXSTRING_TO_BYTEARR` 把 STRING 写回字节数组（不含 null 之后内容）。生产环境用此函数把 EtherCAT / ModBus 字节缓冲的 ASCII 部分拿出来做日志显示。

## 4. 错误码 / 返回值

返回 `T_MaxString`——具体语义见 §3。错误约定：
- 多数函数无独立错误码，**通过返回值的特殊值（如 0 / 255 / 空串 / `FALSE`）报错**——调用方必须始终判返回值。
- 涉及输出缓冲的函数在缓冲不够时通常截断、返回 `FALSE` 或特殊标记；调用方应**始终把返回值当主要错误信号**。

## 5. 使用注意 / 常见坑

- **数组中 0x00 视为 STRING 终结**——含 0x00 的二进制数据会被截断。要保留完整二进制请直接按 BYTE 数组传递或用 `MEMCPY`。
- `MAX_STRING_LENGTH` 是 `Tc2_Utilities` 的常量（默认 255）；类型不可改。需要更长串请用 `Extended STRING functions`。
- 返回类型 `T_MaxString` 实际是 `STRING(255)`；超长源数组中后续字节直接丢弃。
- ASCII 直接复制：源字节 0x80~0xFF 也会被复制，但 STRING 的 Codepage 语义可能不同。
- **对称函数 `MAXSTRING_TO_BYTEARR`** 把 STRING 转回 BYTE 数组（不含 null）。

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_BYTEARR_TO_MAXSTRING.TcPOU`](../examples/P_Demo_BYTEARR_TO_MAXSTRING.TcPOU)（TwinCAT 3 原生 .TcPOU，可直接拖入 XAE 的 PLC POUs 文件夹）
>
> 导入步骤：右键 PLC 项目下 POUs 文件夹 → Add → Existing Item → 选该文件 → OK
> 详见 [`examples/README.md`](../examples/README.md)

## 7. 业务场景与实际价值

- **场景**：从串口收到的 256 字节缓冲含 EtherNet/IP 设备 SCSI 标签——前部 ASCII 标签 + 后部二进制数据。本函数把前部 ASCII 提取为可读日志。
- **价值**：替代 FOR + 字节复制 + null 终结的 8 行手写循环；本函数 1 调用。
- **替代方案对比**：`MAXSTRING_TO_BYTEARR`：反向；`MEMCPY`：手动版本无 null 处理。

## 8. 参考资料

- **PDF**：[TwinCAT_3_PLC_Lib_Tc2_Utilities_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_Utilities_EN.pdf) 第 4.19 节
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tcplclib_tc2_utilities/35073035.html
- **相关函数**：见同库 `functions/` 目录下其他工具函数
