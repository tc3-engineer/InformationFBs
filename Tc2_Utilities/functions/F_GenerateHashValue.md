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

计算 SHA-1 / SHA-256 / SHA-512 / MD5 等密码学哈希值；输出固定长度字节序列。

本函数属于 `Tc2_Utilities` 库的 `Functions` 类别（PDF 第 4 章）——这一类是不带状态的纯函数集合：CRC / 校验和 / 哈希、字符串与字节流互转、GUID 处理、各种基本类型与传输格式之间的桥接。它们是 PLC 通信、日志、配置文件处理的底层零件，多数在 `Tc2_Standard` 之外补充 Beckhoff 工业自动化场景下的常用工具。

## 2. 接口定义

### VAR_INPUT

```iecst
VAR_INPUT
    hashMode : E_HashMode;
    pData : PVOID;
    nData : UDINT;
    pHash : PVOID;
    nHash : UDINT;
END_VAR
```

| 名称 | 类型 | 默认值 | 说明（中文） |
|---|---|---|---|
| `hashMode` | `E_HashMode` | — | 哈希算法选择：`SHA1` / `SHA256` / `SHA384` / `SHA512` / `MD5` 等（详见 `E_HashMode` 枚举）。 |
| `pData` | `PVOID` | — | 源数据起始地址。 |
| `nData` | `UDINT` | — | 源数据字节数。 |
| `pHash` | `PVOID` | — | 目标 hash 输出缓冲地址。 |
| `nHash` | `UDINT` | — | 目标缓冲字节数——必须匹配选择的算法（SHA-256 = 32、SHA-512 = 64、MD5 = 16 等）。 |

### 返回值

| 类型 | 说明（中文） |
|---|---|
| `BOOL` | 详见 §3 行为说明。|

### VAR_OUTPUT

无（本符号是 `FUNCTION`，结果通过返回值传出）。

### 返回值

| 类型 | 说明（中文） |
|---|---|
| `BOOL` | `TRUE` = 哈希算成功，已写入 `pHash`；`FALSE` = 参数错误（`nHash` 与算法长度不符 / 空指针 / 不支持的算法）。 |

### VAR_OUTPUT

无。

## 3. 行为说明

函数无状态、立即返回。算法：根据 `hashMode` 选择对应的密码学哈希函数（SHA 系列 / MD5 等），对 `[pData, pData + nData)` 范围内的字节做单遍计算，输出固定长度的 hash 到 `pHash` 起始的 `nHash` 字节。**`nHash` 必须严格等于算法输出长度**——MD5 = 16 字节、SHA-1 = 20、SHA-256 = 32、SHA-384 = 48、SHA-512 = 64；不匹配返回 `FALSE`。**用途**：文件完整性校验、配方版本指纹、API 签名（对应 secret + payload → HMAC，本库可能不直接支持需自行扩展）、内部缓存键。

## 4. 错误码 / 返回值

返回 `BOOL`——具体语义见 §3。错误约定：
- 多数函数无独立错误码，**通过返回值的特殊值（如 0 / 255 / 空串 / `FALSE`）报错**——调用方必须始终判返回值。
- 涉及输出缓冲的函数在缓冲不够时通常截断、返回 `FALSE` 或特殊标记；调用方应**始终把返回值当主要错误信号**。

## 5. 使用注意 / 常见坑

- **`nHash` 必须严格匹配算法长度**——SHA-256 = 32、SHA-512 = 64、MD5 = 16。错传返回 `FALSE`。
- **MD5 / SHA-1 已知有碰撞漏洞**——不要用于密码学签名 / 反伪造场景。SHA-256 起步。
- **密码哈希应该用 PBKDF2 / bcrypt / Argon2**——本函数是裸 hash，密码场景需 salt + 多轮迭代。
- **返回 `FALSE`** 通常意味着参数错误（缓冲不匹配、算法不支持）；调用方必检。
- **版本要求**：`Tc2_Utilities >= 3.3.51.0`，TwinCAT 3.1.4024.29 以上。
- **HMAC** 本函数不直接支持——需要业务侧组合 inner/outer pad 实现。

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_F_GenerateHashValue.xml`](../examples/P_Demo_F_GenerateHashValue.xml)（PLCopenXML，可直接导入 TwinCAT 3 XAE）
>
> 导入步骤：右键 PLC 项目 → Import PLCopenXML → 选该文件 → OK
> 详见 [`examples/README.md`](../examples/README.md)

## 7. 业务场景与实际价值

- **场景**：OTA 固件升级：算 SHA-256 比对厂家签名，确认固件包未被篡改。
- **价值**：替代手动实现 SHA 算法（数百行 C 移植）；本函数提供库级密码学哈希。
- **替代方案对比**：`F_DATA_TO_CRC16_CCITT`：弱版本（仅 16 位校验）；`F_CheckSum16`：极弱累加。安全场景必须密码哈希。

## 8. 参考资料

- **PDF**：[TwinCAT_3_PLC_Lib_Tc2_Utilities_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_Utilities_EN.pdf) 第 4.36 节
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tcplclib_tc2_utilities/12674358283.html
- **相关函数**：见同库 `functions/` 目录下其他工具函数
