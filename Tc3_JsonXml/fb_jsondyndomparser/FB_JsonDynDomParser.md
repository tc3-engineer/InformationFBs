# FB_JsonDynDomParser

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc3_JsonXml` |
| Library Version | `1.14.2` |
| Type | `FUNCTION_BLOCK` |
| Category | `Function block` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc3_JsonXml_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tcplclib_tc3_jsonxml/8101725835.html |
| Verified | 2026-06-03 ✅ |
| InfoSys-checked | ✅ 2026-06-03 |
| Status | `verified` |
| Example | [`examples/P_Demo_FB_JsonDynDomParser.TcPOU`](../examples/P_Demo_FB_JsonDynDomParser.TcPOU) |

---

## 1. 功能简述

`FB_JsonDynDomParser` 与 `FB_JsonDomParser` 派生自同一内部功能块、对外接口完全一致，差别在于内存管理策略：本 FB 在每次写动作（SetObject/SetJson 等）后会主动释放 router 内存，适合 JSON 文档需要频繁改动且不希望长时间持有 DOM 的场景。性能略低于 `FB_JsonDomParser`，但避免了 router 内存累积膨胀。

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

对外接口与 `FB_JsonDomParser` 完全相同：实例化后用 `NewDocument()` / `ParseDocument()` 初始化，再调用 Add/Set/Get/Push 等方法操作 DOM。本 FB 的差异在内部：每次 `SetObject()` / `SetJson()` 执行后会立即释放旧内存，避免 router 累积。代价是每次写操作引发完整内存重分配，性能略低；但在文档反复变动的应用中能稳定 router 占用。选型口径：偶尔改动 → `FB_JsonDomParser`；频繁改动且不愿手动调 `NewDocument()` → 本 FB。

## 4. 错误码 / 返回值

本功能块/方法无返回值。状态通过 `initStatus` / `bError` / `hrErrorCode` 等输出反馈。

## 5. 使用注意 / 常见坑

- 实例化后先检查 VAR_OUTPUT 中的 `initStatus`，确认 FB 初始化成功（`S_OK`）再调业务方法。（工程经验补充）

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_FB_JsonDynDomParser.TcPOU`](../examples/P_Demo_FB_JsonDynDomParser.TcPOU)（TwinCAT 3 原生 .TcPOU，可直接拖入 XAE 的 PLC POUs 文件夹）
>
> 导入步骤：右键 PLC 项目下 POUs 文件夹 → Add → Existing Item → 选该文件 → OK

```iecst
// 详见 examples 目录下的 .TcPOU 文件
```

## 7. 业务场景与实际价值

- **场景**：MQTT 网关循环更新 JSON 文档（每秒拼一次发出去），不希望 router 内存随时间增长。
- **价值**：每次写操作自动回收旧内存，长时间运行内存占用稳定。
- **替代方案对比**：用 `FB_JsonDomParser` 但要业务代码自己周期调 `NewDocument()` — 容易漏调；本 FB 全自动。

## 8. 参考资料

- **PDF**：[`TwinCAT_3_PLC_Lib_Tc3_JsonXml_EN.pdf`](https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc3_JsonXml_EN.pdf) §4.2
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tcplclib_tc3_jsonxml/8101725835.html
- **相关 FB / FC**：`FB_JsonDomParser`
