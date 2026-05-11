# finish
## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc2_Utilities` |
| Library Version | `2.18.2` |
| Type | `METHOD` |
| Category | `FB_CalcHashValue` |
| Parent FB | [`FB_CalcHashValue`](FB_CalcHashValue.md) |
| Source | https://infosys.beckhoff.com/content/1033/tcplclib_tc2_utilities/ |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_Utilities_EN.pdf |
| Verified | 2026-05-11 ✅ |
| Status | `verified` |
| Example | [`examples/P_Demo_FB_CalcHashValue_finish.xml`](../examples/P_Demo_FB_CalcHashValue_finish.xml) |

---
## 1. 功能简述

This method performs the hash calculation and outputs the calculated hash value.

## 2. 接口定义

### VAR_INPUT

```iecst
VAR_INPUT
    pHash : PVOID;
    nHash : UDINT;
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `pHash` | `PVOID` | Here the address of the buffer is specified where the hash value is to be stored. |
| `nHash` | `UDINT` | The size of the buffer for the hash value is specified here. The size depends on the hash mode, see also `E_HashMode`. |

### 返回值

⚠️ 待人工确认（PDF 在 finish() 节内**省略了 `METHOD finish : <RET>` 头**，仅给出 VAR_INPUT 与参数表。按 start/update 的模式推断为 `BOOL`，但未在 PDF 中显式声明）。

### VAR_IN_OUT

无。

## 3. 行为说明

- `finish()` 完成 hash 计算并把结果写入调用方提供的缓冲区；
- 缓冲区大小 `nHash` 必须**≥ 所选 hash 模式的输出长度**（详见 `E_HashMode`）；
- 调用 `finish()` 后内部状态被消费；如需重新计算，必须重新 `start()`；
- 详细行为以 PDF 第 3.10 节为准。

## 4. 错误码 / 返回值

⚠️ 返回类型与错误码均未在 PDF 显式列出（参见上面"返回值"说明）。

## 5. 使用注意 / 常见坑

- 必须在 `start()` + 至少一次 `update()` 之后调用；
- `nHash` 小于 hash 长度将导致越界写入（PVOID 类型不检查长度）；
  - SHA-512 → 64 字节
  - SHA-256 → 32 字节
  - 实际长度以 `E_HashMode` 文档为准。

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_FB_CalcHashValue_finish.xml`](../examples/P_Demo_FB_CalcHashValue_finish.xml)
>
> 导入步骤：右键 PLC 项目 → Import PLCopenXML → 选该文件 → OK
> 详见 [`examples/README.md`](../examples/README.md)

```iecst
PROGRAM P_Demo_FB_CalcHashValue_finish
VAR
    fbCalc   : FB_CalcHashValue;
    eMode    : E_HashMode := E_HashMode.HashMode_Sha512;
    sInput   : STRING(255) := 'hello';
    aHash    : ARRAY[0..63] OF BYTE;
    bStart   : BOOL;
    bUpdate  : BOOL;
    bFinish  : BOOL;
END_VAR

// 完整三段调用，重点演示 finish()
bStart  := fbCalc.start(hashMode := eMode);
bUpdate := fbCalc.update(pData := ADR(sInput), nData := LEN(sInput));
bFinish := fbCalc.finish(pHash := ADR(aHash), nHash := SIZEOF(aHash));
// 在线监视 aHash 字节数组
```

## 7. 相关

- 见 [`Tc2_Utilities README`](../README.md) 同库其他条目
- 父 FB：[`FB_CalcHashValue`](FB_CalcHashValue.md)
- 同 FB 其他方法：[`start`](start.md) · [`update`](update.md)

## 8. 待确认项

- `finish` 返回类型未在 PDF 显式给出（⚠️ 待人工对照在线 InfoSys 确认）。
