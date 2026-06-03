# ParseValues

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
| Example | [`examples/P_Demo_FB_JsonSaxReader_ParseValues.TcPOU`](../examples/P_Demo_FB_JsonSaxReader_ParseValues.TcPOU) |

---

## 1. 功能简述

类似 `Parse()`，但回调对象需实现 `ITcJsonSaxValues` 接口，每个回调额外携带嵌套 `level` 和路径 `infos`。

## 2. 接口定义

### VAR_INPUT

```iecst
VAR_INPUT
    ipHdl : ITcJsonSaxValues;
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `ipHdl` | `ITcJsonSaxValues` | 实现 SAX 回调接口的对象指针，调用 Parse 时把自定义业务 FB 传入。 |


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
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `sJson` | `STRING` | 字符串参数（STRING）。 |


## 3. 行为说明

类似 `Parse()`，但回调对象需实现 `ITcJsonSaxValues` 接口，每个回调额外携带嵌套 `level` 和路径 `infos`。调用者需注意：本方法的调用语义与 `FB_JsonSaxReader` 的整体行为一致——先确保父对象已正确初始化（FB_JsonSaxReader 的 `initStatus` = `S_OK`、必要时已 ParseDocument 或 NewDocument），再调用本方法。返回值/输出参数需在调用方业务代码中显式检查；如出现非预期返回，可调 `ExceptionRaised()`（DOM 解析器）或检查 `hrErrorCode`（IO/异步方法）定位问题。

## 4. 错误码 / 返回值

本方法返回 `BOOL`。

| 返回值 | 含义 | 处理建议 |
|---|---|---|
| `TRUE` | 调用成功 | 继续后续逻辑 |
| `FALSE` | 调用失败 | 检查输入参数 / 调 `ExceptionRaised()` 或读 `hrErrorCode` 定位 |

## 5. 使用注意 / 常见坑

- SAX 风格依赖调用顺序：违反 JSON 语法（如对象里无键的值）本 FB 不报错，但输出不是合法 JSON。

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_FB_JsonSaxReader_ParseValues.TcPOU`](../examples/P_Demo_FB_JsonSaxReader_ParseValues.TcPOU)（TwinCAT 3 原生 .TcPOU，可直接拖入 XAE 的 PLC POUs 文件夹）
>
> 导入步骤：右键 PLC 项目下 POUs 文件夹 → Add → Existing Item → 选该文件 → OK

```iecst
// 详见 examples 目录下的 .TcPOU 文件
```

## 7. 业务场景与实际价值

- **场景**：解析嵌套深的 JSON 配置（如 users[i].address.street），需要知道当前路径才能取舍。
- **价值**：回调自带 level + infos，业务代码不必自己维护路径栈。
- **替代方案对比**：用 Parse + 自己维护栈 → 易漏对齐；用 DOM → 大文件爆 router。

## 8. 参考资料

- **PDF**：[`TwinCAT_3_PLC_Lib_Tc3_JsonXml_EN.pdf`](https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc3_JsonXml_EN.pdf) §4.3.10
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tcplclib_tc3_jsonxml/4220233355.html
- **相关 FB / FC**：`FB_JsonSaxReader`
