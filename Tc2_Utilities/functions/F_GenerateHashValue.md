# F_GenerateHashValue
## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc2_Utilities` |
| Library Version | `2.18.2` |
| Type | `FUNCTION` |
| Category | `Functions` |
| Source | https://infosys.beckhoff.com/content/1033/tcplclib_tc2_utilities/ |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_Utilities_EN.pdf |
| Verified | 2026-05-10 ✅ |
| Status | `verified` |
| Example | [`examples/P_Demo_F_GenerateHashValue.xml`](../examples/P_Demo_F_GenerateHashValue.xml) |

---
## 1. 功能简述

**计算哈希值**：支持 SHA-256/384/512/MD5 等（详见 `E_HashMode`）。`nHash` 必须等于所选算法输出长度。

## 2. 接口定义

### VAR_INPUT

```iecst
FUNCTION F_GenerateHashValue : BOOL
VAR_INPUT
    hashMode : E_HashMode;
    pData : PVOID;
    nData : UDINT;
    pHash : PVOID; (* destination buffer for generated hash value *)
    nHash : UDINT; (* size of destination buffer in bytes. This needs to match the hash mode. *)
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `hashMode` | `E_HashMode` | 哈希算法（SHA-512 等，见 E_HashMode） |
| `pData` | `PVOID` | 输入数据地址 |
| `nData` | `UDINT` | 输入字节数 |
| `pHash` | `PVOID` | 输出 hash 缓冲 |
| `nHash` | `UDINT` | 输出缓冲字节数（必须匹配 hash 模式） |

### 返回值

`BOOL` —— 函数计算结果。

### VAR_IN_OUT

无。

## 3. 行为说明

- 见上方功能简述。

## 4. 错误码 / 返回值

返回 `BOOL`。

## 5. 使用注意 / 常见坑

- **输出缓冲长度必须严格匹配 hash 算法的输出大小**——错配返回 FALSE。
- MD5 = 16 B、SHA-256 = 32 B、SHA-512 = 64 B 等。

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_F_GenerateHashValue.xml`](../examples/P_Demo_F_GenerateHashValue.xml)
>
> 详见 [`examples/README.md`](../examples/README.md)

```iecst
PROGRAM P_Demo_F_GenerateHashValue
VAR
    rResult : BOOL;
    bRun    : BOOL;
    sIn : STRING := 'hello';
    aHash : ARRAY[0..31] OF BYTE;
END_VAR

IF bRun THEN
    rResult := F_GenerateHashValue(E_HashMode.eHashMode_SHA256, ADR(sIn), LEN(sIn), ADR(aHash), SIZEOF(aHash));
    bRun := FALSE;
END_IF;
```

## 7. 相关

- 见 [`Tc2_Utilities README`](../README.md) 同库其他条目

## 8. 待确认项

无。
