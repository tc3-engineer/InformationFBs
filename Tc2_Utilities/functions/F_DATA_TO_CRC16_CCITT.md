# F_DATA_TO_CRC16_CCITT

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc2_Utilities` |
| Library Version | `2.18.2` |
| Type | `FUNCTION` |
| Category | `Functions` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_Utilities_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tcplclib_tc2_utilities/35114507.html |
| Verified | 2026-05-12 ✅ |
| InfoSys-checked | ✅ 2026-05-12 |
| Status | `verified` |
| Example | [`examples/P_Demo_F_DATA_TO_CRC16_CCITT.TcPOU`](../examples/P_Demo_F_DATA_TO_CRC16_CCITT.TcPOU) |

---

## 1. 功能简述

批量数据 CRC-16 CCITT 计算——内部循环调用 `F_BYTE_TO_CRC16_CCITT`；一次计算整段数据的 CRC。

本函数属于 `Tc2_Utilities` 库的 `Functions` 类别（PDF 第 4 章）——这一类是不带状态的纯函数集合：CRC / 校验和 / 哈希、字符串与字节流互转、GUID 处理、各种基本类型与传输格式之间的桥接。它们是 PLC 通信、日志、配置文件处理的底层零件，多数在 `Tc2_Standard` 之外补充 Beckhoff 工业自动化场景下的常用工具。

## 2. 接口定义

### VAR_INPUT

```iecst
VAR_INPUT
    pData : POINTER TO BYTE;
    cbData : UDINT;
    crc : WORD;
END_VAR
```

| 名称 | 类型 | 默认值 | 说明（中文） |
|---|---|---|---|
| `pData` | `POINTER TO BYTE` | — | 数据缓冲起始地址。 |
| `cbData` | `UDINT` | — | 数据长度（字节）。 |
| `crc` | `WORD` | — | 初值 = `16#FFFF` 或 `16#0000`（按协议要求）或上一次 CRC（链式块计算）。 |

### 返回值

| 类型 | 说明（中文） |
|---|---|
| `WORD` | 详见 §3 行为说明。|

### VAR_OUTPUT

无（本符号是 `FUNCTION`，结果通过返回值传出）。

### 返回值

| 类型 | 说明（中文） |
|---|---|
| `WORD` | 16 位 CRC 累积值。 |

### VAR_OUTPUT

无。

## 3. 行为说明

函数无状态、立即返回。算法：对 `[pData, pData + cbData)` 范围内每个字节执行 `F_BYTE_TO_CRC16_CCITT(byte, crc)`，把累计结果作为返回值。**等价于手动 FOR 循环 + 单字节函数**，但 1 调用 + 内部优化（可能用 256 项查找表加速）。**链式块计算**：把大数据分块，每块调用本函数时把上块返回值作 `crc` 入参——结果与一次性计算整段相同。**适用于网络帧 / 大文件块的 CRC 校验**。

## 4. 错误码 / 返回值

返回 `WORD`——具体语义见 §3。错误约定：
- 多数函数无独立错误码，**通过返回值的特殊值（如 0 / 255 / 空串 / `FALSE`）报错**——调用方必须始终判返回值。
- 涉及输出缓冲的函数在缓冲不够时通常截断、返回 `FALSE` 或特殊标记；调用方应**始终把返回值当主要错误信号**。

## 5. 使用注意 / 常见坑

- **初值与协议一致**——ITU 用 `0xFFFF`、XMODEM 用 `0x0000`。
- **等价的单字节循环**：`crc := 16#FFFF; FOR i := 0 TO cbData-1 DO crc := F_BYTE_TO_CRC16_CCITT(...); END_FOR;`
- **分块计算**：把大数据按块分批喂，传上次返回值作下次初值——结果与一次性算等价。
- 结果字节序：协议可能规定 big-endian 或 little-endian 传输——`SWAP` 后写入帧尾。
- **生成多项式 `0x1021` 固定**——其他 CRC 不可用此函数。
- **`F_CheckSum16` 是简单 checksum 不是 CRC**——两者强度差异大。

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_F_DATA_TO_CRC16_CCITT.TcPOU`](../examples/P_Demo_F_DATA_TO_CRC16_CCITT.TcPOU)（TwinCAT 3 原生 .TcPOU，可直接拖入 XAE 的 PLC POUs 文件夹）
>
> 导入步骤：右键 PLC 项目下 POUs 文件夹 → Add → Existing Item → 选该文件 → OK
> 详见 [`examples/README.md`](../examples/README.md)

## 7. 业务场景与实际价值

- **场景**：EtherCAT / Modbus-RTU 帧 CRC 校验：收到完整帧后调用本函数计算 CRC，与帧尾 CRC 字段比较。
- **价值**：比手写 256 字节查找表 + 位移 XOR 算法更省事；O(N) 但带库级优化。
- **替代方案对比**：`F_BYTE_TO_CRC16_CCITT`：单字节版本（用于流式喂入）；`F_CheckSum16`：弱 checksum。

## 8. 参考资料

- **PDF**：[TwinCAT_3_PLC_Lib_Tc2_Utilities_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_Utilities_EN.pdf) 第 4.34 节
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tcplclib_tc2_utilities/35114507.html
- **相关函数**：见同库 `functions/` 目录下其他工具函数
