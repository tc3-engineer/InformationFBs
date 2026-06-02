# ExportLoggedEvents

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc3_EventLogger` |
| Library Version | `1.6.2` |
| Type | `METHOD` |
| Category | `FB_TcEventLogger` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc3_EventLogger_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tcplclib_tc3_eventlogger/10361941643.html |
| Verified | 2026-05-11 ✅ |
| InfoSys-checked | ✅ 2026-05-11 |
| Status | `verified` |
| Example | [`examples/P_Demo_ExportLoggedEvents.TcPOU`](../examples/P_Demo_ExportLoggedEvents.TcPOU) |

---

## 1. 功能简述

`FB_TcEventLogger.ExportLoggedEvents()` 异步把 EventLogger 持久化日志中的事件导出到 CSV 文件。支持通过 `I_TcEventExportSettings`（即 `FB_TcEventCsvExportSettings` 实例）按规则筛选要导出的事件子集。

**返回类型是 BOOL**——TRUE 表示异步处理完成。配合 `bError` + `hrErrorCode` 反映成败。

## 2. 接口定义

### VAR_INPUT

```iecst
VAR_INPUT
    ipExportSettings : I_TcEventExportSettings;
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `ipExportSettings` | `I_TcEventExportSettings` | 导出过滤器；传 0 导出全部 |


### VAR_OUTPUT

```iecst
VAR_OUTPUT
    bError : BOOL;
    hrErrorCode : HRESULT;
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `bError` | `BOOL` | TRUE = 导出失败 |
| `hrErrorCode` | `HRESULT` | 错误码 |


### VAR_IN_OUT

```iecst
VAR_IN_OUT
    sFileName : STRING;
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `sFileName` | `STRING` | 导出 CSV 文件的完整路径（含文件名与扩展名） |


## 3. 行为说明

异步导出：每周期调用同一方法推进状态。请求未完成时返回 FALSE；完成时 TRUE。文件路径由 VAR_IN_OUT CONSTANT `sFileName : STRING` 传入。文件已存在会被覆盖。

`ipExportSettings := 0` 时导出**全部**事件历史；传 `FB_TcEventCsvExportSettings` 实例可按时间范围 / 严重级别 / 事件类等条件筛选。导出过程不阻塞 PLC 周期——大量事件导出可能耗时数秒。

**典型流程**：导出 → ClearLoggedEvents 清理旧日志 → 完成归档。

## 4. 错误码 / 返回值

本方法/函数返回 `BOOL`。

| 返回值 | 含义 | 处理建议 |
|---|---|---|
| `TRUE` | 异步导出已完成 | 读 bError 判断成败；可继续后续清理 |
| `FALSE` | 导出仍在进行 | 下一周期继续调用同方法保持轮询 |

## 5. 使用注意 / 常见坑

- 文件路径必须 TwinCAT runtime 有写权限——典型放 `C:\Temp\` 或 `C:\ProgramData\Beckhoff\`。（工程经验补充）
- BOOL 返回值是"完成状态"不是"成功/失败"——必须额外检查 bError。
- 现有同名文件会被**覆盖**——批量归档时给文件名加时间戳。（工程经验补充）
- 异步方法：每周期都要调用同一方法保持轮询。

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_ExportLoggedEvents.TcPOU`](../examples/P_Demo_ExportLoggedEvents.TcPOU)（TwinCAT 3 原生 .TcPOU，可直接拖入 XAE 的 PLC POUs 文件夹）
>
> 导入步骤：右键 PLC 项目下 POUs 文件夹 → Add → Existing Item → 选该文件 → OK

```iecst
// 详见 examples 目录下的 .xml 文件
```

## 7. 业务场景与实际价值

每日 23:00 自动导出当日全部事件到带日期的 CSV，配合 ClearLoggedEvents 做完整归档


一次调用 + 轮询完成大批量事件导出，无需自建数据库 SELECT


自建 SQL Server INSERT → 阻塞 PLC 周期、网络中断风险大；通过 OPC UA Server 拉取 → 需要额外 license


## 8. 参考资料

- **PDF**：[TwinCAT_3_PLC_Lib_Tc3_EventLogger_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc3_EventLogger_EN.pdf) §3.10.6
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tcplclib_tc3_eventlogger/10361941643.html
- **相关**：`FB_TcEventCsvExportSettings`, `FB_TcEventLogger.ClearLoggedEvents`
