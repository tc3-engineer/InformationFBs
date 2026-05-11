# start
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
| Example | [`examples/P_Demo_FB_CalcHashValue_start.xml`](../examples/P_Demo_FB_CalcHashValue_start.xml) |

---
## 1. 功能简述

This method initializes the hash calculation with the specified hash mode.

## 2. 接口定义

### VAR_INPUT

```iecst
METHOD start : BOOL
VAR_INPUT
    hashMode : E_HashMode;
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `hashMode` | `E_HashMode` | A hash mode, such as SHA 512, is specified here. See `E_HashMode`. |

### 返回值

`BOOL` —— PDF 显式声明为 `METHOD start : BOOL`。

### VAR_IN_OUT

无。

## 3. 行为说明

- 调用 `start()` 是计算 hash 的**第一步**，给定 hash 模式（如 SHA 512）；
- 之后必须按顺序调用 `update()`（可多次）和 `finish()`；
- 详细行为以 PDF 第 3.10 节为准（⚠️ 错误条件未显式列出）。

## 4. 错误码 / 返回值

返回 `BOOL`。⚠️ PDF 未列出 FALSE 时的具体错误情景，请对照 InfoSys 进一步细化。

## 5. 使用注意 / 常见坑

- 重新计算 hash 之前必须重新调用 `start()` 以重置内部状态。
- `hashMode` 必须是 `E_HashMode` 枚举中的合法值。

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_FB_CalcHashValue_start.xml`](../examples/P_Demo_FB_CalcHashValue_start.xml)
>
> 导入步骤：右键 PLC 项目 → Import PLCopenXML → 选该文件 → OK
> 详见 [`examples/README.md`](../examples/README.md)

```iecst
PROGRAM P_Demo_FB_CalcHashValue_start
VAR
    fbCalc    : FB_CalcHashValue;
    eMode     : E_HashMode := E_HashMode.HashMode_Sha512;
    bStartOk  : BOOL;
END_VAR

// 仅演示 start() 初始化；完整三段调用见 FB_CalcHashValue.md 顶层例程
bStartOk := fbCalc.start(hashMode := eMode);
```

## 7. 相关

- 见 [`Tc2_Utilities README`](../README.md) 同库其他条目
- 父 FB：[`FB_CalcHashValue`](FB_CalcHashValue.md)
- 同 FB 其他方法：[`update`](update.md) · [`finish`](finish.md)

## 8. 待确认项

- 返回 FALSE 的错误情景未列于 PDF（⚠️ 待人工对照 InfoSys）。
