# AddReal

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
| Example | [`examples/P_Demo_FB_JsonSaxPrettyWriter_AddReal.TcPOU`](../examples/P_Demo_FB_JsonSaxPrettyWriter_AddReal.TcPOU) |

---

## 1. 功能简述

向 SAX writer 缓冲追加一个 Real 类型的值（无键）。通常在数组上下文中使用，给数组追加一个元素；如要写键值对请用 `AddKey<Type>` 方法。

## 2. 接口定义

### VAR_INPUT

```iecst
VAR_INPUT
    value : REAL;
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `value` | `REAL` | 回调传入的值；类型与回调方法名后缀对应。 |


### VAR_OUTPUT

无。

### VAR_IN_OUT

无。

## 3. 行为说明

顺序追加到 SAX writer 内部缓冲。如果当前最近的容器是数组（StartArray 已调），追加一个数组元素；如果最近容器是对象，本方法将在没有键的情况下抛出非法 JSON，需要先调 `AddKey()` 给出键名。调用顺序若不匹配 JSON 语法（如对象里出现没键的值），输出的字符串将不是合法 JSON，但本 FB 不会报错——需要业务代码自己保证调用顺序符合 JSON grammar。

## 4. 错误码 / 返回值

本功能块/方法无返回值。状态通过 `initStatus` / `bError` / `hrErrorCode` 等输出反馈。

## 5. 使用注意 / 常见坑

- SAX 风格依赖调用顺序：违反 JSON 语法（如对象里无键的值）本 FB 不报错，但输出不是合法 JSON。

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_FB_JsonSaxPrettyWriter_AddReal.TcPOU`](../examples/P_Demo_FB_JsonSaxPrettyWriter_AddReal.TcPOU)（TwinCAT 3 原生 .TcPOU，可直接拖入 XAE 的 PLC POUs 文件夹）
>
> 导入步骤：右键 PLC 项目下 POUs 文件夹 → Add → Existing Item → 选该文件 → OK

```iecst
// 详见 examples 目录下的 .TcPOU 文件
```

## 7. 业务场景与实际价值

- **场景**：SAX 流式生成 JSON 时追加 Real 类型的值/键值对。
- **价值**：无 DOM 中间态，内存最省、速度最快。
- **替代方案对比**：用 DOM 拼后导出 → 多一份内存；手写字符串拼接 → 转义和嵌套层级控制出错风险大。

## 8. 参考资料

- **PDF**：[`TwinCAT_3_PLC_Lib_Tc3_JsonXml_EN.pdf`](https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc3_JsonXml_EN.pdf) §4.5.22
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tcplclib_tc3_jsonxml/11948988555.html
- **相关 FB / FC**：`FB_JsonSaxPrettyWriter`
