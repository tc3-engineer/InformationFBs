# FB_JsonSaxReader

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc3_JsonXml` |
| Library Version | `1.14.2` |
| Type | `FUNCTION_BLOCK` |
| Category | `Function block` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc3_JsonXml_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tcplclib_tc3_jsonxml/4220233355.html |
| Verified | 2026-06-03 ✅ |
| InfoSys-checked | ✅ 2026-06-03 |
| Status | `verified` |
| Example | [`examples/P_Demo_FB_JsonSaxReader.TcPOU`](../examples/P_Demo_FB_JsonSaxReader.TcPOU) |

---

## 1. 功能简述

`FB_JsonSaxReader` 是基于 SAX（Simple API for XML，借用到 JSON）的流式 JSON 解析器。不在内存里建 DOM，而是按 token 顺序触发回调（OnBool / OnString / OnStartObject ...），通过实现 `ITcJsonSaxHandler` 或 `ITcJsonSaxValues` 接口接收事件。适合大文档低内存解析或事件驱动的处理流程。

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

SAX 解析器，不维护 DOM。调用 `Parse()` 方法传入完整 JSON 字符串及一个实现 `ITcJsonSaxHandler` 的对象，解析器按 token 顺序回调 OnBool / OnDint / OnString / OnStartObject / OnEndObject 等方法。回调内部返回 `S_OK` 继续扫描、返回 `S_FALSE` 立刻终止解析。`ParseValues()` 与 `Parse()` 类似，但回调实现的是 `ITcJsonSaxValues` 接口，每个回调多带嵌套 level 和路径信息。内存占用与文档大小弱相关、与嵌套深度强相关，适合大文档流式处理。

## 4. 错误码 / 返回值

本功能块/方法无返回值。状态通过 `initStatus` / `bError` / `hrErrorCode` 等输出反馈。

## 5. 使用注意 / 常见坑

- 实例化后先检查 VAR_OUTPUT 中的 `initStatus`，确认 FB 初始化成功（`S_OK`）再调业务方法。（工程经验补充）

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_FB_JsonSaxReader.TcPOU`](../examples/P_Demo_FB_JsonSaxReader.TcPOU)（TwinCAT 3 原生 .TcPOU，可直接拖入 XAE 的 PLC POUs 文件夹）
>
> 导入步骤：右键 PLC 项目下 POUs 文件夹 → Add → Existing Item → 选该文件 → OK

```iecst
// 详见 examples 目录下的 .TcPOU 文件
```

## 7. 业务场景与实际价值

- **场景**：解析超大 JSON 日志（几 MB 起），全文加载 DOM 会爆 router 内存。
- **价值**：事件驱动的回调机制按 token 流处理，内存占用只与嵌套深度相关而非文档大小。
- **替代方案对比**：用 `FB_JsonDomParser` 解析后遍历 → 大文档时 router 不够；自己写 token 扫描 → 复杂度高、易错。

## 8. 参考资料

- **PDF**：[`TwinCAT_3_PLC_Lib_Tc3_JsonXml_EN.pdf`](https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc3_JsonXml_EN.pdf) §4.3
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tcplclib_tc3_jsonxml/4220233355.html
- **相关 FB / FC**：`FB_JsonSaxWriter`, `ITcJsonSaxHandler`, `ITcJsonSaxValues`
