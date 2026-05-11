# update
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
| Example | [`examples/P_Demo_FB_CalcHashValue_update.xml`](../examples/P_Demo_FB_CalcHashValue_update.xml) |

---
## 1. 功能简述

This method can be called once or multiple times. Input data for the hash calculation is added with each call.

## 2. 接口定义

### VAR_INPUT

```iecst
METHOD update : BOOL
VAR_INPUT
    pData : PVOID;
    nData : UDINT;
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `pData` | `PVOID` | The address of the input data is specified here. |
| `nData` | `UDINT` | The size of the input data in bytes is specified here. |

### 返回值

`BOOL` —— PDF 显式声明为 `METHOD update : BOOL`。

### VAR_IN_OUT

无。

## 3. 行为说明

- `update()` 可被调用一次或多次；每次调用追加一段输入数据到 hash 计算中；
- 必须先调用 `start()` 初始化才能调用本方法；
- 详细行为以 PDF 第 3.10 节为准。

## 4. 错误码 / 返回值

返回 `BOOL`。⚠️ PDF 未列出 FALSE 时的具体错误情景。

## 5. 使用注意 / 常见坑

- `pData` 用 `ADR(<变量>)` 取地址；`nData` 必须是有效字节数（如 `SIZEOF(...)` 或 `LEN(...)` 对应的字节长度）；
- 调用顺序错误（未先 `start`、或 `finish` 之后再 `update`）会导致结果不可预期。

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_FB_CalcHashValue_update.xml`](../examples/P_Demo_FB_CalcHashValue_update.xml)
>
> 导入步骤：右键 PLC 项目 → Import PLCopenXML → 选该文件 → OK
> 详见 [`examples/README.md`](../examples/README.md)

```iecst
PROGRAM P_Demo_FB_CalcHashValue_update
VAR
    fbCalc    : FB_CalcHashValue;
    eMode     : E_HashMode := E_HashMode.HashMode_Sha512;
    sInput    : STRING(255) := 'hello';
    bStart    : BOOL;
    bUpdate   : BOOL;
END_VAR

// 演示 update()：先 start，再 update 一段数据
bStart  := fbCalc.start(hashMode := eMode);
bUpdate := fbCalc.update(pData := ADR(sInput), nData := LEN(sInput));
```

## 7. 相关

- 见 [`Tc2_Utilities README`](../README.md) 同库其他条目
- 父 FB：[`FB_CalcHashValue`](FB_CalcHashValue.md)
- 同 FB 其他方法：[`start`](start.md) · [`finish`](finish.md)

## 8. 待确认项

- 返回 FALSE 的错误情景未列于 PDF（⚠️ 待人工对照 InfoSys）。
