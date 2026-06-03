# AddKeyNumber

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc3_JsonXml` |
| Library Version | `1.14.2` |
| Type | `METHOD` |
| Category | `FB_JsonSaxWriter` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc3_JsonXml_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tcplclib_tc3_jsonxml/4220235275.html |
| Verified | 2026-06-03 ✅ |
| InfoSys-checked | ✅ 2026-06-03 |
| Status | `verified` |
| Example | [`examples/P_Demo_FB_JsonSaxWriter_AddKeyNumber.TcPOU`](../examples/P_Demo_FB_JsonSaxWriter_AddKeyNumber.TcPOU) |

---

## 1. 功能简述

向 SAX writer 缓冲一次性写入 JSON 键名和对应的 Number 类型值，等价于先 `AddKey()` 再 `AddNumber()`，但减少一次方法调用。

## 2. 接口定义

### VAR_INPUT

```iecst
VAR_INPUT
    value : DINT;
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `value` | `DINT` | 回调传入的值；类型与回调方法名后缀对应。 |


### VAR_OUTPUT

无。

### VAR_IN_OUT

```iecst
VAR_IN_OUT
    key : STRING;
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `key` | `STRING` | JSON 键名（VAR_IN_OUT，调用方可读取或修改）。 |


## 3. 行为说明

等价于先 `AddKey(key)` 再 `Add<Type>(value)`，把键名和值一次性写入 SAX writer 缓冲。在循环里反复构造对象字段时，每对键值少一次方法调用、性能略好。本方法属 `FB_JsonSaxWriter` 的对外 API，调用前需要保证父 FB 实例已成功初始化（`initStatus` 为 `S_OK`）。如返回值或输出参数不符合预期，可优先检查输入参数有效性，再调 `ExceptionRaised()` / 读 `hrErrorCode` 定位。

## 4. 错误码 / 返回值

本功能块/方法无返回值。状态通过 `initStatus` / `bError` / `hrErrorCode` 等输出反馈。

## 5. 使用注意 / 常见坑

- SAX 风格依赖调用顺序：违反 JSON 语法（如对象里无键的值）本 FB 不报错，但输出不是合法 JSON。

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_FB_JsonSaxWriter_AddKeyNumber.TcPOU`](../examples/P_Demo_FB_JsonSaxWriter_AddKeyNumber.TcPOU)（TwinCAT 3 原生 .TcPOU，可直接拖入 XAE 的 PLC POUs 文件夹）
>
> 导入步骤：右键 PLC 项目下 POUs 文件夹 → Add → Existing Item → 选该文件 → OK

```iecst
// 详见 examples 目录下的 .TcPOU 文件
```

## 7. 业务场景与实际价值

- **场景**：SAX 流式生成 JSON 时追加 Number 类型的值/键值对。
- **价值**：无 DOM 中间态，内存最省、速度最快。
- **替代方案对比**：用 DOM 拼后导出 → 多一份内存；手写字符串拼接 → 转义和嵌套层级控制出错风险大。

## 8. 参考资料

- **PDF**：[`TwinCAT_3_PLC_Lib_Tc3_JsonXml_EN.pdf`](https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc3_JsonXml_EN.pdf) §4.4.15
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tcplclib_tc3_jsonxml/4220235275.html
- **相关 FB / FC**：`FB_JsonSaxWriter`
