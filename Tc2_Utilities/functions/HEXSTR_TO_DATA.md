# HEXSTR_TO_DATA

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc2_Utilities` |
| Library Version | `2.18.2` |
| Type | `FUNCTION` |
| Category | `Functions` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_Utilities_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tcplclib_tc2_utilities/35140619.html |
| Verified | 2026-05-12 ✅ |
| InfoSys-checked | ✅ 2026-05-12 |
| Status | `verified` |
| Example | [`examples/P_Demo_HEXSTR_TO_DATA.xml`](../examples/P_Demo_HEXSTR_TO_DATA.xml) |

---

## 1. 功能简述

把 hex 字符串解析为字节流——`HEXSTR_TO_DATA2` 的旧版（无显式 nDstSize 内部检查较弱）；只允许空格作分隔；遇错返回 0。

本函数属于 `Tc2_Utilities` 库的 `Functions` 类别（PDF 第 4 章）——这一类是不带状态的纯函数集合：CRC / 校验和 / 哈希、字符串与字节流互转、GUID 处理、各种基本类型与传输格式之间的桥接。它们是 PLC 通信、日志、配置文件处理的底层零件，多数在 `Tc2_Standard` 之外补充 Beckhoff 工业自动化场景下的常用工具。

## 2. 接口定义

### VAR_INPUT

```iecst
VAR_INPUT
    sHex : T_MaxString;
    pData : POINTER TO BYTE;
    cbData : UDINT;
END_VAR
```

| 名称 | 类型 | 默认值 | 说明（中文） |
|---|---|---|---|
| `sHex` | `T_MaxString` | — | 源 hex 字符串（例 `'AB CD 01 23'`）。 |
| `pData` | `POINTER TO BYTE` | — | 目标缓冲首地址（`ADR(buf)`）。 |
| `cbData` | `UDINT` | — | 目标缓冲字节数（`SIZEOF(buf)`）。 |

### 返回值

| 类型 | 说明（中文） |
|---|---|
| `UDINT` | 详见 §3 行为说明。|

### VAR_OUTPUT

无（本符号是 `FUNCTION`，结果通过返回值传出）。

## 3. 行为说明

函数无状态、立即返回。算法：扫描 `sHex`，每对 hex 字符（带或不带单空格分隔）解码为 1 字节写入 `pData`。**只允许空格作分隔符**——其它字符（制表、连字符、逗号）视为错误。**遇错立即返 0**，不返回部分结果。`cbData` 是目标缓冲容量上限；扫满即停。**生产新代码建议用 `HEXSTR_TO_DATA2`**——后者错误处理一致、有显式 `nDstSize` 保护。

## 4. 错误码 / 返回值

返回 `UDINT`——具体语义见 §3。错误约定：
- 多数函数无独立错误码，**通过返回值的特殊值（如 0 / 255 / 空串 / `FALSE`）报错**——调用方必须始终判返回值。
- 涉及输出缓冲的函数在缓冲不够时通常截断、返回 `FALSE` 或特殊标记；调用方应**始终把返回值当主要错误信号**。

## 5. 使用注意 / 常见坑

- **只接受空格作分隔符**；其他字符 → 错。预处理用 `FindAndReplaceChar` 把别的字符换为空格。
- **遇错返 0**——业务侧 `nLen > 0` 判合法。
- **生产新代码用 `HEXSTR_TO_DATA2`**（PDF 4.2.13）——新版语义更清晰。
- **大小写都接受**（`'af'` / `'AF'` / `'aF'`）。
- **对称函数 `DATA_TO_HEXSTR`**（PDF 4.22）。
- **`sHex` 是 STRING——上限 255 字符**；更长 hex 串用 `HEXSTR_TO_DATA2`（POINTER 输入）。

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_HEXSTR_TO_DATA.xml`](../examples/P_Demo_HEXSTR_TO_DATA.xml)（PLCopenXML，可直接导入 TwinCAT 3 XAE）
>
> 导入步骤：右键 PLC 项目 → Import PLCopenXML → 选该文件 → OK
> 详见 [`examples/README.md`](../examples/README.md)

## 7. 业务场景与实际价值

- **场景**：从配置文件 / HMI 输入读出的 hex 字符串写入 EtherCAT 配置区。
- **价值**：基础 hex 解析；新代码迁移到 `HEXSTR_TO_DATA2`。
- **替代方案对比**：`HEXSTR_TO_DATA2`：新版无 255 限制；手写循环 + `HEXCHRNIBBLE_TO_BYTE`：细粒度控制但繁琐。

## 8. 参考资料

- **PDF**：[TwinCAT_3_PLC_Lib_Tc2_Utilities_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_Utilities_EN.pdf) 第 4.49 节
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tcplclib_tc2_utilities/35140619.html
- **相关函数**：见同库 `functions/` 目录下其他工具函数
