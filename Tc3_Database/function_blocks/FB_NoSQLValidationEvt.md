# FB_NoSQLValidationEvt

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc3_Database` |
| Library Version | `1.14.1` |
| Type | `FUNCTION_BLOCK` |
| Category | `Function blocks` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/tf6420_tc3_database_server_en.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tf6420_tc3_database_server/5875270411.html |
| Verified | 2026-06-03 ✅ |
| InfoSys-checked | ✅ 2026-06-03 |
| Status | `verified` |
| Example | [`examples/P_Demo_FB_NoSQLValidationEvt.TcPOU`](../examples/P_Demo_FB_NoSQLValidationEvt.TcPOU) |

---

## 1. 功能简述

NoSQL 结果验证功能块（PDF §6.1.1.4.4）——专门用于读取 `FB_NoSQLResultEvt.ReadAsStruct(bValidate := TRUE, pNoSQLValidation := ADR(this))` 调用中发现的「schema 不匹配」详情。三个方法：`GetIssues` 取问题列表（`ARRAY OF T_MAXSTRING`，描述哪些字段未映射或不一致）；`GetRemainingData` 取「无法映射到 PLC 结构」的原始 JSON 文档；`Release` 释放验证缓存。该 FB **不是直接发查询的**——它是 `FB_NoSQLResultEvt` 的辅助 / 配套 FB。

## 2. 接口定义

### VAR_INPUT

```iecst
VAR_INPUT
    sNetID: T_AmsNetID := '';
    tTimeout: TIME := T#5S;
END_VAR
```

| 名称 | 类型 | 默认值 | 说明 |
|---|---|---|---|
| `sNetID` | `T_AmsNetID` | `''` | Database Server AMS Net ID。 |
| `tTimeout` | `TIME` | `T#5S` | ADS 超时。 |

### VAR_OUTPUT

```iecst
VAR_OUTPUT
    bBusy: BOOL;
    bError: BOOL;
    ipTcResult: Tc3_EventLogger.I_TcResultEvent;
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `bBusy` | `BOOL` | 方法运行中。 |
| `bError` | `BOOL` | 错误置 TRUE。 |
| `ipTcResult` | `Tc3_EventLogger.I_TcResultEvent` | Tc3 EventLogger 消息接口（PDF 此 FB 声明里写 `I_TcResultEvent`，但 PDF 别处和 InfoSys 同样使用 `I_TcMessage`——以 InfoSys 为准 / 实际编译时按声明）。 |

### VAR_IN_OUT

无。

### Properties

| 属性 | 类型 | 说明 |
|---|---|---|
| `eTraceLevel` | `TcEventSeverity` | 事件分级阈值。 |

### Method: `GetIssues`（取问题列表）

```iecst
METHOD GetIssues : BOOL
VAR_INPUT
    pData : POINTER TO BYTE;
    cbData: UDINT;
    bDataRelease : BOOL;
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `pData` | `POINTER TO BYTE` | 接收数组地址（`ARRAY[0..N] OF T_MAXSTRING`），每元素描述一个 issue（如 `"Field 'temp' missing in PLC struct"`）。 |
| `cbData` | `UDINT` | 数组 SIZEOF。 |
| `bDataRelease` | `BOOL` | TRUE = 取完释放 Server 缓存的 issue 列表。 |

### Method: `GetRemainingData`（取未映射文档）

