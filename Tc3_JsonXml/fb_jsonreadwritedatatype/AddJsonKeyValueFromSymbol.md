# AddJsonKeyValueFromSymbol

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
| Example | [`examples/P_Demo_FB_JsonReadWriteDataType_AddJsonKeyValueFromSymbol.TcPOU`](../examples/P_Demo_FB_JsonReadWriteDataType_AddJsonKeyValueFromSymbol.TcPOU) |

---

## 1. 功能简述

基于 PLC 符号信息向 JSON SAX writer 输出键值对：方法读取符号的当前值并按 JSON 形式写入 SAX writer 缓冲。用于把 PLC 结构体的字段值自动序列化到 JSON 文档。

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
    fbWriter : FB_JsonSaxWriter;
    sKey : STRING;
    sDatatype : STRING;
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `fbWriter` | `FB_JsonSaxWriter` | SAX writer 实例引用，提供数据流目标。 |
| `sKey` | `STRING` | 字符串参数（STRING）。 |
| `sDatatype` | `STRING` | 字符串参数（STRING）。 |


## 3. 行为说明

通过 ADS 读符号、读到当前值后按 JSON 形式写到 SAX writer 缓冲。用于把 PLC 结构体的字段自动序列化进 JSON，无需手写每个字段的 `AddKey + AddString`。需要 TwinCAT 工程启用符号上传与 UTF-8 符号支持（System → Settings）；结构体字段加 `{attribute 'json' := 'keyName'}` 可指定 JSON key 名。本方法属 `FB_JsonReadWriteDataType` 的对外 API，调用前需要保证父 FB 实例已成功初始化（`initStatus` 为 `S_OK`）。

## 4. 错误码 / 返回值

本方法返回 `BOOL`。

| 返回值 | 含义 | 处理建议 |
|---|---|---|
| `TRUE` | 调用成功 | 继续后续逻辑 |
| `FALSE` | 调用失败 | 检查输入参数 / 调 `ExceptionRaised()` 或读 `hrErrorCode` 定位 |

## 5. 使用注意 / 常见坑

- 调用前确保父 FB（`FB_JsonReadWriteDataType`）的 `initStatus` 为 `S_OK`。失败排查可调 `ExceptionRaised()`（DOM）或读 `hrErrorCode`（异步方法）。（工程经验补充）

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_FB_JsonReadWriteDataType_AddJsonKeyValueFromSymbol.TcPOU`](../examples/P_Demo_FB_JsonReadWriteDataType_AddJsonKeyValueFromSymbol.TcPOU)（TwinCAT 3 原生 .TcPOU，可直接拖入 XAE 的 PLC POUs 文件夹）
>
> 导入步骤：右键 PLC 项目下 POUs 文件夹 → Add → Existing Item → 选该文件 → OK

```iecst
// 详见 examples 目录下的 .TcPOU 文件
```

## 7. 业务场景与实际价值

- **场景**：在 `FB_JsonReadWriteDataType` 的工作流程里完成一个具体子操作；通常配合本 FB 的其他方法组合使用。
- **价值**：作为 `FB_JsonReadWriteDataType` API 的一部分提供标准化能力，业务代码无需自实现。
- **替代方案对比**：自己写实现 → 与本库类型/接口不互通；用其他库 → 与 TwinCAT 工程内现有 JSON/XML 流程脱节。

## 8. 参考资料

- **PDF**：[`TwinCAT_3_PLC_Lib_Tc3_JsonXml_EN.pdf`](https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc3_JsonXml_EN.pdf) §4.6.2
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tcplclib_tc3_jsonxml/4220231435.html
- **相关 FB / FC**：`FB_JsonReadWriteDataType`
