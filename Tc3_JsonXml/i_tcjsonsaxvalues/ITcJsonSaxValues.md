# ITcJsonSaxValues

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc3_JsonXml` |
| Library Version | `1.14.2` |
| Type | `INTERFACE` |
| Category | `Interface` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc3_JsonXml_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tcplclib_tc3_jsonxml/4219229195.html |
| Verified | 2026-06-03 ✅ |
| InfoSys-checked | ✅ 2026-06-03 |
| Status | `verified` |
| Example | [`examples/P_Demo_ITcJsonSaxValues.TcPOU`](../examples/P_Demo_ITcJsonSaxValues.TcPOU) |

---

## 1. 功能简述

`ITcJsonSaxValues` 与 `ITcJsonSaxHandler` 类似，但每个 On*Value 回调多带 `level`（嵌套层级）与 `infos`（层级路径信息指针）两个参数，便于在处理深层嵌套 JSON 时知道当前 token 所处的对象/数组路径。适合需要知道上下文路径的 SAX 处理逻辑（如「只关注 user.profile.address 路径下的值」）。

## 2. 接口定义

### VAR_INPUT

无。

### VAR_OUTPUT

无。

### VAR_IN_OUT

无。

## 3. 行为说明

与 `ITcJsonSaxHandler` 接口形状相似，但每个回调额外多两个 VAR_INPUT 参数：`level`（当前嵌套深度，从 0 起）和 `infos`（指向 `TcJsonLevelInfo` 数组的指针，记录每层是 object 还是 array 以及在父层中的索引/键名）。通过 infos 可在不维护自有路径栈的前提下直接判断「我在哪条 JSON 路径上」，适合实现「只关心特定路径下的值」这种过滤式 SAX 处理。调用方与 `ITcJsonSaxHandler` 一致：实现该接口的功能块作为参数传给 `FB_JsonSaxReader.ParseValues()`。

## 4. 错误码 / 返回值

本功能块/方法无返回值。状态通过 `initStatus` / `bError` / `hrErrorCode` 等输出反馈。

## 5. 使用注意 / 常见坑

- 实例化后先检查 VAR_OUTPUT 中的 `initStatus`，确认 FB 初始化成功（`S_OK`）再调业务方法。（工程经验补充）

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_ITcJsonSaxValues.TcPOU`](../examples/P_Demo_ITcJsonSaxValues.TcPOU)（TwinCAT 3 原生 .TcPOU，可直接拖入 XAE 的 PLC POUs 文件夹）
>
> 导入步骤：右键 PLC 项目下 POUs 文件夹 → Add → Existing Item → 选该文件 → OK

```iecst
// 详见 examples 目录下的 .TcPOU 文件
```

## 7. 业务场景与实际价值

- **场景**：需要在 SAX 解析时知道当前 token 所处的 JSON 路径（如 `users[0].name`），实现该接口比手维护路径栈方便。
- **价值**：回调直接拿到 level + infos，业务代码只判断 `infos[1].name = 'address'` 之类的条件。
- **替代方案对比**：实现 `ITcJsonSaxHandler` 但业务代码自己维护路径栈 → 容易和 SAX reader 不同步；不维护路径 → 信息不全。

## 8. 参考资料

- **PDF**：[`TwinCAT_3_PLC_Lib_Tc3_JsonXml_EN.pdf`](https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc3_JsonXml_EN.pdf) §5.2
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tcplclib_tc3_jsonxml/4219229195.html
- **相关 FB / FC**：`FB_JsonSaxReader`, `ITcJsonSaxHandler`
