# FB_XmlDomParser

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc3_JsonXml` |
| Library Version | `1.14.2` |
| Type | `FUNCTION_BLOCK` |
| Category | `Function block` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc3_JsonXml_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tcplclib_tc3_jsonxml/5512100491.html |
| Verified | 2026-06-03 ✅ |
| InfoSys-checked | ✅ 2026-06-03 |
| Status | `verified` |
| Example | [`examples/P_Demo_FB_XmlDomParser.TcPOU`](../examples/P_Demo_FB_XmlDomParser.TcPOU) |

---

## 1. 功能简述

`FB_XmlDomParser` 是基于 DOM 的 XML 文档解析与构建器。提供 ParseDocument / LoadDocumentFromFile / SaveDocumentToFile 等文档级方法，以及 NodeAsBool/Int/String 等节点值读取、SetChildAs*/SetAttributeAs* 节点值写入、AppendNode/RemoveChild 等树结构修改方法。适合配置文件读写、TwinCAT 工程数据交换等需要随机访问 XML 节点的场景。

## 2. 接口定义

### VAR_INPUT

无。

### VAR_OUTPUT

无。

### VAR_IN_OUT

无。

## 3. 行为说明

XML DOM 解析器。实例化后可调 `ParseDocument()` 解析字符串 / `LoadDocumentFromFile()` 加载文件，DOM 根节点用 `GetDocumentRoot()` 获取。对节点：`NodeAsBool/Int/String` 读取值；`SetChildAs*` 创建并赋值子节点；`SetAttributeAs*` 设置节点属性；`FirstChild/NextSibling/Parent` 遍历树；`AppendNode/RemoveChild` 调整结构。用 `SaveDocumentToFile()` 序列化到文件、用 `GetDocument()` 拷出 STRING。支持 XPath 风格的 `FindNode` / `FindNodePath` 查询。本方法属 `Function blocks` 的对外 API，调用前需要保证父 FB / 接口实例已就绪（必要时检查 `initStatus`）。

## 4. 错误码 / 返回值

本功能块/方法无返回值。状态通过 `initStatus` / `bError` / `hrErrorCode` 等输出反馈。

## 5. 使用注意 / 常见坑

- 实例化后先检查 VAR_OUTPUT 中的 `initStatus`，确认 FB 初始化成功（`S_OK`）再调业务方法。（工程经验补充）

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_FB_XmlDomParser.TcPOU`](../examples/P_Demo_FB_XmlDomParser.TcPOU)（TwinCAT 3 原生 .TcPOU，可直接拖入 XAE 的 PLC POUs 文件夹）
>
> 导入步骤：右键 PLC 项目下 POUs 文件夹 → Add → Existing Item → 选该文件 → OK

```iecst
// 详见 examples 目录下的 .TcPOU 文件
```

## 7. 业务场景与实际价值

- **场景**：读 TwinCAT 工程配置 XML、解析第三方 SCADA 的 XML 报文。
- **价值**：完整 DOM 操作含 XPath 风格查询；不必业务代码手写 SAX。
- **替代方案对比**：用 SAX 流式 → 简单查询也要写一堆回调；用文件解析库 + 字符串 split → 嵌套结构难处理。

## 8. 参考资料

- **PDF**：[`TwinCAT_3_PLC_Lib_Tc3_JsonXml_EN.pdf`](https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc3_JsonXml_EN.pdf) §4.7
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tcplclib_tc3_jsonxml/5512100491.html
- **相关 FB / FC**：`FB_JsonDomParser`
