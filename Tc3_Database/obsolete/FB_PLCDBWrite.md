# FB_PLCDBWrite

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc3_Database` |
| Library Version | `1.14.1` |
| Type | `FUNCTION_BLOCK` |
| Category | `Obsolete` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/tf6420_tc3_database_server_en.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tf6420_tc3_database_server/6183400459.html |
| Verified | 2026-06-03 ✅ |
| InfoSys-checked | ✅ 2026-06-03 |
| Status | `verified` |
| Example | [`examples/P_Demo_FB_PLCDBWrite.TcPOU`](../examples/P_Demo_FB_PLCDBWrite.TcPOU) |

---

## 1. 功能简述

⚠️ **已废弃（obsolete）** —— 早期版本的 PLC Expert mode 数据写入 FB（PDF §6.1.4.2.5）。三个方法 `Write` / `WriteBySymbol` / `WriteStruct` 与 `FB_PLCDBWriteEvt` 完全一致；差别仅在输出接口名 `ipTcResultEvent : I_TcResultEvent`（旧）vs `ipTcResult : I_TcMessage`（新）。新项目用 `FB_PLCDBWriteEvt`。

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
    ipTcResultEvent: Tc3_EventLogger.I_TcResultEvent;
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `bBusy` | `BOOL` | 方法运行中。 |
| `bError` | `BOOL` | 错误置 TRUE。 |
| `ipTcResultEvent` | `Tc3_EventLogger.I_TcResultEvent` | 旧式事件接口。 |

### VAR_IN_OUT

无。

### Method: `Write`

```iecst
METHOD Write : BOOL
VAR_INPUT
    hDBID: UDINT;
    sTableName: T_MaxString;
    pValue: POINTER TO BYTE;
    cbValue: UDINT;
    sDBSymbolName: T_MaxString;
    eDBWriteMode: E_WriteMode := E_WriteMode.eADS_TO_DB_Append;
    nRingBuffParameter: UDINT;
END_VAR
```

参数同 `FB_PLCDBWriteEvt.Write`——单值写入标准 4 列表，4 种 E_WriteMode（Append / Update / RingBuffer_Time / RingBuffer_Count）。

### Method: `WriteBySymbol`

签名 `METHOD WriteBySymbol : BOOL`，VAR_INPUT 含 hDBID / sTableName / stADSDevice / stSymbol / eDBWriteMode / nRingBuffParameter。Server 跨 ADS 设备读符号后写。详情参考 `FB_PLCDBWriteEvt.WriteBySymbol`。

### Method: `WriteStruct`

签名 `METHOD WriteStruct : BOOL`，VAR_INPUT 含 hDBID / sTableName / pRecord / cbRecord / pColumnNames / cbColumnNames。任意自定义表写入。详情参考 `FB_PLCDBWriteEvt.WriteStruct`。

## 3. 行为说明

与 `FB_PLCDBWriteEvt` 完全一致的行为语义——三种写入方法覆盖不同场景：`Write` 把单个 PLC 数值（按地址 + 长度）以「Name + Value」形式写入 Beckhoff 标准 4 列表，配合 `E_WriteMode` 四种模式控制日志保留策略（Append 追加 / Update 按 Name 覆盖 / RingBuffer 按时间窗或行数滚动）；`WriteBySymbol` 让 Server 主动通过 ADS 去 `stADSDevice` 描述的别的 PLC / CX 设备读取 `stSymbol` 对应符号后写入；`WriteStruct` 把任意 PLC 自定义结构按 `pColumnNames^` 列名数组顺序写入自定义表。每方法周期调直到返回 TRUE，然后查 `bError` + `ipTcResultEvent`。`Write` 与 `WriteBySymbol` 支持 RingBuffer 模式，`WriteStruct` 不支持（按 Append 语义）。

**与 Evt 版差别**：仅输出接口字段名 / 类型不同；方法签名 / 参数 / RingBuffer 模式 / 状态机完全一致。新项目迁移只需替换 FB 类型与字段名。

**为何保留**：Beckhoff 向后二进制兼容；老 PLC 工程升级 TwinCAT Runtime 后本 FB 仍可用。

## 4. 错误码 / 返回值

方法返回 `BOOL`。`bError + ipTcResultEvent` 报实际结果。典型错误：String too long、Cannot convert、Connection lost、Constraint violation。完整 PDF §8.1.1。

## 5. 使用注意 / 常见坑

- **⚠️ 已废弃**：新项目用 `FB_PLCDBWriteEvt`。
- **行为细节与 Evt 版完全一致**：套用所有 §5 注意事项。
- **`E_WriteMode` 4 种**：Append / Update / RingBuffer_Time / RingBuffer_Count；意义不变。
- **`WriteStruct` 列名顺序**：与结构体字段顺序严格一致。

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_FB_PLCDBWrite.TcPOU`](../examples/P_Demo_FB_PLCDBWrite.TcPOU)
>
> 导入步骤：右键 PLC 项目下 POUs 文件夹 → Add → Existing Item → 选该文件 → OK

详见 example xml 文件。

## 7. 业务场景与实际价值

- **场景**：老 OEM 工程的数据采集模块用本 FB；新模块迁移到 `FB_PLCDBWriteEvt`。
- **价值**：老工程二进制兼容；新项目应迁移。
- **替代方案对比**：`FB_PLCDBWriteEvt`（推荐）；本 FB 仅兼容用。

## 8. 参考资料

- **PDF**：[tf6420_tc3_database_server_en.pdf](https://download.beckhoff.com/download/document/automation/twincat3/tf6420_tc3_database_server_en.pdf) §6.1.4.2.5
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tf6420_tc3_database_server/6183400459.html
- **相关 FB / FC / DUT**：`FB_PLCDBWriteEvt`（现代版）、`ST_StandardRecord`、`E_WriteMode`、`ST_ADSDevice` / `ST_Symbol`、`MAX_DBCOLUMNS`
