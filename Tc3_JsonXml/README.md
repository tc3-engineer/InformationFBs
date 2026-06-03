# Tc3_JsonXml

> Beckhoff TwinCAT 3 JSON/XML 解析与构建库 — DOM 与 SAX 两套解析器，覆盖 JSON / XML 文档读写、PLC 符号双向序列化、JWT 生成。

- **Library Version**: `1.14.2`
- **Source PDF**: <https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc3_JsonXml_EN.pdf>
- **InfoSys 根**: <https://infosys.beckhoff.com/content/1033/tcplclib_tc3_jsonxml/>
- **总条目**: 337
  - 7 个 OO 父 FB（`FB_JsonDomParser` / `FB_JsonDynDomParser` / `FB_JsonSaxReader` / `FB_JsonSaxWriter` / `FB_JsonSaxPrettyWriter` / `FB_JsonReadWriteDataType` / `FB_XmlDomParser`）
  - 1 个独立 FB（`FB_JwtEncode`）
  - 2 个回调接口（`ITcJsonSaxHandler` / `ITcJsonSaxValues`，共 21 个回调方法）
  - 306 个 OO 方法（`FB_JsonDomParser` 114 + `FB_JsonReadWriteDataType` 14 + `FB_JsonSaxReader` 10 + `FB_JsonSaxWriter` 35 + `FB_JsonSaxPrettyWriter` 37 + `FB_XmlDomParser` 96）
- **状态**: ✅ done (337/337 verified)

## 子目录索引

| 子目录 | 说明 | 条目数 |
|---|---|---|
| [`fb_jsondomparser/`](fb_jsondomparser/) | `FB_JsonDomParser` 父 FB + 114 个 DOM 操作方法（Add / Get / Set / Push / Is / Find / Member 系列） | 115 |
| [`fb_jsondyndomparser/`](fb_jsondyndomparser/) | `FB_JsonDynDomParser`（继承自 `FB_JsonDomParser`，差异只在内存管理） | 1 |
| [`fb_jsonsaxreader/`](fb_jsonsaxreader/) | `FB_JsonSaxReader` 父 FB + 10 个 SAX 解析辅助方法（Decode / Is / Parse / ParseValues） | 11 |
| [`fb_jsonsaxwriter/`](fb_jsonsaxwriter/) | `FB_JsonSaxWriter` 父 FB + 35 个 SAX 写入方法（StartObject / Add / AddKey / EndArray …） | 36 |
| [`fb_jsonsaxprettywriter/`](fb_jsonsaxprettywriter/) | `FB_JsonSaxPrettyWriter` 父 FB + 37 个方法（与 SaxWriter 一致 + `Configure` 缩进字符） | 38 |
| [`fb_jsonreadwritedatatype/`](fb_jsonreadwritedatatype/) | `FB_JsonReadWriteDataType` 父 FB + 14 个符号 ↔ JSON 桥接方法 | 15 |
| [`fb_xmldomparser/`](fb_xmldomparser/) | `FB_XmlDomParser` 父 FB + 96 个 XML DOM 操作方法（Append / Node / Set / Find 系列） | 97 |
| [`function_blocks/`](function_blocks/) | 独立 FB（`FB_JwtEncode`） | 1 |
| [`i_tcjsonsaxhandler/`](i_tcjsonsaxhandler/) | `ITcJsonSaxHandler` 接口 + 13 个回调方法 | 14 |
| [`i_tcjsonsaxvalues/`](i_tcjsonsaxvalues/) | `ITcJsonSaxValues` 接口 + 8 个带层级路径的回调方法 | 9 |
| [`examples/`](examples/) | 337 个 `P_Demo_*.TcPOU` 例程（OO 方法用 `P_Demo_<Parent>_<Method>.TcPOU` 前缀消歧义） | 337 |

## 选型口径（重要）

| 场景 | 推荐 FB |
|---|---|
| 小 JSON 文档、随机读写节点 | `FB_JsonDomParser` |
| 频繁改动的 JSON 文档、不希望 router 内存累积 | `FB_JsonDynDomParser` |
| 大 JSON 文档、流式解析、低内存占用 | `FB_JsonSaxReader` + `ITcJsonSaxHandler` / `ITcJsonSaxValues` |
| 紧凑 JSON 输出（MQTT/HTTP） | `FB_JsonSaxWriter` |
| 可读 JSON 输出（调试 / 配置文件） | `FB_JsonSaxPrettyWriter` |
| 把 PLC 结构体 ↔ JSON 自动转换 | `FB_JsonReadWriteDataType` |
| XML DOM 读写 | `FB_XmlDomParser` |
| 生成 JWT (RFC 7519) | `FB_JwtEncode` |

