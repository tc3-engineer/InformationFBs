# DecodeBase64

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc3_JsonXml` |
| Library Version | `1.14.2` |
| Type | `METHOD` |
| Category | `FB_JsonSaxReader` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc3_JsonXml_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tcplclib_tc3_jsonxml/4220233355.html |
| Verified | 2026-06-03 ✅ |
| InfoSys-checked | ✅ 2026-06-03 |
| Status | `verified` |
| Example | [`examples/P_Demo_FB_JsonSaxReader_DecodeBase64.TcPOU`](../examples/P_Demo_FB_JsonSaxReader_DecodeBase64.TcPOU) |

---

## 1. 功能简述

把 Base64 编码的字符串解码为二进制数据写入外部 BYTE 缓冲。成功返回 `TRUE`。

## 2. 接口定义

### VAR_INPUT

```iecst
VAR_INPUT
    sBase64 : STRING;
    pBytes : POINTER TO BYTE;
    nBytes : REFERENCE TO DINT;
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `sBase64` | `STRING` | Base64 编码后的字符串（待校验/待解码）。 |
| `pBytes` | `POINTER TO BYTE` | 指向源 BYTE 缓冲区起始地址的指针（POINTER TO BYTE）。 |
| `nBytes` | `REFERENCE TO DINT` | 源缓冲区字节数（DINT/UDINT/REFERENCE TO DINT）。 |


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

无。

## 3. 行为说明

字符串解码工具方法，同步执行单次调用即返回。成功返回 `TRUE`；失败（输入格式不合法、缓冲过小等）返回 `FALSE`、`hrErrorCode` 给出具体 HRESULT。可单独使用，不依赖 SAX 解析上下文。本方法属 `FB_JsonSaxReader` 的对外 API，调用前需要保证父 FB 实例已成功初始化（`initStatus` 为 `S_OK`）。如返回值或输出参数不符合预期，可优先检查输入参数有效性，再调 `ExceptionRaised()` / 读 `hrErrorCode` 定位。

## 4. 错误码 / 返回值

本方法返回 `BOOL`。

| 返回值 | 含义 | 处理建议 |
|---|---|---|
| `TRUE` | 调用成功 | 继续后续逻辑 |
| `FALSE` | 调用失败 | 检查输入参数 / 调 `ExceptionRaised()` 或读 `hrErrorCode` 定位 |

## 5. 使用注意 / 常见坑

- SAX 风格依赖调用顺序：违反 JSON 语法（如对象里无键的值）本 FB 不报错，但输出不是合法 JSON。

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_FB_JsonSaxReader_DecodeBase64.TcPOU`](../examples/P_Demo_FB_JsonSaxReader_DecodeBase64.TcPOU)（TwinCAT 3 原生 .TcPOU，可直接拖入 XAE 的 PLC POUs 文件夹）
>
> 导入步骤：右键 PLC 项目下 POUs 文件夹 → Add → Existing Item → 选该文件 → OK

```iecst
// 详见 examples 目录下的 .TcPOU 文件
```

## 7. 业务场景与实际价值

- **场景**：把 base64 / hex / ISO8601 编码字符串解回二进制或时间——常见于解析外部下发的二进制 payload。
- **价值**：标准工具方法，避免自己写编码转换逻辑。
- **替代方案对比**：自行写转换 → 转义错误难调；用第三方代码 → 与本库类型不互通。

## 8. 参考资料

- **PDF**：[`TwinCAT_3_PLC_Lib_Tc3_JsonXml_EN.pdf`](https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc3_JsonXml_EN.pdf) §4.3.1
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tcplclib_tc3_jsonxml/4220233355.html
- **相关 FB / FC**：`FB_JsonSaxReader`
