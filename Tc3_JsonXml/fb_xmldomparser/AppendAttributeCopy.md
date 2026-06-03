# AppendAttributeCopy

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc3_JsonXml` |
| Library Version | `1.14.2` |
| Type | `METHOD` |
| Category | `FB_XmlDomParser` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc3_JsonXml_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tcplclib_tc3_jsonxml/5512100491.html |
| Verified | 2026-06-03 ✅ |
| InfoSys-checked | ✅ 2026-06-03 |
| Status | `verified` |
| Example | [`examples/P_Demo_FB_XmlDomParser_AppendAttributeCopy.TcPOU`](../examples/P_Demo_FB_XmlDomParser_AppendAttributeCopy.TcPOU) |

---

## 1. 功能简述

为指定 XML 节点附加一个新属性。属性名和值通过参数传入，返回新属性的 `SXmlAttribute` 引用。

## 2. 接口定义

### VAR_INPUT

```iecst
VAR_INPUT
    n : SXmlNode;
    copy : SXmlAttribute;
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `n` | `SXmlNode` | 目标 XML 节点的 `SXmlNode` 引用。 |
| `copy` | `SXmlAttribute` | 是否深拷贝：`TRUE` 表示拷贝节点内容并独立成新节点；`FALSE` 直接引用源节点。 |


### VAR_OUTPUT

无。

### VAR_IN_OUT

无。

## 3. 行为说明

在指定 XML 节点下添加新的子节点/属性。返回新添加节点的引用。调用方需要保证父节点引用有效（解析得到或 `GetDocumentRoot()` 得到），无效引用会导致行为未定义。本方法属 `FB_XmlDomParser` 的对外 API，调用前需要保证父 FB / 接口实例已就绪（必要时检查 `initStatus`）。

## 4. 错误码 / 返回值

本方法返回 `SXmlAttribute` 引用/句柄。

| 返回值 | 含义 |
|---|---|
| 有效 `SXmlAttribute` | 调用成功，可用于后续 DOM/迭代器操作 |
| 无效（0 / NULL） | 节点不存在 / 参数错误 / 类型不匹配 |

## 5. 使用注意 / 常见坑

- 调用前确保父 FB（`FB_XmlDomParser`）的 `initStatus` 为 `S_OK`。失败排查可调 `ExceptionRaised()`（DOM）或读 `hrErrorCode`（异步方法）。（工程经验补充）

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_FB_XmlDomParser_AppendAttributeCopy.TcPOU`](../examples/P_Demo_FB_XmlDomParser_AppendAttributeCopy.TcPOU)（TwinCAT 3 原生 .TcPOU，可直接拖入 XAE 的 PLC POUs 文件夹）
>
> 导入步骤：右键 PLC 项目下 POUs 文件夹 → Add → Existing Item → 选该文件 → OK

```iecst
// 详见 examples 目录下的 .TcPOU 文件
```

## 7. 业务场景与实际价值

- **场景**：在 XML 配置文件里增加新节点（如新增一台设备、加一行报警定义）。
- **价值**：DOM 操作随机插入，比重建文件高效。
- **替代方案对比**：用文本编辑流读写 → 行号难维护；重新生成整个文件 → 大文件慢。

## 8. 参考资料

- **PDF**：[`TwinCAT_3_PLC_Lib_Tc3_JsonXml_EN.pdf`](https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc3_JsonXml_EN.pdf) §4.7.9
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tcplclib_tc3_jsonxml/5512100491.html
- **相关 FB / FC**：`FB_XmlDomParser`