## 例程导入

每个文档配套一个 `examples/P_Demo_<...>.TcPOU` 文件，可直接拖入 TwinCAT 3 XAE：

1. 解决方案 / 项目里展开 PLC → POUs 文件夹
2. 右键 POUs → Add → Existing Item → 选 `P_Demo_<Name>.TcPOU` → OK
3. 在该 POU 所在的 PLC References 节点下确认 `Tc3_JsonXml` 已加入引用（System → References → Add library）
4. 编译 → 登录 → 运行；在线 monitor / 在线写值观察行为

OO 方法的例程文件名带父 FB 前缀避免重名（如 `FB_JsonDomParser.GetBool` → `P_Demo_FB_JsonDomParser_GetBool.TcPOU`）。

## 验收基线

- 全部 337 篇 `verify_doc.py` 退出码 0（PASS）
- 全部 337 个 `lint_tcpou.py` 退出码 0（PASS）
- 全仓 GUID 唯一性 `--check-unique` PASS
- PDF + InfoSys 双源对照，元信息 10 行齐全；OO 方法 Source InfoSys 行指向父 FB 的 topic（per-method topic IDs 在 InfoSys 上未公开枚举）

## 已知细节

- **PDF TOC 重名**：第 4.7.20 节与 4.7.31 节的 TOC 标题都写为 "Attributes"，但前者实际是 `METHOD Attribute`（按名字单查），后者是 `METHOD Attributes`（返回迭代器遍历）。本仓库分别落位为 [`fb_xmldomparser/Attribute.md`](fb_xmldomparser/Attribute.md) 与 [`fb_xmldomparser/Attributes.md`](fb_xmldomparser/Attributes.md)；由于 parse_toc 无法区分这两个同名条目，其 Status 标 `⚠️ infer-from-naming-convention`，verify_doc 跳过 VAR 对账（PDF 自身排版问题，非文档质量问题）。
- **OO 方法 InfoSys 链接**：Beckhoff InfoSys 把所有 OO 方法都列在父 FB 的 topic 页下（如所有 `FB_JsonDomParser` 方法都在 `4219231115.html`），单方法没有独立 topic URL。因此本仓 OO 方法的 `Source InfoSys` 行指向父 FB 的 topic 页，`InfoSys-checked` 标 `✅ <date>`。
- **回调接口（ITc...）方法**：`ITcJsonSaxHandler` / `ITcJsonSaxValues` 是接口（不是 FB），但 PDF 把它们的回调方法以 `METHOD` 形式列在 4.5/5.1/5.2 节中。本仓按 OO 方法格式生成文档与例程占位（例程演示用法说明，实际项目里需要业务代码 implements 接口）。
- **`FB_JsonDynDomParser`**：PDF 第 4.2 节明确说「方法集合见 4.1 `FB_JsonDomParser`」，没有自己的方法列表。本仓 `fb_jsondyndomparser/` 子目录里只放 `FB_JsonDynDomParser.md` 一篇父 FB 文档；调用 DOM 方法时直接看 `FB_JsonDomParser` 同名方法的文档。

## 关键 Worked Examples（PDF 第 6 章）

PDF 第 6 章列了 6 个完整应用示例，本仓未单独落 .TcPOU 例程（PDF 例子较长且需要多 POU 协作），但相关方法文档都对应有最小例程：

| PDF 章节 | 示例标题 | 涉及方法 |
|---|---|---|
| 6.1 | Tc3JsonXmlSampleJsonDataType | `FB_JsonReadWriteDataType.AddJsonValueFromSymbol` 等 |
| 6.2 | Tc3JsonXmlSampleJsonSaxReader | `FB_JsonSaxReader.Parse` + `ITcJsonSaxHandler` |
| 6.3 | Tc3JsonXmlSampleJsonSaxWriter | `FB_JsonSaxWriter.StartObject/AddKey/AddString/EndObject` |
| 6.4 | Tc3JsonXmlSampleJsonDomReader | `FB_JsonDomParser.ParseDocument/FindMember/GetXxx` |
| 6.5 | Tc3JsonXmlSampleXmlDomReader | `FB_XmlDomParser.ParseDocument/FirstChild/NodeAsXxx` |
| 6.6 | Tc3JsonXmlSampleXmlDomWriter | `FB_XmlDomParser.NewDocument/AppendNode/SetChildAsXxx` |

直接阅读 PDF 第 6 章可看到完整可拷贝代码；本仓单方法文档配套的 `examples/P_Demo_<Method>.TcPOU` 适合做最小验证起步。
