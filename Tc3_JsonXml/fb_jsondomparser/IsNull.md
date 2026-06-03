# IsNull

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc3_JsonXml` |
| Library Version | `1.14.2` |
| Type | `METHOD` |
| Category | `FB_JsonDomParser` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc3_JsonXml_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tcplclib_tc3_jsonxml/4219231115.html |
| Verified | 2026-06-03 ✅ |
| InfoSys-checked | ✅ 2026-06-03 |
| Status | `verified` |
| Example | [`examples/P_Demo_FB_JsonDomParser_IsNull.TcPOU`](../examples/P_Demo_FB_JsonDomParser_IsNull.TcPOU) |

---

## 1. 功能简述

判断 JSON 节点的值是否为 JSON null 值 类型。返回 `TRUE` 表示是。

## 2. 接口定义

### VAR_INPUT

```iecst
VAR_INPUT
    v : SJsonValue;
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `v` | `SJsonValue` | 目标 JSON 节点的 `SJsonValue` 句柄。 |


### VAR_OUTPUT

无。

### VAR_IN_OUT

无。

## 3. 行为说明

运行时类型检查。SAX 解析得到的 JSON 节点没有静态类型，必须先用 `Is*` 系列判断类型再调用对应的 Get* 取值。未做类型检查就 Get 的话，返回值未定义；严重时可能触发 ExceptionRaised。工程实践：先 `HasMember` 检查 key 存在，再 `Is*` 检查类型，最后 `Get*` 取值——三步走避免崩溃。

## 4. 错误码 / 返回值

本方法返回 `BOOL`。

| 返回值 | 含义 | 处理建议 |
|---|---|---|
| `TRUE` | 调用成功 | 继续后续逻辑 |
| `FALSE` | 调用失败 | 检查输入参数 / 调 `ExceptionRaised()` 或读 `hrErrorCode` 定位 |

## 5. 使用注意 / 常见坑

- DOM 内存只在 `NewDocument()` / `ParseDocument()` 时重新分配；频繁 Set/Add 会累积 router 内存（PDF 4.1 节明确警告）。
- 使用 `Is*` / `HasMember` 做前置检查再 `Get*` 取值，避免对无效或类型不匹配节点取值导致未定义行为。（工程经验补充）

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_FB_JsonDomParser_IsNull.TcPOU`](../examples/P_Demo_FB_JsonDomParser_IsNull.TcPOU)（TwinCAT 3 原生 .TcPOU，可直接拖入 XAE 的 PLC POUs 文件夹）
>
> 导入步骤：右键 PLC 项目下 POUs 文件夹 → Add → Existing Item → 选该文件 → OK

```iecst
// 详见 examples 目录下的 .TcPOU 文件
```

## 7. 业务场景与实际价值

- **场景**：对解析后的不可信 JSON 数据做类型验证（如校验外部下发字段是否真是 Null 类型）。
- **价值**：避免 Get* 在类型不匹配时返回未定义值导致后续计算异常。
- **替代方案对比**：用 try/catch 兜底 → IEC 61131-3 不直接支持异常；不检查直接 Get → 偶发崩溃难定位。

## 8. 参考资料

- **PDF**：[`TwinCAT_3_PLC_Lib_Tc3_JsonXml_EN.pdf`](https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc3_JsonXml_EN.pdf) §4.1.63
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tcplclib_tc3_jsonxml/4219231115.html
- **相关 FB / FC**：`FB_JsonDomParser`, `GetNull`
