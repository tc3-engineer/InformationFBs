# SendMessageEx

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc3_EventLogger` |
| Library Version | `1.6.2` |
| Type | `METHOD` |
| Category | `FB_TcEventLogger` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc3_EventLogger_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tcplclib_tc3_eventlogger/5050857483.html |
| Verified | 2026-05-11 ✅ |
| InfoSys-checked | ✅ 2026-05-11 |
| Status | `verified` |
| Example | [`examples/P_Demo_SendMessageEx.TcPOU`](../examples/P_Demo_SendMessageEx.TcPOU) |

---

## 1. 功能简述

`FB_TcEventLogger.SendMessageEx()` 与 `SendMessage()` 功能相同——免实例发 message——区别在事件参数以 **`TcEventEntry` 结构体一次性传入**。

适用：事件定义已经是结构化数据（远程接收 / 配方加载）。

## 2. 接口定义

### VAR_INPUT

```iecst
VAR_INPUT
    stEventEntry : TcEventEntry;
    ipSourceInfo : I_TcSourceInfo := 0;
    nTimeStamp : ULINT := 0;
    ipArguments : I_TcArguments := 0;
END_VAR
```

| 名称 | 类型 | 默认值 | 说明 |
|---|---|---|---|
| `stEventEntry` | `TcEventEntry` | - | 事件入口（GUID + EventID + Severity） |
| `ipSourceInfo` | `I_TcSourceInfo` | `0` | 源信息接口；传 0 用默认 |
| `nTimeStamp` | `ULINT` | `0` | 时间戳：0 = 当前系统时间 |
| `ipArguments` | `I_TcArguments` | `0` | 参数接口；传 0 = 无参数 |


### VAR_OUTPUT

无。

### VAR_IN_OUT

无。

## 3. 行为说明

调用过程与 `SendMessage()` 完全一致：EventLogger 临时构造一个 message 对象 → 写入事件日志 → 分发给所有监听器 → 立即释放，调用方不持有任何 message 实例。区别只在事件参数来源——本方法用 `stEventEntry` 结构体一次性传入 GUID + EventID + Severity 三件套。

**参数细节**：`ipArguments` 可选附加预先填好的参数列表（用于文本占位符填充）；`nTimeStamp = 0` 用当前系统时间，非 0 时是 FILETIME 100ns 单位；`ipSourceInfo = 0` 用默认源信息（PLC 实例符号路径）。

## 4. 错误码 / 返回值

本方法返回 `HRESULT`（32 位有符号整数）。`SUCCEEDED(hr)` 为 TRUE 表示调用成功。

| HRESULT | 含义 | 处理建议 |
|---|---|---|
| `S_OK` | 消息已发送 | 继续业务 |
| `其他错误` | ⚠️ PDF 未列详细码 | 查 ADS Return Codes |

## 5. 使用注意 / 常见坑

- `stEventEntry` 必须有效——GUID 全 0 / EventID = 0 会让 HMI 显示空白。
- 边沿触发不要每周期发。
- Severity 是 stEventEntry 的一部分，注意与目标事件类配置一致。（工程经验补充）

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_SendMessageEx.TcPOU`](../examples/P_Demo_SendMessageEx.TcPOU)（TwinCAT 3 原生 .TcPOU，可直接拖入 XAE 的 PLC POUs 文件夹）
>
> 导入步骤：右键 PLC 项目下 POUs 文件夹 → Add → Existing Item → 选该文件 → OK

```iecst
// 详见 examples 目录下的 .xml 文件
```

## 7. 业务场景与实际价值

从配方文件加载事件清单后批量按结构体发送 message


结构体接口适合循环遍历事件清单批量发送


`SendMessage` 分字段 → 临时已知 GUID 时更直观；本方法适合事件清单已结构化


## 8. 参考资料

- **PDF**：[TwinCAT_3_PLC_Lib_Tc3_EventLogger_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc3_EventLogger_EN.pdf) §3.10.13
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tcplclib_tc3_eventlogger/5050857483.html
- **相关**：`FB_TcEventLogger.SendMessage`, `FB_TcEventLogger.SendMessageEx2`
