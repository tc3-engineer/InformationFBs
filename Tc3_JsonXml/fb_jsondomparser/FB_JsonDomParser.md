# FB_JsonDomParser

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc3_JsonXml` |
| Library Version | `1.14.2` |
| Type | `FUNCTION_BLOCK` |
| Category | `Function block` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc3_JsonXml_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tcplclib_tc3_jsonxml/4219231115.html |
| Verified | 2026-06-03 ✅ |
| InfoSys-checked | ✅ 2026-06-03 |
| Status | `verified` |
| Example | [`examples/P_Demo_FB_JsonDomParser.TcPOU`](../examples/P_Demo_FB_JsonDomParser.TcPOU) |

---

## 1. 功能简述

`FB_JsonDomParser` 是 Tc3_JsonXml 库基于 DOM（Document Object Model）的 JSON 解析器。把整个 JSON 文档读入内部 DOM 内存，通过迭代器、按键查找、按路径查找等方式访问节点；并提供 Add*/Set*/Push*/Get*/Is* 等近百个方法用于构建、查询、修改 JSON 文档。适合改动较少、需要随机访问节点的场景；改动较多时改用 `FB_JsonDynDomParser`。

## 2. 接口定义

### VAR_INPUT

无。

### VAR_OUTPUT

```iecst
VAR_OUTPUT
    initStatus : HRESULT;
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `initStatus` | `HRESULT` | 功能块实例化结果。`S_OK` 表示初始化成功；其他 HRESULT 表示失败，参考 ADS Return Codes。 |


### VAR_IN_OUT

无。

## 3. 行为说明

实例化后即可使用，VAR_OUTPUT 的 `initStatus` 返回功能块初始化结果（`S_OK` 表示成功）。典型用法：先 `NewDocument()` 建立空 DOM 或 `ParseDocument()` 解析已有 JSON 字符串，再通过 `FindMember()` / `FindMemberPath()` 获取节点迭代器（`SJsonValue`），用 `GetBool/GetInt/GetString` 等方法读取节点值或用 `SetBool/SetInt/Add*Member` 等方法修改。DOM 内存只在 `NewDocument()` 或 `ParseDocument()` 时重新分配——频繁修改同一文档会累积 router 内存，请关注 PDF 4.1 节的 Router memory 警告；改动多请改用 `FB_JsonDynDomParser`。

## 4. 错误码 / 返回值

本功能块/方法无返回值。状态通过 `initStatus` / `bError` / `hrErrorCode` 等输出反馈。

## 5. 使用注意 / 常见坑

- 实例化后先检查 VAR_OUTPUT 中的 `initStatus`，确认 FB 初始化成功（`S_OK`）再调业务方法。（工程经验补充）

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_FB_JsonDomParser.TcPOU`](../examples/P_Demo_FB_JsonDomParser.TcPOU)（TwinCAT 3 原生 .TcPOU，可直接拖入 XAE 的 PLC POUs 文件夹）
>
> 导入步骤：右键 PLC 项目下 POUs 文件夹 → Add → Existing Item → 选该文件 → OK

```iecst
// 详见 examples 目录下的 .TcPOU 文件
```

## 7. 业务场景与实际价值

- **场景**：工控机与上位系统/云平台之间通过 JSON 交换配方、生产数据；需要随机读写 JSON 节点。
- **价值**：一次解析进 DOM 后任意路径都能 O(log) 访问，比每次重扫字符串快得多。
- **替代方案对比**：纯字符串拼/手写解析 → 字段一变就崩；用 OPC UA 替代 → 改协议成本高。

## 8. 参考资料

- **PDF**：[`TwinCAT_3_PLC_Lib_Tc3_JsonXml_EN.pdf`](https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc3_JsonXml_EN.pdf) §4.1
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tcplclib_tc3_jsonxml/4219231115.html
- **相关 FB / FC**：`FB_JsonDynDomParser`, `FB_JsonSaxReader`, `FB_JsonSaxWriter`
