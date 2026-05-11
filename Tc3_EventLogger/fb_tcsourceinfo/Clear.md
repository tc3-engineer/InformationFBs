# Clear

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc3_EventLogger` |
| Library Version | `1.6.2` |
| Type | `METHOD` |
| Category | `FB_TcSourceInfo` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc3_EventLogger_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tcplclib_tc3_eventlogger/5050985483.html |
| Verified | 2026-05-11 ✅ |
| InfoSys-checked | ✅ 2026-05-11 |
| Status | `verified` |
| Example | [`examples/P_Demo_FB_TcSourceInfo_Clear.xml`](../examples/P_Demo_FB_TcSourceInfo_Clear.xml) |

---

## 1. 功能简述

`FB_TcSourceInfo.Clear()` 清空 SourceInfo 的全部字段（SourceName / SourceID / SourceGuid 都置为默认/空）。

用于重置 SourceInfo 实例准备复用，或确保 alarm 使用 EventLogger 的默认源信息。

## 2. 接口定义

### VAR_INPUT

无。

### VAR_OUTPUT

无。

### VAR_IN_OUT

无。

## 3. 行为说明

调用一次清空三字段：SourceName 变空串、SourceID 变 0、SourceGuid 变全 0。之后传给 alarm.Create() 时 EventLogger 视为「无自定义源信息」，回退到默认（PLC 符号路径）。

**与 ResetToDefault 的区别**：Clear 真的清空（让字段为空）；ResetToDefault 是显式还原到 EventLogger 默认值。实际效果接近，但语义上 Clear 更适合"准备重新填写"，ResetToDefault 适合"我就要默认"。

## 4. 错误码 / 返回值

本方法返回 `HRESULT`（32 位有符号整数）。`SUCCEEDED(hr)` 为 TRUE 表示调用成功。

| HRESULT | 含义 | 处理建议 |
|---|---|---|
| `S_OK` | 字段已清空 | 可重新填写或直接传给 alarm 用默认 |
| `其他错误` | ⚠️ PDF 未列详细码 | 查 ADS Return Codes |

## 5. 使用注意 / 常见坑

- Clear 后 SourceInfo 是空——传给 alarm 后 alarm 用默认源信息（PLC 符号路径）。
- Clear 与 ResetToDefault 语义相近，混用 OK 但建议保持一致风格。（工程经验补充）
- 不要在运行中清空已被多个 alarm 引用的 SourceInfo——会让那些 alarm 失去来源信息。（工程经验补充）

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_FB_TcSourceInfo_Clear.xml`](../examples/P_Demo_FB_TcSourceInfo_Clear.xml)（PLCopenXML，可直接导入 TwinCAT 3 XAE）
>
> 导入步骤：右键 PLC 项目 → Import PLCopenXML → 选该文件 → OK

```iecst
// 详见 examples 目录下的 .xml 文件
```

## 7. 业务场景与实际价值

复用 FB_TcSourceInfo 实例：清空后重新填字段用于不同 alarm


支持 SourceInfo 实例的复用，节省资源


`ResetToDefault` → 还原到默认；本方法清空字段（语义不同）


## 8. 参考资料

- **PDF**：[TwinCAT_3_PLC_Lib_Tc3_EventLogger_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc3_EventLogger_EN.pdf) §3.12.1
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tcplclib_tc3_eventlogger/5050985483.html
- **相关**：`FB_TcSourceInfo.ResetToDefault`, `FB_TcSourceInfo.ExtendName`
