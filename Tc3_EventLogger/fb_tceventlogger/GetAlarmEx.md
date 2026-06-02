# GetAlarmEx

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc3_EventLogger` |
| Library Version | `1.6.2` |
| Type | `METHOD` |
| Category | `FB_TcEventLogger` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc3_EventLogger_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tcplclib_tc3_eventlogger/5050800779.html |
| Verified | 2026-05-11 ✅ |
| InfoSys-checked | ✅ 2026-05-11 |
| Status | `verified` |
| Example | [`examples/P_Demo_GetAlarmEx.TcPOU`](../examples/P_Demo_GetAlarmEx.TcPOU) |

---

## 1. 功能简述

`FB_TcEventLogger.GetAlarmEx()` 与 `GetAlarm()` 功能相同——查询已存在的 alarm 拿到引用——区别在事件参数以 **`TcEventEntry` 结构体一次性传入**。

适用：当事件定义已经是结构化数据时（如从远程 EventLogger 接收的事件、从配方加载的事件清单）免去拆字段。

## 2. 接口定义

### VAR_INPUT

```iecst
VAR_INPUT
    stEventEntry : TcEventEntry;
    ipSourceInfo : I_TcSourceInfo := 0;
    fbAlarm : REFERENCE TO FB_TcAlarm;
END_VAR
```

| 名称 | 类型 | 默认值 | 说明 |
|---|---|---|---|
| `stEventEntry` | `TcEventEntry` | - | 事件入口结构体（GUID + EventID + Severity） |
| `ipSourceInfo` | `I_TcSourceInfo` | `0` | 源信息接口；传 0 用默认 |
| `fbAlarm` | `REFERENCE TO FB_TcAlarm` | - | REFERENCE 输出：成功时指向匹配 alarm |


### VAR_OUTPUT

无。

### VAR_IN_OUT

无。

## 3. 行为说明

调用过程与 `GetAlarm()` 完全一致：根据事件键匹配活动 alarm 表，找到的实例通过`fbAlarm : REFERENCE TO FB_TcAlarm` 引用参数返回，未找到时返回 `ADS_E_NOTFOUND`。区别只在事件参数来源——本方法用 `stEventEntry` 结构体一次性打包传入 GUID + EventID + Severity 三件套。

**Severity 也参与匹配**：与 `GetAlarm` 不同，这里 Severity 是查询键的一部分；同 GUID+EventID 不同 Severity 会被认作不同 alarm 实例（即 Severity 升级版的同名 alarm 是新的实例）。实际工程里要注意保持 Severity 一致，否则 GetAlarmEx 找不到 alarm 但 GetAlarm 能找到。

## 4. 错误码 / 返回值

本方法返回 `HRESULT`（32 位有符号整数）。`SUCCEEDED(hr)` 为 TRUE 表示调用成功。

| HRESULT | 含义 | 处理建议 |
|---|---|---|
| `S_OK` | 找到 alarm | 继续使用 fbAlarm 引用 |
| `ADS_E_NOTFOUND` | 无匹配 alarm | 检查 stEventEntry / ipSourceInfo |
| `其他错误` | ⚠️ PDF 未列详细码 | 查 ADS Return Codes |

## 5. 使用注意 / 常见坑

- Severity 字段也参与匹配——同 GUID+EventID 不同 Severity 算不同 alarm。
- REFERENCE 输出变量必须先声明。（工程经验补充）
- 找不到时 fbAlarm 引用未定义，HRESULT 是唯一可靠判断。

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_GetAlarmEx.TcPOU`](../examples/P_Demo_GetAlarmEx.TcPOU)（TwinCAT 3 原生 .TcPOU，可直接拖入 XAE 的 PLC POUs 文件夹）
>
> 导入步骤：右键 PLC 项目下 POUs 文件夹 → Add → Existing Item → 选该文件 → OK

```iecst
// 详见 examples 目录下的 .xml 文件
```

## 7. 业务场景与实际价值

从远程 EventLogger 接收事件后凭 TcEventEntry 查到本地对应 alarm 引用


结构体接口更适合"事件清单已结构化"的场景


`GetAlarm` 分字段 → 适合已知具体 GUID/ID 的场景；本方法适合事件已经打包的场景


## 8. 参考资料

- **PDF**：[TwinCAT_3_PLC_Lib_Tc3_EventLogger_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc3_EventLogger_EN.pdf) §3.10.8
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tcplclib_tc3_eventlogger/5050800779.html
- **相关**：`FB_TcEventLogger.GetAlarm`, `FB_TcEventLogger.IsAlarmRaisedEx`
