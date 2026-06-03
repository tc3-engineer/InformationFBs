# GetDocument

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc3_JsonXml` |
| Library Version | `1.14.2` |
| Type | `METHOD` |
| Category | `FB_JsonSaxWriter` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc3_JsonXml_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tcplclib_tc3_jsonxml/4220235275.html |
| Verified | 2026-06-03 ✅ |
| InfoSys-checked | ✅ 2026-06-03 |
| Status | `verified` |
| Example | [`examples/P_Demo_FB_JsonSaxWriter_GetDocument.TcPOU`](../examples/P_Demo_FB_JsonSaxWriter_GetDocument.TcPOU) |

---

## 1. 功能简述

把当前 DOM 内存中的 JSON 文档序列化为 STRING(255) 输出。

## 2. 接口定义

### VAR_INPUT

无。

### VAR_OUTPUT

```iecst
VAR_OUTPUT
    hrErrorCode : HRESULT;
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `hrErrorCode` | `HRESULT` | 操作失败时返回错误码（HRESULT）。`S_OK` (0) = 成功；其他值见附录 ADS Return Codes 表。 |


### VAR_IN_OUT

无。

## 3. 行为说明

把当前 DOM 序列化为 JSON 字符串，拷贝到调用方的 STRING(255) 缓冲。返回写入字节数（不含尾零）；文档过长被截断时也会返回字节数。用于把 DOM 转换为可发送/可保存的字符串形式。本方法属 `FB_JsonSaxWriter` 的对外 API，调用前需要保证父 FB 实例已成功初始化（`initStatus` 为 `S_OK`）。

## 4. 错误码 / 返回值

本方法返回 `STRING(255)` 字符串。

## 5. 使用注意 / 常见坑

- SAX 风格依赖调用顺序：违反 JSON 语法（如对象里无键的值）本 FB 不报错，但输出不是合法 JSON。

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_FB_JsonSaxWriter_GetDocument.TcPOU`](../examples/P_Demo_FB_JsonSaxWriter_GetDocument.TcPOU)（TwinCAT 3 原生 .TcPOU，可直接拖入 XAE 的 PLC POUs 文件夹）
>
> 导入步骤：右键 PLC 项目下 POUs 文件夹 → Add → Existing Item → 选该文件 → OK

```iecst
// 详见 examples 目录下的 .TcPOU 文件
```

## 7. 业务场景与实际价值

- **场景**：拼装完 DOM 后把整份 JSON 拷成 STRING 推到 MQTT broker。
- **价值**：一次调用拿到完整序列化字符串。
- **替代方案对比**：遍历节点自己拼字符串 → 多此一举；用 SAX writer → 流式拼装本来就该用 SAX writer 而非 DOM。

## 8. 参考资料

- **PDF**：[`TwinCAT_3_PLC_Lib_Tc3_JsonXml_EN.pdf`](https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc3_JsonXml_EN.pdf) §4.4.29
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tcplclib_tc3_jsonxml/4220235275.html
- **相关 FB / FC**：`FB_JsonSaxWriter`, `IsDocument`, `SetDocument`
