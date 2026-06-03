# SetFormatOptions

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
| Example | [`examples/P_Demo_FB_JsonSaxPrettyWriter_SetFormatOptions.TcPOU`](../examples/P_Demo_FB_JsonSaxPrettyWriter_SetFormatOptions.TcPOU) |

---

## 1. 功能简述

设置 pretty writer 的输出格式选项（`EJsonPrettyFormatOptions` 枚举位组合，控制换行/对齐等额外排版规则）。

## 2. 接口定义

### VAR_INPUT

```iecst
VAR_INPUT
    options : EJsonPrettyFormatOptions;
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `options` | `EJsonPrettyFormatOptions` | 格式选项枚举（如 `EJsonPrettyFormatOptions` 的位组合）。 |


### VAR_OUTPUT

无。

### VAR_IN_OUT

无。

## 3. 行为说明

配置 pretty writer 的额外排版选项（`EJsonPrettyFormatOptions` 枚举位组合）。可控制换行风格、嵌套对齐规则等额外样式。与 `SetIndent()` 互补：`SetIndent()` 决定缩进字符，本方法决定额外排版规则。调用时机：建议在生成第一个 JSON token 之前调用，避免中途切换风格。本方法属 `FB_JsonSaxPrettyWriter` 的对外 API，调用前需要保证父 FB 实例已成功初始化（`initStatus` 为 `S_OK`）。

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

> 配套可导入文件：[`examples/P_Demo_FB_JsonSaxPrettyWriter_SetFormatOptions.TcPOU`](../examples/P_Demo_FB_JsonSaxPrettyWriter_SetFormatOptions.TcPOU)（TwinCAT 3 原生 .TcPOU，可直接拖入 XAE 的 PLC POUs 文件夹）
>
> 导入步骤：右键 PLC 项目下 POUs 文件夹 → Add → Existing Item → 选该文件 → OK

```iecst
// 详见 examples 目录下的 .TcPOU 文件
```

## 7. 业务场景与实际价值

- **场景**：修改已有 JSON 节点的 FormatOptions 类型值（如更新缓存的实时数据字段）。
- **价值**：DOM 树本地修改不重新构造整个文档，比 GetDocument + 字符串替换效率高。
- **替代方案对比**：重新组建整个 JSON → 大文档时性能差；字符串 Find + Replace → 同名字段容易误改。

## 8. 参考资料

- **PDF**：[`TwinCAT_3_PLC_Lib_Tc3_JsonXml_EN.pdf`](https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc3_JsonXml_EN.pdf) §4.5.33
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tcplclib_tc3_jsonxml/11948988555.html
- **相关 FB / FC**：`FB_JsonSaxPrettyWriter`, `AddFormatOptionsMember`, `GetFormatOptions`
