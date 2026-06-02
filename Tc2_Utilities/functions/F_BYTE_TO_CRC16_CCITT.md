# F_BYTE_TO_CRC16_CCITT

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc2_Utilities` |
| Library Version | `2.18.2` |
| Type | `FUNCTION` |
| Category | `Functions` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_Utilities_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tcplclib_tc2_utilities/35108363.html |
| Verified | 2026-05-12 ✅ |
| InfoSys-checked | ✅ 2026-05-12 |
| Status | `verified` |
| Example | [`examples/P_Demo_F_BYTE_TO_CRC16_CCITT.TcPOU`](../examples/P_Demo_F_BYTE_TO_CRC16_CCITT.TcPOU) |

---

## 1. 功能简述

单字节版本 CRC-16 CCITT 计算——逐字节喂入构建 CRC；用于 ITU X.25/T.30/HDLC/SDLC 等协议。

本函数属于 `Tc2_Utilities` 库的 `Functions` 类别（PDF 第 4 章）——这一类是不带状态的纯函数集合：CRC / 校验和 / 哈希、字符串与字节流互转、GUID 处理、各种基本类型与传输格式之间的桥接。它们是 PLC 通信、日志、配置文件处理的底层零件，多数在 `Tc2_Standard` 之外补充 Beckhoff 工业自动化场景下的常用工具。

## 2. 接口定义

### VAR_INPUT

```iecst
VAR_INPUT
    value : BYTE;
    crc : WORD;
END_VAR
```

| 名称 | 类型 | 默认值 | 说明（中文） |
|---|---|---|---|
| `value` | `BYTE` | — | 本次喂入的数据字节。 |
| `crc` | `WORD` | — | 初始值（首次喂入用 `16#FFFF` 或 `16#0000`）或上一次的 CRC 结果（链式喂入）。 |

### 返回值

| 类型 | 说明（中文） |
|---|---|
| `WORD` | 详见 §3 行为说明。|

### VAR_OUTPUT

无（本符号是 `FUNCTION`，结果通过返回值传出）。

### 返回值

| 类型 | 说明（中文） |
|---|---|
| `WORD` | 处理完当前字节后的 16 位 CRC 累积值；可作为下一次调用的 `crc` 入参，或在帧尾作为最终校验值。 |

### VAR_OUTPUT

无。

## 3. 行为说明

函数无状态、立即返回。算法：对输入 `value` 用 CRC-16 CCITT 生成多项式 `0x1021`（即 x^16 + x^12 + x^5 + 1）迭代一次——具体实现是查表 / 位移 XOR 组合（PDF 未公开内部表）。**典型用法是链式调用**：第一次传 `16#FFFF` 作初值，后续每次传上一次的返回值作 `crc` 入参——这样最后得到的 WORD 就是整个数据流的 CRC。**适合按字节边到边算 CRC**——如串口收到一个字节立即喂入、不缓存。批量数据请用 `F_DATA_TO_CRC16_CCITT`（内部即按本函数循环）。

## 4. 错误码 / 返回值

返回 `WORD`——具体语义见 §3。错误约定：
- 多数函数无独立错误码，**通过返回值的特殊值（如 0 / 255 / 空串 / `FALSE`）报错**——调用方必须始终判返回值。
- 涉及输出缓冲的函数在缓冲不够时通常截断、返回 `FALSE` 或特殊标记；调用方应**始终把返回值当主要错误信号**。

## 5. 使用注意 / 常见坑

- **初值选 `16#FFFF` 还是 `16#0000` 取决于协议**——ITU-T V.41 用 `0xFFFF`、CRC-CCITT-XMODEM 用 `0x0000`。混用会导致校验不通过。
- **链式调用必须传上次返回值作 crc**——重新传初值意味着 CRC 重新开始。
- **生成多项式固定 `0x1021`**，不可改；其他 CRC（CRC-16/CRC-32/CRC-MODBUS）请用其他函数（如 `F_CheckSum16` 不是 CRC）。
- **批量数据用 `F_DATA_TO_CRC16_CCITT`**——本函数仅单字节、循环喂入。
- 结果是 WORD（16 位）——与协议规定的字节序（大/小端）配合需调用方手动 `SWAP`。
- **CRC ≠ checksum**：CRC 检测错误能力远强于简单累加 checksum（`F_CheckSum16`）。

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_F_BYTE_TO_CRC16_CCITT.TcPOU`](../examples/P_Demo_F_BYTE_TO_CRC16_CCITT.TcPOU)（TwinCAT 3 原生 .TcPOU，可直接拖入 XAE 的 PLC POUs 文件夹）
>
> 导入步骤：右键 PLC 项目下 POUs 文件夹 → Add → Existing Item → 选该文件 → OK
> 详见 [`examples/README.md`](../examples/README.md)

## 7. 业务场景与实际价值

- **场景**：串口协议（如 RDM / HART / DLMS）实时校验：收到每个字节立即喂入 CRC 计算器，到帧尾比对收到的 CRC 字段。
- **价值**：替代手写位移 XOR 循环或维护 256 字节查找表——本函数封装好的 CRC-16 CCITT 实现。
- **替代方案对比**：`F_DATA_TO_CRC16_CCITT`：批量数据；`F_CheckSum16`：弱版本累加 checksum；其他 CRC（CRC-32 等）：库不提供，需自写。

## 8. 参考资料

- **PDF**：[TwinCAT_3_PLC_Lib_Tc2_Utilities_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_Utilities_EN.pdf) 第 4.30 节
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tcplclib_tc2_utilities/35108363.html
- **相关函数**：见同库 `functions/` 目录下其他工具函数
