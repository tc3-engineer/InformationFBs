# ResetToDefault

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc3_EventLogger` |
| Library Version | `1.6.2` |
| Type | `METHOD` |
| Category | `FB_TcSourceInfo` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc3_EventLogger_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tcplclib_tc3_eventlogger/5051012491.html |
| Verified | 2026-05-11 ✅ |
| InfoSys-checked | ✅ 2026-05-11 |
| Status | `verified` |
| Example | [`examples/P_Demo_ResetToDefault.TcPOU`](../examples/P_Demo_ResetToDefault.TcPOU) |

---

## 1. 功能简述

`FB_TcSourceInfo.ResetToDefault()` 把 SourceInfo 还原到 EventLogger 的默认值——即使用 PLC 实例的符号路径作为 SourceName。

用于撤销之前的 ExtendName 或自定义 setter 修改，回到"开箱即用"状态。

## 2. 接口定义

### VAR_INPUT

无。

### VAR_OUTPUT

无。

### VAR_IN_OUT

无。

## 3. 行为说明

调用即同步执行：SourceName 重置为 PLC 默认符号路径；SourceID / SourceGuid 重置为默认值。之后传给 alarm 时 EventLogger 用这些默认源信息。

**与 Clear 的区别**：ResetToDefault 显式还原到"EventLogger 提供的默认值"（非空）；Clear 是真的清空字段（变空）。两者最终行为接近——传给 alarm 后 alarm 都用默认源信息——但语义不同。

## 4. 错误码 / 返回值

本方法返回 `HRESULT`（32 位有符号整数）。`SUCCEEDED(hr)` 为 TRUE 表示调用成功。

| HRESULT | 含义 | 处理建议 |
|---|---|---|
| `S_OK` | 已还原到默认 | 继续业务 |
| `其他错误` | ⚠️ PDF 未列详细码 | 查 ADS Return Codes |

## 5. 使用注意 / 常见坑

- ResetToDefault 后丢失之前的 ExtendName 后缀。
- 默认 SourceName 是 PLC 符号路径——动态生成的 alarm 路径可能不唯一。（工程经验补充）
- 用 Reset 还是 Clear 看团队约定——两者实际行为接近。（工程经验补充）

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_ResetToDefault.TcPOU`](../examples/P_Demo_ResetToDefault.TcPOU)（TwinCAT 3 原生 .TcPOU，可直接拖入 XAE 的 PLC POUs 文件夹）
>
> 导入步骤：右键 PLC 项目下 POUs 文件夹 → Add → Existing Item → 选该文件 → OK

```iecst
// 详见 examples 目录下的 .xml 文件
```

## 7. 业务场景与实际价值

测试场景：临时改了 SourceInfo 后用本方法还原到默认


一次调用还原到 EventLogger 默认行为


`Clear` 清空字段；本方法显式还原到默认。两者效果接近


## 8. 参考资料

- **PDF**：[TwinCAT_3_PLC_Lib_Tc3_EventLogger_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc3_EventLogger_EN.pdf) §3.12.3
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tcplclib_tc3_eventlogger/5051012491.html
- **相关**：`FB_TcSourceInfo`, `FB_TcSourceInfo.Clear`, `FB_TcSourceInfo.ExtendName`
