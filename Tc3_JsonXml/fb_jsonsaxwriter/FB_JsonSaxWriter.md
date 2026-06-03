# FB_JsonSaxWriter

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc3_JsonXml` |
| Library Version | `1.14.2` |
| Type | `FUNCTION_BLOCK` |
| Category | `Function block` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc3_JsonXml_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tcplclib_tc3_jsonxml/4220235275.html |
| Verified | 2026-06-03 ✅ |
| InfoSys-checked | ✅ 2026-06-03 |
| Status | `verified` |
| Example | [`examples/P_Demo_FB_JsonSaxWriter.TcPOU`](../examples/P_Demo_FB_JsonSaxWriter.TcPOU) |

---

## 1. 功能简述

`FB_JsonSaxWriter` 是基于 SAX 思想的 JSON 流式写入器，通过 StartObject / StartArray / AddKey / AddString / EndObject 等顺序调用构建 JSON 文档，无需先在内存里组装 DOM。生成的 JSON 不带额外缩进/换行（紧凑格式），可读性较差但传输效率高。需要可读性可改用 `FB_JsonSaxPrettyWriter`。

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

构建 JSON 文档的 SAX 风格写入器。典型顺序：`StartObject()` 或 `StartArray()` 打开容器，对每个键值对调用 `AddKey()` 加键名再调 `AddBool/AddString/AddInt` 等加值，嵌套对象/数组再调一次 `StartObject/StartArray` 进入，结束时 `EndObject()` / `EndArray()` 闭合。全部写完后 `GetDocument(sJsonOut)` 把结果拷出 STRING。`ResetDocument()` 清空内部缓冲准备下一次构建。本 FB 输出紧凑无空白格式，可读性差但 byte 数最少；需要 pretty-print 改用 `FB_JsonSaxPrettyWriter`。

## 4. 错误码 / 返回值

本功能块/方法无返回值。状态通过 `initStatus` / `bError` / `hrErrorCode` 等输出反馈。

## 5. 使用注意 / 常见坑

- 实例化后先检查 VAR_OUTPUT 中的 `initStatus`，确认 FB 初始化成功（`S_OK`）再调业务方法。（工程经验补充）

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_FB_JsonSaxWriter.TcPOU`](../examples/P_Demo_FB_JsonSaxWriter.TcPOU)（TwinCAT 3 原生 .TcPOU，可直接拖入 XAE 的 PLC POUs 文件夹）
>
> 导入步骤：右键 PLC 项目下 POUs 文件夹 → Add → Existing Item → 选该文件 → OK

```iecst
// 详见 examples 目录下的 .TcPOU 文件
```

## 7. 业务场景与实际价值

- **场景**：PLC 周期拼装一份 JSON 推给 MQTT broker；体积越小越好。
- **价值**：流式构造无中间 DOM，输出紧凑无空白，带宽节省 ~30%。
- **替代方案对比**：用 `FB_JsonDomParser` 写完再 `GetDocument` → 多一份 DOM 内存；手写字符串拼 → 转义出错风险大。

## 8. 参考资料

- **PDF**：[`TwinCAT_3_PLC_Lib_Tc3_JsonXml_EN.pdf`](https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc3_JsonXml_EN.pdf) §4.4
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tcplclib_tc3_jsonxml/4220235275.html
- **相关 FB / FC**：`FB_JsonSaxPrettyWriter`, `FB_JsonSaxReader`
