# SetIndent

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
| Example | [`examples/P_Demo_FB_JsonSaxPrettyWriter_SetIndent.TcPOU`](../examples/P_Demo_FB_JsonSaxPrettyWriter_SetIndent.TcPOU) |

---

## 1. 功能简述

为 pretty writer 设置缩进字符（指定字符的 ASCII 码 + 重复次数）。如 `SetIndent(32, 2)` 表示用 2 个空格作为每层缩进。

## 2. 接口定义

### VAR_INPUT

```iecst
VAR_INPUT
    indentChar : SINT;
    indentCharCount : UDINT;
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `indentChar` | `SINT` | 缩进字符的 ASCII 编码（如 `32` = 空格，`9` = Tab）。 |
| `indentCharCount` | `UDINT` | 每层缩进重复多少个 `indentChar`（如 2 / 4）。 |


### VAR_OUTPUT

无。

### VAR_IN_OUT

无。

## 3. 行为说明

为 pretty writer 配置缩进风格。`indentChar` 是字符的 ASCII 编码（32 = 空格、9 = Tab），`indentCharCount` 是每层缩进重复多少个该字符。例如 `SetIndent(32, 2)` 输出 2 空格缩进，`SetIndent(9, 1)` 输出单 Tab 缩进。调用时机：在生成第一个 JSON token 之前调用一次；中途修改会让前后部分缩进风格不一致。未调用 `SetIndent()` 时使用 4 空格 + LF 换行的默认配置。

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

> 配套可导入文件：[`examples/P_Demo_FB_JsonSaxPrettyWriter_SetIndent.TcPOU`](../examples/P_Demo_FB_JsonSaxPrettyWriter_SetIndent.TcPOU)（TwinCAT 3 原生 .TcPOU，可直接拖入 XAE 的 PLC POUs 文件夹）
>
> 导入步骤：右键 PLC 项目下 POUs 文件夹 → Add → Existing Item → 选该文件 → OK

```iecst
// 详见 examples 目录下的 .TcPOU 文件
```

## 7. 业务场景与实际价值

- **场景**：修改已有 JSON 节点的 Indent 类型值（如更新缓存的实时数据字段）。
- **价值**：DOM 树本地修改不重新构造整个文档，比 GetDocument + 字符串替换效率高。
- **替代方案对比**：重新组建整个 JSON → 大文档时性能差；字符串 Find + Replace → 同名字段容易误改。

## 8. 参考资料

- **PDF**：[`TwinCAT_3_PLC_Lib_Tc3_JsonXml_EN.pdf`](https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc3_JsonXml_EN.pdf) §4.5.34
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tcplclib_tc3_jsonxml/11948988555.html
- **相关 FB / FC**：`FB_JsonSaxPrettyWriter`, `AddIndentMember`, `GetIndent`
