# SetMaxDecimalPlaces

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc3_JsonXml` |
| Library Version | `1.14.2` |
| Type | `METHOD` |
| Category | `FB_JsonSaxPrettyWriter` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc3_JsonXml_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tcplclib_tc3_jsonxml/11948988555.html |
| Verified | 2026-06-03 ✅ |
| InfoSys-checked | ✅ 2026-06-03 |
| Status | `verified` |
| Example | [`examples/P_Demo_FB_JsonSaxPrettyWriter_SetMaxDecimalPlaces.TcPOU`](../examples/P_Demo_FB_JsonSaxPrettyWriter_SetMaxDecimalPlaces.TcPOU) |

---

## 1. 功能简述

设置 LREAL/REAL 浮点序列化时的最大小数位数。

## 2. 接口定义

### VAR_INPUT

```iecst
VAR_INPUT
    decimalPlaces : DINT;
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `decimalPlaces` | `DINT` | 浮点序列化保留的最大小数位数（DINT）。 |


### VAR_OUTPUT

无。

### VAR_IN_OUT

无。

## 3. 行为说明

把 JSON 节点的值改成指定类型。节点已存在则原值被覆盖（`FB_JsonDomParser` 仅追加新内存、router 内存增长；`FB_JsonDynDomParser` 释放旧内存）；节点不存在请用 `Add<Type>Member`。返回更新后的 `SJsonValue` 句柄，便于链式调用。本方法属 `FB_JsonSaxPrettyWriter` 的对外 API，调用前需要保证父 FB 实例已成功初始化（`initStatus` 为 `S_OK`）。如返回值或输出参数不符合预期，可优先检查输入参数有效性，再调 `ExceptionRaised()` / 读 `hrErrorCode` 定位。

## 4. 错误码 / 返回值

本方法返回 `HRESULT`（32 位有符号整数）。`SUCCEEDED(hr)` 为 `TRUE` 表示调用成功。

| HRESULT | 含义 | 处理建议 |
|---|---|---|
| `S_OK` (0) | 操作成功，继续 | 继续下一步 |
| `S_FALSE` (1) | 在 SAX 回调里表示「请求终止解析」 | 让 `Parse()` 立即返回 |
| 其他 (E_*) | 操作失败 | 参考 PDF 第 7 章 ADS Return Codes 表 |

## 5. 使用注意 / 常见坑

- SAX 风格依赖调用顺序：违反 JSON 语法（如对象里无键的值）本 FB 不报错，但输出不是合法 JSON。

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_FB_JsonSaxPrettyWriter_SetMaxDecimalPlaces.TcPOU`](../examples/P_Demo_FB_JsonSaxPrettyWriter_SetMaxDecimalPlaces.TcPOU)（TwinCAT 3 原生 .TcPOU，可直接拖入 XAE 的 PLC POUs 文件夹）
>
> 导入步骤：右键 PLC 项目下 POUs 文件夹 → Add → Existing Item → 选该文件 → OK

```iecst
// 详见 examples 目录下的 .TcPOU 文件
```

## 7. 业务场景与实际价值

- **场景**：把 LREAL 浮点序列化精度从默认改成 6 位（适合工程数据）或 17 位（适合无损往返）。
- **价值**：一次调用改变全局序列化精度。
- **替代方案对比**：在每个 AddLreal 调用前做 ROUND → 重复代码；不调整 → 默认 17 位输出冗长。

## 8. 参考资料

- **PDF**：[`TwinCAT_3_PLC_Lib_Tc3_JsonXml_EN.pdf`](https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc3_JsonXml_EN.pdf) §4.5.35
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tcplclib_tc3_jsonxml/11948988555.html
- **相关 FB / FC**：`FB_JsonSaxPrettyWriter`, `AddMaxDecimalPlacesMember`, `GetMaxDecimalPlaces`
