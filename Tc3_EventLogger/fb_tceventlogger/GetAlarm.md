# GetAlarm

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc3_EventLogger` |
| Library Version | `1.6.2` |
| Type | `METHOD` |
| Category | `FB_TcEventLogger` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc3_EventLogger_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tcplclib_tc3_eventlogger/5050786699.html |
| Verified | 2026-05-11 ✅ |
| InfoSys-checked | ✅ 2026-05-11 |
| Status | `verified` |
| Example | [`examples/P_Demo_GetAlarm.TcPOU`](../examples/P_Demo_GetAlarm.TcPOU) |

---

## 1. 功能简述

`FB_TcEventLogger.GetAlarm()` 通过 EventClass GUID + EventID + SourceInfo 查询已存在的 alarm 实例，拿到 `FB_TcAlarm` 引用以便对它调用 `Raise` / `Clear` / `Confirm`。

适合在 listener 回调或第三方代码里只持有 GUID + ID 而没有 alarm 实例引用的场景。

## 2. 接口定义

### VAR_INPUT

```iecst
VAR_INPUT
    eventClass : GUID;
    nEventId : UDINT;
    ipSourceInfo : I_TcSourceInfo := 0;
    fbAlarm : REFERENCE TO FB_TcAlarm;
END_VAR
```

| 名称 | 类型 | 默认值 | 说明 |
|---|---|---|---|
| `eventClass` | `GUID` | - | 事件类 GUID |
| `nEventId` | `UDINT` | - | 事件 ID |
| `ipSourceInfo` | `I_TcSourceInfo` | `0` | 源信息接口；传 0 用默认（PLC 符号路径，与 Create 时一致） |
| `fbAlarm` | `REFERENCE TO FB_TcAlarm` | - | REFERENCE 输出：成功时指向匹配的活动 alarm |


### VAR_OUTPUT

无。

### VAR_IN_OUT

无。

## 3. 行为说明

本方法接收 `eventClass` + `nEventId` + `ipSourceInfo`，找到匹配的活动 alarm 后通过 `fbAlarm : REFERENCE TO FB_TcAlarm` 引用参数返回。

**调用约定**：调用方先声明 `VAR fbAlarmRef : REFERENCE TO FB_TcAlarm;`，调用后 `fbAlarmRef` 指向EventLogger 内部 alarm 实例（不是拷贝），后续对它的方法调用都直接作用于活动 alarm。找不到时返回 `ADS_E_NOTFOUND`，引用未定义。

**典型用法**：listener 收到事件后凭事件 GUID/ID 拿到 alarm 引用做自动复位、或在跨模块通信时代替手写全局变量传递 alarm 引用。

## 4. 错误码 / 返回值

本方法返回 `HRESULT`（32 位有符号整数）。`SUCCEEDED(hr)` 为 TRUE 表示调用成功。

| HRESULT | 含义 | 处理建议 |
|---|---|---|
| `S_OK` | 找到 alarm，fbAlarm 引用已设置 | 继续调用 fbAlarm 方法 |
| `ADS_E_NOTFOUND` | 无匹配 alarm | fbAlarm 引用未定义，先检查 GUID/ID/SourceInfo 是否匹配 |
| `其他错误` | ⚠️ PDF 未列详细码 | 查 ADS Return Codes |

## 5. 使用注意 / 常见坑

- REFERENCE 类型变量必须先声明再传入，不能直接传 VAR 指针。（工程经验补充）
- `ipSourceInfo` 若与 Create 时传的不一致，会找不到 alarm（即便 GUID+ID 都对）。
- 找不到时返回 ADS_E_NOTFOUND 而不是 NULL——按 HRESULT 而不是引用判断。
- 拿到的引用是"指向 EventLogger 内部实例"——不要 __DELETE 也不要 Release。

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_GetAlarm.TcPOU`](../examples/P_Demo_GetAlarm.TcPOU)（TwinCAT 3 原生 .TcPOU，可直接拖入 XAE 的 PLC POUs 文件夹）
>
> 导入步骤：右键 PLC 项目下 POUs 文件夹 → Add → Existing Item → 选该文件 → OK

```iecst
// 详见 examples 目录下的 .xml 文件
```

## 7. 业务场景与实际价值

跨模块通信：A 模块创建 alarm，B 模块只持有 GUID/ID 需要查到 alarm 引用做后续操作


解耦 alarm 创建者与使用者，无需手写全局变量传递引用


把 alarm 实例放全局变量 → 模块间硬耦合；用本方法按 GUID 查询 → 弱耦合，事件清单是唯一接口


## 8. 参考资料

- **PDF**：[TwinCAT_3_PLC_Lib_Tc3_EventLogger_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc3_EventLogger_EN.pdf) §3.10.7
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tcplclib_tc3_eventlogger/5050786699.html
- **相关**：`FB_TcEventLogger.GetAlarmEx`, `FB_TcEventLogger.IsAlarmRaised`, `FB_TcAlarm`
