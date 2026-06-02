# F_CheckSum16

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc2_Utilities` |
| Library Version | `2.18.2` |
| Type | `FUNCTION` |
| Category | `Functions` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_Utilities_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tcplclib_tc2_utilities/35109899.html |
| Verified | 2026-05-12 ✅ |
| InfoSys-checked | ✅ 2026-05-12 |
| Status | `verified` |
| Example | [`examples/P_Demo_F_CheckSum16.TcPOU`](../examples/P_Demo_F_CheckSum16.TcPOU) |

---

## 1. 功能简述

16 位 checksum——简单累加和（无生成多项式）；检错能力弱于 CRC，但计算极快。

本函数属于 `Tc2_Utilities` 库的 `Functions` 类别（PDF 第 4 章）——这一类是不带状态的纯函数集合：CRC / 校验和 / 哈希、字符串与字节流互转、GUID 处理、各种基本类型与传输格式之间的桥接。它们是 PLC 通信、日志、配置文件处理的底层零件，多数在 `Tc2_Standard` 之外补充 Beckhoff 工业自动化场景下的常用工具。

## 2. 接口定义

### VAR_INPUT

```iecst
VAR_INPUT
    dwSrcAddr  : POINTER TO BYTE;
    cbLen      : UDINT;
    wChkSum    : WORD;
END_VAR
```

| 名称 | 类型 | 默认值 | 说明（中文） |
|---|---|---|---|
| `dwSrcAddr` | `POINTER TO BYTE` | — | 源数据起始地址；`ADR(buf)`。 |
| `cbLen` | `UDINT` | — | 数据字节数（`SIZEOF`）。 |
| `wChkSum` | `WORD` | — | 初值 = 0 或上一次结果（链式调用）。 |

### 返回值

| 类型 | 说明（中文） |
|---|---|
| `WORD` | 详见 §3 行为说明。|

### VAR_OUTPUT

无（本符号是 `FUNCTION`，结果通过返回值传出）。

### 返回值

| 类型 | 说明（中文） |
|---|---|
| `WORD` | 16 位累加和；后续段可作为下次 `wChkSum` 入参。 |

### VAR_OUTPUT

无。

## 3. 行为说明

函数无状态、立即返回。算法：把 `[dwSrcAddr, dwSrcAddr + cbLen)` 范围内的字节按 16 位累加，每次溢出进位丢弃（mod 0x10000）。`wChkSum` 入参是初值（典型 = 0），或链式调用上次结果。**比 CRC 弱**——只检测奇偶位翻转 + 部分位翻转；多个相同位置位翻转不被检测。**用法**：弱协议（如老设备的简单校验位）或仅做完整性自检（不防恶意攻击）。强校验请用 `F_DATA_TO_CRC16_CCITT`。

## 4. 错误码 / 返回值

返回 `WORD`——具体语义见 §3。错误约定：
- 多数函数无独立错误码，**通过返回值的特殊值（如 0 / 255 / 空串 / `FALSE`）报错**——调用方必须始终判返回值。
- 涉及输出缓冲的函数在缓冲不够时通常截断、返回 `FALSE` 或特殊标记；调用方应**始终把返回值当主要错误信号**。

## 5. 使用注意 / 常见坑

- **比 CRC 弱**——只用在低风险场景。安全/可靠性高场景用 CRC。
- **累加 mod 0x10000**——溢出进位丢弃，所以两段相同字节顺序不同的数据可能得相同 checksum。
- 初值通常 = 0；链式调用传上次返回值。
- **`F_DATA_TO_CRC16_CCITT`** 是首选的 CRC 版本。
- 字节顺序无关（累加是交换律的）——但下游协议可能定字节序，需调用方 SWAP。
- **适合配置文件本地完整性自检**（如 PLC 启动时算 ROM 镜像 checksum）。

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_F_CheckSum16.TcPOU`](../examples/P_Demo_F_CheckSum16.TcPOU)（TwinCAT 3 原生 .TcPOU，可直接拖入 XAE 的 PLC POUs 文件夹）
>
> 导入步骤：右键 PLC 项目下 POUs 文件夹 → Add → Existing Item → 选该文件 → OK
> 详见 [`examples/README.md`](../examples/README.md)

## 7. 业务场景与实际价值

- **场景**：PLC 启动时校验非易失存储中的配方表完整性：算 checksum 并与存储的预期 checksum 比对，不一致则报警。
- **价值**：替代手写累加循环；O(N) 时间但码量最小。
- **替代方案对比**：`F_DATA_TO_CRC16_CCITT`：更强的 CRC-16；`F_GenerateHashValue`：SHA-256/512 用于安全场景。

## 8. 参考资料

- **PDF**：[TwinCAT_3_PLC_Lib_Tc2_Utilities_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_Utilities_EN.pdf) 第 4.31 节
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tcplclib_tc2_utilities/35109899.html
- **相关函数**：见同库 `functions/` 目录下其他工具函数
