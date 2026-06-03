# AddKey

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
| Example | [`examples/P_Demo_FB_JsonSaxWriter_AddKey.TcPOU`](../examples/P_Demo_FB_JsonSaxWriter_AddKey.TcPOU) |

---

## 1. 功能简述

向 SAX writer 缓冲写入一个 JSON 键名（key）。调用本方法后通常紧接一个对应值的 Add 方法（`AddBool` / `AddString` 等）以形成完整键值对。

## 2. 接口定义

### VAR_INPUT

无。

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

向 SAX writer 缓冲写入键名（不含冒号；冒号由下一次 Add 值方法或本 FB 内部添加）。调用顺序：必须在对象上下文里调用（前面已 StartObject），否则输出非法。调用后应紧跟一个 Add 值方法（`AddBool/AddString/StartObject/StartArray` 等）才能形成完整键值对。本方法属 `FB_JsonSaxWriter` 的对外 API，调用前需要保证父 FB 实例已成功初始化（`initStatus` 为 `S_OK`）。

## 4. 错误码 / 返回值

本功能块/方法无返回值。状态通过 `initStatus` / `bError` / `hrErrorCode` 等输出反馈。

## 5. 使用注意 / 常见坑

- SAX 风格依赖调用顺序：违反 JSON 语法（如对象里无键的值）本 FB 不报错，但输出不是合法 JSON。

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_FB_JsonSaxWriter_AddKey.TcPOU`](../examples/P_Demo_FB_JsonSaxWriter_AddKey.TcPOU)（TwinCAT 3 原生 .TcPOU，可直接拖入 XAE 的 PLC POUs 文件夹）
>
> 导入步骤：右键 PLC 项目下 POUs 文件夹 → Add → Existing Item → 选该文件 → OK

```iecst
// 详见 examples 目录下的 .TcPOU 文件
```

## 7. 业务场景与实际价值

- **场景**：SAX 流式生成 JSON 时追加 基本 类型的值/键值对。
- **价值**：无 DOM 中间态，内存最省、速度最快。
- **替代方案对比**：用 DOM 拼后导出 → 多一份内存；手写字符串拼接 → 转义和嵌套层级控制出错风险大。

## 8. 参考资料

- **PDF**：[`TwinCAT_3_PLC_Lib_Tc3_JsonXml_EN.pdf`](https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc3_JsonXml_EN.pdf) §4.4.8
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tcplclib_tc3_jsonxml/4220235275.html
- **相关 FB / FC**：`FB_JsonSaxWriter`
