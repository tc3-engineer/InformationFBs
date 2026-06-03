# FB_JsonSaxPrettyWriter

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc3_JsonXml` |
| Library Version | `1.14.2` |
| Type | `FUNCTION_BLOCK` |
| Category | `Function block` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc3_JsonXml_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tcplclib_tc3_jsonxml/11948988555.html |
| Verified | 2026-06-03 ✅ |
| InfoSys-checked | ✅ 2026-06-03 |
| Status | `verified` |
| Example | [`examples/P_Demo_FB_JsonSaxPrettyWriter.TcPOU`](../examples/P_Demo_FB_JsonSaxPrettyWriter.TcPOU) |

---

## 1. 功能简述

`FB_JsonSaxPrettyWriter` 与 `FB_JsonSaxWriter` 接口完全一致，区别是在生成的 JSON 文档中插入缩进与换行，提升可读性。Configure() 方法可自定义缩进字符（空格/制表符/换行符等）。适合调试输出或人工查看的场景；正式传输用 `FB_JsonSaxWriter` 体积更小。

## 2. 接口定义

### VAR_INPUT

无。

### VAR_OUTPUT

```iecst
VAR_OUTPUT
    initStatus : HRESULT;
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `initStatus` | `HRESULT` | 功能块实例化结果。`S_OK` 表示初始化成功；其他 HRESULT 表示失败，参考 ADS Return Codes。 |


### VAR_IN_OUT

无。

## 3. 行为说明

用法与 `FB_JsonSaxWriter` 完全相同。差异在内部：每次 `AddKey/AddString/StartObject/EndObject` 后自动插入可配置的缩进字符与换行，生成可读性更好的 JSON。可调用 `Configure(indentChar, indentCharCount, lineBreak)` 自定义缩进字符（如空格 vs 制表符）、缩进字符数（如 2 vs 4）、行尾换行符（如 `$N` vs `$R$N`）。未调 `Configure()` 时使用默认配置（4 空格 + LF）。选型：调试日志/配置文件 → 本 FB；MQTT/HTTP 传输 → `FB_JsonSaxWriter`。

## 4. 错误码 / 返回值

本功能块/方法无返回值。状态通过 `initStatus` / `bError` / `hrErrorCode` 等输出反馈。

## 5. 使用注意 / 常见坑

- 实例化后先检查 VAR_OUTPUT 中的 `initStatus`，确认 FB 初始化成功（`S_OK`）再调业务方法。（工程经验补充）

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_FB_JsonSaxPrettyWriter.TcPOU`](../examples/P_Demo_FB_JsonSaxPrettyWriter.TcPOU)（TwinCAT 3 原生 .TcPOU，可直接拖入 XAE 的 PLC POUs 文件夹）
>
> 导入步骤：右键 PLC 项目下 POUs 文件夹 → Add → Existing Item → 选该文件 → OK

```iecst
// 详见 examples 目录下的 .TcPOU 文件
```

## 7. 业务场景与实际价值

- **场景**：调试 PLC ↔ 后端联调时把生成的 JSON 落盘成可读文件，方便 grep / diff。
- **价值**：在 `FB_JsonSaxWriter` 基础上自动加缩进换行，调用代码完全相同。
- **替代方案对比**：用 `FB_JsonSaxWriter` 自己后处理插换行 → 复杂；用外部 jq 美化 → 多一道流程。

## 8. 参考资料

- **PDF**：[`TwinCAT_3_PLC_Lib_Tc3_JsonXml_EN.pdf`](https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc3_JsonXml_EN.pdf) §4.5
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tcplclib_tc3_jsonxml/11948988555.html
- **相关 FB / FC**：`FB_JsonSaxWriter`
