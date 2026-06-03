# SetSymbolFromJson

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc3_JsonXml` |
| Library Version | `1.14.2` |
| Type | `METHOD` |
| Category | `FB_JsonReadWriteDataType` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc3_JsonXml_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tcplclib_tc3_jsonxml/4220231435.html |
| Verified | 2026-06-03 ✅ |
| InfoSys-checked | ✅ 2026-06-03 |
| Status | `verified` |
| Example | [`examples/P_Demo_FB_JsonReadWriteDataType_SetSymbolFromJson.TcPOU`](../examples/P_Demo_FB_JsonReadWriteDataType_SetSymbolFromJson.TcPOU) |

---

## 1. 功能简述

把指定 JSON 节点的值反向赋回 PLC 符号信息所指的变量。配合 `FB_JsonDomParser` 已解析的 DOM 节点使用，实现 JSON → PLC 结构体的自动反序列化。

## 2. 接口定义

### VAR_INPUT

```iecst
VAR_INPUT
    nData : UDINT;
    pData : PVOID;
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `nData` | `UDINT` | 数量/索引参数（UDINT）。 |
| `pData` | `PVOID` | 存放源/目标二进制数据的内存指针（POINTER TO BYTE / PVOID）。 |


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

```iecst
VAR_IN_OUT
    sJson : STRING;
    sDatatype : STRING;
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `sJson` | `STRING` | 字符串参数（STRING）。 |
| `sDatatype` | `STRING` | 字符串参数（STRING）。 |


## 3. 行为说明

把 JSON 节点的值改成指定类型。节点已存在则原值被覆盖（`FB_JsonDomParser` 仅追加新内存、router 内存增长；`FB_JsonDynDomParser` 释放旧内存）；节点不存在请用 `Add<Type>Member`。返回更新后的 `SJsonValue` 句柄，便于链式调用。本方法属 `FB_JsonReadWriteDataType` 的对外 API，调用前需要保证父 FB 实例已成功初始化（`initStatus` 为 `S_OK`）。如返回值或输出参数不符合预期，可优先检查输入参数有效性，再调 `ExceptionRaised()` / 读 `hrErrorCode` 定位。

## 4. 错误码 / 返回值

本方法返回 `BOOL`。

| 返回值 | 含义 | 处理建议 |
|---|---|---|
| `TRUE` | 调用成功 | 继续后续逻辑 |
| `FALSE` | 调用失败 | 检查输入参数 / 调 `ExceptionRaised()` 或读 `hrErrorCode` 定位 |

## 5. 使用注意 / 常见坑

- 调用前确保父 FB（`FB_JsonReadWriteDataType`）的 `initStatus` 为 `S_OK`。失败排查可调 `ExceptionRaised()`（DOM）或读 `hrErrorCode`（异步方法）。（工程经验补充）

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_FB_JsonReadWriteDataType_SetSymbolFromJson.TcPOU`](../examples/P_Demo_FB_JsonReadWriteDataType_SetSymbolFromJson.TcPOU)（TwinCAT 3 原生 .TcPOU，可直接拖入 XAE 的 PLC POUs 文件夹）
>
> 导入步骤：右键 PLC 项目下 POUs 文件夹 → Add → Existing Item → 选该文件 → OK

```iecst
// 详见 examples 目录下的 .TcPOU 文件
```

## 7. 业务场景与实际价值

- **场景**：修改已有 JSON 节点的 SymbolFromJson 类型值（如更新缓存的实时数据字段）。
- **价值**：DOM 树本地修改不重新构造整个文档，比 GetDocument + 字符串替换效率高。
- **替代方案对比**：重新组建整个 JSON → 大文档时性能差；字符串 Find + Replace → 同名字段容易误改。

## 8. 参考资料

- **PDF**：[`TwinCAT_3_PLC_Lib_Tc3_JsonXml_EN.pdf`](https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc3_JsonXml_EN.pdf) §4.6.14
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tcplclib_tc3_jsonxml/4220231435.html
- **相关 FB / FC**：`FB_JsonReadWriteDataType`, `AddSymbolFromJsonMember`, `GetSymbolFromJson`
