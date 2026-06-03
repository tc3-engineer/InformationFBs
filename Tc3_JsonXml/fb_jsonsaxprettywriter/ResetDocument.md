# ResetDocument

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc3_JsonXml` |
| Library Version | `1.14.2` |
| Type | `METHOD` |
| Category | `FB_JsonSaxPrettyWriter` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc3_JsonXml_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tcplclib_tc3_jsonxml/11948988555.html |
| Verified | 2026-06-03 ✅ |
| InfoSys-checked | ✅ 2026-06-03 |
| Status | `verified` |
| Example | [`examples/P_Demo_FB_JsonSaxPrettyWriter_ResetDocument.TcPOU`](../examples/P_Demo_FB_JsonSaxPrettyWriter_ResetDocument.TcPOU) |

---

## 1. 功能简述

清空内部 SAX writer 缓冲，准备下一次 JSON 构建。

## 2. 接口定义

### VAR_INPUT

无。

### VAR_OUTPUT

无。

### VAR_IN_OUT

无。

## 3. 行为说明

清空 SAX writer 内部缓冲，准备下一次 JSON 构建。在长时间运行的应用中循环复用 SAX writer 实例时，每轮开始前都应调用本方法，避免老内容被拼到新文档前面。本方法属 `FB_JsonSaxPrettyWriter` 的对外 API，调用前需要保证父 FB 实例已成功初始化（`initStatus` 为 `S_OK`）。如返回值或输出参数不符合预期，可优先检查输入参数有效性，再调 `ExceptionRaised()` / 读 `hrErrorCode` 定位。

## 4. 错误码 / 返回值

本方法返回 `HRESULT`（32 位有符号整数）。`SUCCEEDED(hr)` 为 `TRUE` 表示调用成功。

| HRESULT | 含义 | 处理建议 |
|---|---|---|
| `S_OK` (0) | 操作成功，继续 | 继续下一步 |
| `S_FALSE` (1) | 在 SAX 回调里表示「请求终止解析」 | 让 `Parse()` 立即返回 |
| 其他 (E_*) | 操作失败 | 参考 PDF 第 7 章 ADS Return Codes 表 |

## 5. 使用注意 / 常见坑

- SAX 风格依赖调用顺序：违反 JSON 语法（如对象里无键的值）本 FB 不报错，但输出不是合法 JSON。

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_FB_JsonSaxPrettyWriter_ResetDocument.TcPOU`](../examples/P_Demo_FB_JsonSaxPrettyWriter_ResetDocument.TcPOU)（TwinCAT 3 原生 .TcPOU，可直接拖入 XAE 的 PLC POUs 文件夹）
>
> 导入步骤：右键 PLC 项目下 POUs 文件夹 → Add → Existing Item → 选该文件 → OK

```iecst
// 详见 examples 目录下的 .TcPOU 文件
```

## 7. 业务场景与实际价值

- **场景**：循环复用 SAX writer 实例时，每轮开始前清空缓冲。
- **价值**：一次调用即重置内部状态。
- **替代方案对比**：重新实例化 FB → 浪费；不重置直接续 Add → 内容拼到上一轮后面，输出非法。

## 8. 参考资料

- **PDF**：[`TwinCAT_3_PLC_Lib_Tc3_JsonXml_EN.pdf`](https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc3_JsonXml_EN.pdf) §4.5.32
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tcplclib_tc3_jsonxml/11948988555.html
- **相关 FB / FC**：`FB_JsonSaxPrettyWriter`
