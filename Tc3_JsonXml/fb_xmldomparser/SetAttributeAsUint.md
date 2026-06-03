# SetAttributeAsUint

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
| Example | [`examples/P_Demo_FB_XmlDomParser_SetAttributeAsUint.TcPOU`](../examples/P_Demo_FB_XmlDomParser_SetAttributeAsUint.TcPOU) |

---

## 1. 功能简述

把 JSON 节点的 AttributeAsUint 属性设置为传入值。返回更新后的 `SJsonValue` 句柄。

## 2. 接口定义

### VAR_INPUT

```iecst
VAR_INPUT
    a : SXmlAttribute;
    value : UDINT;
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `a` | `SXmlAttribute` | 数组节点 `SJsonAIterator` 或目标 JSON 数组节点 `SJsonValue`。 |
| `value` | `UDINT` | 回调传入的值；类型与回调方法名后缀对应。 |


### VAR_OUTPUT

无。

### VAR_IN_OUT

无。

## 3. 行为说明

把 JSON 节点的值改成指定类型。节点已存在则原值被覆盖（`FB_JsonDomParser` 仅追加新内存、router 内存增长；`FB_JsonDynDomParser` 释放旧内存）；节点不存在请用 `Add<Type>Member`。返回更新后的 `SJsonValue` 句柄，便于链式调用。本方法属 `FB_XmlDomParser` 的对外 API，调用前需要保证父 FB / 接口实例已就绪（必要时检查 `initStatus`）。

## 4. 错误码 / 返回值

本方法返回 `SXmlAttribute` 引用/句柄。

| 返回值 | 含义 |
|---|---|
| 有效 `SXmlAttribute` | 调用成功，可用于后续 DOM/迭代器操作 |
| 无效（0 / NULL） | 节点不存在 / 参数错误 / 类型不匹配 |

## 5. 使用注意 / 常见坑

- 调用前确保父 FB（`FB_XmlDomParser`）的 `initStatus` 为 `S_OK`。失败排查可调 `ExceptionRaised()`（DOM）或读 `hrErrorCode`（异步方法）。（工程经验补充）

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_FB_XmlDomParser_SetAttributeAsUint.TcPOU`](../examples/P_Demo_FB_XmlDomParser_SetAttributeAsUint.TcPOU)（TwinCAT 3 原生 .TcPOU，可直接拖入 XAE 的 PLC POUs 文件夹）
>
> 导入步骤：右键 PLC 项目下 POUs 文件夹 → Add → Existing Item → 选该文件 → OK

```iecst
// 详见 examples 目录下的 .TcPOU 文件
```

## 7. 业务场景与实际价值

- **场景**：修改已有 JSON 节点的 AttributeAsUint 类型值（如更新缓存的实时数据字段）。
- **价值**：DOM 树本地修改不重新构造整个文档，比 GetDocument + 字符串替换效率高。
- **替代方案对比**：重新组建整个 JSON → 大文档时性能差；字符串 Find + Replace → 同名字段容易误改。

## 8. 参考资料

- **PDF**：[`TwinCAT_3_PLC_Lib_Tc3_JsonXml_EN.pdf`](https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc3_JsonXml_EN.pdf) §4.7.87
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tcplclib_tc3_jsonxml/5512100491.html
- **相关 FB / FC**：`FB_XmlDomParser`, `AddAttributeAsUintMember`, `GetAttributeAsUint`
