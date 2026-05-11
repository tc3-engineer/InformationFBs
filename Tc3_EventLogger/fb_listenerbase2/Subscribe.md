# Subscribe

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc3_EventLogger` |
| Library Version | `1.6.2` |
| Type | `METHOD` |
| Category | `FB_ListenerBase2` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc3_EventLogger_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tcplclib_tc3_eventlogger/5050398219.html |
| Verified | 2026-05-11 ✅ |
| InfoSys-checked | ✅ 2026-05-11 |
| Status | `verified` |
| Example | [`examples/P_Demo_Subscribe.xml`](../examples/P_Demo_Subscribe.xml) |

---

## 1. 功能简述

`FB_ListenerBase2.Subscribe()` 把 listener 注册到 EventLogger，开始接收事件回调。支持分别为 message 与 alarm 配置过滤器（`POINTER TO ITcEventFilterConfig`）。

传 0 = 接收对应类型的所有事件；传具体过滤器实例 = 只接收匹配的事件。

## 2. 接口定义

### VAR_INPUT

```iecst
VAR_INPUT
    ipMessageFilterConfig : POINTER TO ITcEventFilterConfig;
    ipAlarmFilterConfig : POINTER TO ITcEventFilterConfig;
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `ipMessageFilterConfig` | `POINTER TO ITcEventFilterConfig` | message 事件过滤器；传 0 接收全部 |
| `ipAlarmFilterConfig` | `POINTER TO ITcEventFilterConfig` | alarm 事件过滤器；传 0 接收全部 |


### VAR_OUTPUT

无。

### VAR_IN_OUT

无。

## 3. 行为说明

一次性注册：通常在 FB_init 或第一次扫描调一次。重复注册返回 `ADS_E_EXISTS`，本身无副作用。

**过滤器选择**：`ipMessageFilterConfig` 控制 message 事件的接收范围；`ipAlarmFilterConfig` 控制 alarm 事件。两者独立——可以只订 alarm 不订 message，反之亦然。过滤器实例通常是 `FB_TcEventFilter` 配置好后传入。

订阅成功后 EventLogger 把后续匹配事件加入本 listener 的内部队列，等下次 Execute 调用回调。

## 4. 错误码 / 返回值

本方法返回 `HRESULT`（32 位有符号整数）。`SUCCEEDED(hr)` 为 TRUE 表示调用成功。

| HRESULT | 含义 | 处理建议 |
|---|---|---|
| `S_OK` | 订阅成功 | 继续周期调用 Execute |
| `ADS_E_EXISTS` | 已订阅过 | 用 latch 跳过重复调用 |
| `其他错误` | ⚠️ PDF 未列详细码 | 查 ADS Return Codes |

## 5. 使用注意 / 常见坑

- Subscribe 一次性调用——用 latch 包裹。
- 过滤器传 0 = 接收全部——大型系统事件量大时建议用过滤器减少回调开销。（工程经验补充）
- `Subscribe2` 是简化版（单过滤器）——新工程推荐用 Subscribe2。

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_Subscribe.xml`](../examples/P_Demo_Subscribe.xml)（PLCopenXML，可直接导入 TwinCAT 3 XAE）
>
> 导入步骤：右键 PLC 项目 → Import PLCopenXML → 选该文件 → OK

```iecst
// 详见 examples 目录下的 .xml 文件
```

## 7. 业务场景与实际价值

HMI 后端 listener 只接收 Error 及以上级别的 alarm 事件以减小回调负担


过滤器机制让 listener 只关心感兴趣的事件


`Subscribe2` 单过滤器 → 新工程推荐；本方法分开过滤器更精细


## 8. 参考资料

- **PDF**：[TwinCAT_3_PLC_Lib_Tc3_EventLogger_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc3_EventLogger_EN.pdf) §3.5.7
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tcplclib_tc3_eventlogger/5050398219.html
- **相关**：`FB_ListenerBase2.Subscribe2`, `FB_ListenerBase2.Unsubscribe`, `FB_ListenerBase2.Execute`, `FB_TcEventFilter`
