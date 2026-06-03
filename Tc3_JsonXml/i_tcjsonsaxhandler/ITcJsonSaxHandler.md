# ITcJsonSaxHandler

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc3_JsonXml` |
| Library Version | `1.14.2` |
| Type | `INTERFACE` |
| Category | `Interface` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc3_JsonXml_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tcplclib_tc3_jsonxml/4219229195.html |
| Verified | 2026-06-03 ✅ |
| InfoSys-checked | ✅ 2026-06-03 |
| Status | `verified` |
| Example | [`examples/P_Demo_ITcJsonSaxHandler.TcPOU`](../examples/P_Demo_ITcJsonSaxHandler.TcPOU) |

---

## 1. 功能简述

`ITcJsonSaxHandler` 是供 `FB_JsonSaxReader` 回调的接口（callback interface）。实现该接口的功能块需要给出 OnBool / OnDint / OnString / OnStartObject / OnEndObject 等全部回调方法。SAX 解析器在扫描 JSON token 流时按顺序调用对应回调；回调返回 `S_OK` 继续，返回 `S_FALSE` 终止解析。

## 2. 接口定义

### VAR_INPUT

无。

### VAR_OUTPUT

无。

### VAR_IN_OUT

无。

## 3. 行为说明

接口本身不维护状态；用户在自定义功能块上实现这一接口后，把功能块实例传给 `FB_JsonSaxReader.Parse()`。解析过程中，扫描到 JSON token（如 `true` / 数字 / 字符串 / `{` / `}` / `[` / `]` / 键名）时，SAX reader 顺序调用对应的 OnXxx 方法把 token 内容传给业务代码。OnBool / OnDint / OnLint / OnLreal / OnString / OnNull 对应基本值；OnStartObject / OnEndObject / OnStartArray / OnEndArray 对应容器边界；OnKey 在解析到键名时触发并把 key 通过 VAR_IN_OUT 传出。所有回调返回 `HRESULT`：`S_OK` 继续、`S_FALSE` 终止。

## 4. 错误码 / 返回值

本功能块/方法无返回值。状态通过 `initStatus` / `bError` / `hrErrorCode` 等输出反馈。

## 5. 使用注意 / 常见坑

- 实例化后先检查 VAR_OUTPUT 中的 `initStatus`，确认 FB 初始化成功（`S_OK`）再调业务方法。（工程经验补充）

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_ITcJsonSaxHandler.TcPOU`](../examples/P_Demo_ITcJsonSaxHandler.TcPOU)（TwinCAT 3 原生 .TcPOU，可直接拖入 XAE 的 PLC POUs 文件夹）
>
> 导入步骤：右键 PLC 项目下 POUs 文件夹 → Add → Existing Item → 选该文件 → OK

```iecst
// 详见 examples 目录下的 .TcPOU 文件
```

## 7. 业务场景与实际价值

- **场景**：自定义 SAX 解析处理逻辑（如过滤特定 key、累计统计）需要实现这个回调接口。
- **价值**：接口标准化让任何业务 FB 都能挂到 SAX reader 上，关注点解耦。
- **替代方案对比**：用 DOM 解析全文然后遍历 → 大文档浪费内存；不实现接口 → 没法用 SAX reader。

## 8. 参考资料

- **PDF**：[`TwinCAT_3_PLC_Lib_Tc3_JsonXml_EN.pdf`](https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc3_JsonXml_EN.pdf) §5.1
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tcplclib_tc3_jsonxml/4219229195.html
- **相关 FB / FC**：`FB_JsonSaxReader`, `ITcJsonSaxValues`
