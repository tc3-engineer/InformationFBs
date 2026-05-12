# F_GenerateHashValue

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc2_Utilities` |
| Library Version | `2.18.2` |
| Min Lib Version | `3.3.51.0` |
| Type | `FUNCTION` |
| Category | `Functions` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_Utilities_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tcplclib_tc2_utilities/12674358283.html |
| Verified | 2026-05-12 ✅ |
| InfoSys-checked | ✅ 2026-05-12 |
| Status | `verified` |
| Example | [`examples/P_Demo_F_GenerateHashValue.xml`](../examples/P_Demo_F_GenerateHashValue.xml) |

---

## 1. 功能简述

按指定算法（`E_HashMode`，常用 SHA-1 / SHA-256 / SHA-512）对一段数据 buffer 计算密码学哈希值，结果写入用户提供的目标 buffer。一次性算完，无需流式 init/update/final 模板；若分批数据要累积哈希，请改用 `FB_CalcHashValue`（功能块版，支持多次 `Add()` 后再 `Calc()`）。

适合"数据已全部到位、需要一次性指纹"的场景：配方文件指纹、固件下发后的完整性自校、retain 数据快照防篡改。返回 `TRUE` 表示算成功；`FALSE` 表示参数错误（最常见原因：`nHash` 与算法不匹配，例如 SHA-256 要传 32 字节 buffer 但传了 28）。

## 2. 接口定义

### VAR_INPUT

```iecst
VAR_INPUT
    hashMode : E_HashMode;
    pData    : PVOID;
    nData    : UDINT;
    pHash    : PVOID;    // destination buffer for generated hash value
    nHash    : UDINT;    // size of destination buffer in bytes. This needs to match the hash mode.
END_VAR
```

| 名称 | 类型 | 默认值 | 说明（中文） |
|---|---|---|---|
| `hashMode` | `E_HashMode` | — | 哈希算法选择枚举（如 SHA-1、SHA-256、SHA-512；具体枚举值见 `E_HashMode`）。 |
| `pData` | `PVOID` | — | 输入数据起始地址。 |
| `nData` | `UDINT` | — | 输入数据字节数。 |
| `pHash` | `PVOID` | — | 目标 buffer 起始地址，函数把哈希值写入此处。 |
| `nHash` | `UDINT` | — | 目标 buffer 字节数；必须与算法匹配（SHA-1 = 20、SHA-256 = 32、SHA-512 = 64）。不匹配则函数失败返回 `FALSE`。 |

### VAR_IN_OUT

无。

### 返回值

| 类型 | 说明（中文） |
|---|---|
| `BOOL` | `TRUE` = 哈希算成功，已写入 `pHash`；`FALSE` = 参数错误（`nHash` 与算法长度不符 / 空指针 / 不支持的算法）。 |

### VAR_OUTPUT

无。

## 3. 行为说明

函数按 `hashMode` 调对应算法对 `[pData, pData+nData)` 区段计算密码学哈希，把 N 字节结果写到 `pHash`（N 由算法定，必须等于 `nHash`）。

算法长度对照（典型值）：
- SHA-1：20 字节
- SHA-256：32 字节
- SHA-512：64 字节
具体枚举值与对应字节数见 `E_HashMode` 章节。

关键性质：
- **一次性**：本函数不支持流式分批；要边收边算用 `FB_CalcHashValue` 的 `Add()` + `Calc()`。
- **密码学强度**：碰撞难度由算法决定，SHA-256/SHA-512 实用上抗碰撞；不要再用 MD5/SHA-1 做安全检测（虽然 PDF 可能列出 SHA-1，是历史兼容）。
- **`nHash` 不匹配即失败**：返回 `FALSE`，目标 buffer 不动；调用方要保证 buffer 大小正确。

InfoSys 强调："如果不需要多次添加输入数据，建议用 `F_GenerateHashValue()` 而不是 `FB_CalcHashValue`"——本函数性能更直接，无 FB 实例开销。

## 4. 错误码 / 返回值

| 返回值 | 含义 |
|---|---|
| `TRUE` | 成功；`pHash` 指向的 buffer 含哈希值 |
| `FALSE` | 失败：`nHash` 与算法长度不符 / `pData` 或 `pHash` 空 / 不支持的 `hashMode` |

## 5. 使用注意 / 常见坑

- **`nHash` 必须等于算法的输出长度**：SHA-256 = 32 字节，传 16 / 28 都返回 `FALSE`。
- **不要再用 MD5/SHA-1 做安全验证**：仅作完整性指纹时勉强可接受；安全上下文必须 SHA-256/SHA-512。
- **流式数据用 `FB_CalcHashValue`**：多个 `Add()` 后再 `Calc()`；本函数一次性，分批用不了。
- **`nData = 0`**：仍可调用，得到"空输入"的哈希值（SHA-256 空串 = `e3b0c4...`）；调用方可借此判一致性。
- **要求库版本 `>= 3.3.51.0`**：早版本无本函数；CCS 显示 "F_GenerateHashValue undefined" 时升级 Tc2_Utilities（工程经验补充）。

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_F_GenerateHashValue.xml`](../examples/P_Demo_F_GenerateHashValue.xml)（PLCopenXML，可直接导入 TwinCAT 3 XAE）
>
> 详见 [`examples/README.md`](../examples/README.md)

```iecst
PROGRAM P_Demo_F_GenerateHashValue
VAR
    sFirmware  : T_MaxString := 'firmware_v2.1.0_release';
    arSha256   : ARRAY[0..31] OF BYTE;   // SHA-256 输出固定 32 字节
    bSucceeded : BOOL;
END_VAR

bSucceeded := F_GenerateHashValue(
    hashMode := E_HashMode.SHA256,
    pData    := ADR(sFirmware),
    nData    := LEN(sFirmware),
    pHash    := ADR(arSha256),
    nHash    := SIZEOF(arSha256));
```

## 7. 业务场景与实际价值

- **场景**：固件包下发到 PLC 后做完整性自检——把固件二进制 + 厂商签名一起读出，本函数算 SHA-256 与厂商签名内嵌的哈希比对，不一致就拒绝运行新固件。
- **价值**：替代手写 SHA 算法（200+ 行汇编级位运算）；Beckhoff 已验证，性能与底层 CryptoAPI 一致。
- **替代方案对比**：
  - 手写 SHA-256：200+ 行，几乎不可能调对
  - 用 `F_CheckSum16` 当指纹：强度太低，不抗篡改
  - 用 `F_DATA_TO_CRC16_CCITT`：抗篡改强度低于 SHA
  - 流式用 `FB_CalcHashValue`：分块累积场景
  - 本函数：一次性场景的最佳选择

## 8. 参考资料

- **PDF**：[TwinCAT_3_PLC_Lib_Tc2_Utilities_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_Utilities_EN.pdf) 第 4.36 节
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tcplclib_tc2_utilities/12674358283.html
- **相关 FB / 类型**：`FB_CalcHashValue`（流式累积版）、`E_HashMode`（算法枚举）、`PVOID`（通用指针类型）