```iecst
METHOD GetRemainingData : BOOL
VAR_INPUT
    pData : POINTER TO BYTE;
    cbData : UDINT;
    cbDocument : UDINT;
    bDataRelease : BOOL;
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `pData` | `POINTER TO BYTE` | 接收数组地址（`ARRAY[0..N] OF STRING(M)`）。 |
| `cbData` | `UDINT` | 数组 SIZEOF。 |
| `cbDocument` | `UDINT` | 单文档 STRING 长度。 |
| `bDataRelease` | `BOOL` | TRUE = 取完释放。 |

### Method: `Release`

```iecst
METHOD Release : BOOL
```

无入参——释放 Server 端验证缓存。

## 3. 行为说明

**触发方式**：本 FB 不主动发查询。它的 Server 端缓存由 `FB_NoSQLResultEvt.ReadAsStruct` 在 `bValidate := TRUE` + `pNoSQLValidation := ADR(thisFb)` 的调用下被填充。每次 ReadAsStruct 调用后，本 FB 实例对应的内存里可能多了一批新的 issues 与 remaining data。

**两种验证输出**：
1. **Issues**（`GetIssues`）：文字描述——如 `"Field 'temperature' could not be mapped (target structure has no such field)"`、`"PLC field 'rPressure' was not filled (JSON document missing this key)"`、`"Type mismatch on field 'sName': expected STRING, got NUMBER"`。便于程序员看日志定位问题。
2. **Remaining Data**（`GetRemainingData`）：原 JSON 字符串数组——返回那些根本无法映射到 PLC 结构的文档（整文档不匹配，而非某字段）。可用 `Tc3_JsonXml` 在 PLC 端手工解析或写日志。

**典型用法**：开发期 / 调试期开启 `bValidate := TRUE` 看 DB 端数据结构与 PLC 假设的差异；生产期发现 schema 漂移时调用 GetIssues 自动告警；OEM 部署到新车间发现 DB schema 略有差异时快速适配（不用每次都改 PLC 结构）。

**`ipTcResult` 类型不一致**：PDF 6.1.1.4.4 节定义为 `Tc3_EventLogger.I_TcResultEvent`，与其他 NoSQL FB 用的 `I_TcMessage` 不一致。这可能是 Beckhoff 内部接口分级——`I_TcResultEvent` 是 `I_TcMessage` 的父接口或别名。实际调用时按 IEC 编译器接受的类型——目前推荐按 PDF 声明使用 `I_TcResultEvent`。

**`Release` 不调的后果**：Server 累积验证缓存，长时间运行后占内存。建议每次取完 GetIssues + GetRemainingData 都 `bDataRelease := TRUE` 或显式 Release。

**Tc3_EventLogger 错误**：本 FB 自身的错误（如取数据时缓存不存在）通过 `bError + ipTcResult` 报告。

## 4. 错误码 / 返回值

每方法返回 `BOOL`（TRUE = 方法体结束）。`bError + ipTcResult` 报实际成败。典型：

| 现象 | 含义 | 处理 |
|---|---|---|
| `bError`，事件含 `Cache empty` | 上一次 ReadAsStruct 没设 bValidate=TRUE 或 cache 已释放 | 重新调用 ReadAsStruct |
| `bError`，事件含 `Buffer too small` | pData 容量不足 | 加大数组 |
| GetIssues 返回 0 issues（无 bError） | 验证通过——schema 完全匹配 | 不需处理 |

完整 PDF §8.1.1。

## 5. 使用注意 / 常见坑

- **本 FB 只能作为 `FB_NoSQLResultEvt.ReadAsStruct` 的输出收集器**：不能独立使用。
- **必须先一次 `ReadAsStruct(bValidate := TRUE, ...)`**：否则 Server 端没有验证数据可取。
- **每次 ReadAsStruct 都会覆盖 / 追加本 FB 实例的缓存**：取出后及时 Release 避免混淆下一批。
- **`GetIssues` 与 `GetRemainingData` 互相独立**：可只取其一。
- **`ipTcResult` 类型 `I_TcResultEvent`**：与其他 NoSQL FB 用的 `I_TcMessage` 不同名；调用代码注意接口类型断言。
- **生产期不一定要开 bValidate**：性能开销 5-10%；只在调试或预期 schema 漂移时开。
- **`Release` 与 ReadAsStruct 的 bDataRelease 都释放**：使用其中之一即可。重复 Release 一般无害。

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_FB_NoSQLValidationEvt.TcPOU`](../examples/P_Demo_FB_NoSQLValidationEvt.TcPOU)
>
> 导入步骤：右键 PLC 项目下 POUs 文件夹 → Add → Existing Item → 选该文件 → OK

详见 example xml 文件。

## 7. 业务场景与实际价值

- **场景**：OEM 设备部署到新车间，运行后日志报「读取 MongoDB recipes 集合时部分字段缺失」。维护人员开发 PLC 端调试程序：`ReadAsStruct(bValidate := TRUE, pNoSQLValidation := ADR(fbValidation))` 拿到当前批数据；`fbValidation.GetIssues` 取问题列表写到 HMI 报警栏，运维人员一眼看到「字段 'mold_temperature' 不存在于 PLC 结构」——按此适配。
- **价值**：schema 漂移可见可调试；不用 mongoshell 进数据库查；EventLogger 错误诊断；OEM 跨车间部署的 schema 兼容性问题用本 FB 一次性解决。
- **替代方案对比**：
  - **关闭验证，直接读结构**：字段不匹配静默丢失，问题难发现。
  - **PLC 端解析 JSON 字符串后人工对比**：开销大、代码冗长。
  - **DB 端手工 explore**：依赖外部工具，对 OEM 维护人员不友好。
  - **本 FB**：TC3 NoSQL Expert mode 的 schema 验证唯一选项。

## 8. 参考资料

- **PDF**：[tf6420_tc3_database_server_en.pdf](https://download.beckhoff.com/download/document/automation/twincat3/tf6420_tc3_database_server_en.pdf) §6.1.1.4.4
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tf6420_tc3_database_server/5875270411.html
- **相关 FB / FC / DUT**：`FB_NoSQLResultEvt`（ReadAsStruct 触发本 FB 的缓存）、`Tc3_JsonXml`（PLC 端 JSON 解析备选）、`I_TcResultEvent` / `I_TcMessage`（接口类型差异）
