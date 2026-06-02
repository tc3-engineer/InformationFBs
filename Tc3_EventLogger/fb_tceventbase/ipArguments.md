# ipArguments

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc3_EventLogger` |
| Library Version | `1.6.2` |
| Type | `PROPERTY` |
| Category | `FB_TcEventBase` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc3_EventLogger_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tcplclib_tc3_eventlogger/5050737547.html |
| Verified | 2026-05-11 ✅ |
| InfoSys-checked | ✅ 2026-05-11 |
| Status | `verified` |
| Example | [`examples/P_Demo_ipArguments.TcPOU`](../examples/P_Demo_ipArguments.TcPOU) |

---

## 1. 功能简述

`FB_TcEventBase.ipArguments` 是一个**只读属性**（getter），返回当前事件的 `I_TcArguments` 接口指针——用于在 `Raise()` 之前给事件附加结构化参数（int / real / bool / string …），或在收到事件后读出参数。

## 2. 接口定义

### VAR_INPUT

无。

### VAR_OUTPUT

无。

### VAR_IN_OUT

无。

## 3. 行为说明

属性 getter 返回 `I_TcArguments` 接口指针。通过该接口可调用 `AddInt` / `AddReal` / `AddString` / `AddBool` 等 20 多个 Add 方法把不同类型的参数依次压入参数列表；事件 Raise 时 EventLogger 把整张参数表与事件元数据一起持久化到日志，HMI 显示事件文本时按顺序把参数填进文本模板的占位符 `{0}` `{1}` `{2}`…

**典型用法**：在 `Raise()` 之前调一连串 Add* 方法压入工艺数据，例如`alarm.ipArguments.AddString(sValue := 'M-01')`、`alarm.ipArguments.AddReal(fValue := 95.5)`；之后 `Raise()` 让 EventLogger 把「电机 M-01 温度 95.5°C 过高」这种结构化文本送给 HMI / 持久化 / 监听器。参数顺序与文本模板占位符严格对应——顺序错了文本会乱填。

## 4. 错误码 / 返回值

本方法返回接口指针（interface pointer）。

| 返回值 | 含义 |
|---|---|
| 非 `0` | 调用成功，可继续通过接口调用相关方法 |
| `0` | 未找到匹配实例 / 参数无效 |

## 5. 使用注意 / 常见坑

- 属性是 getter，每次访问可能拿到同一接口实例——不要持有过久的引用。（工程经验补充）
- Add* 方法必须在 Raise 之前调用，否则填进去的参数对前一次 Raise 无效。
- 参数顺序与文本模板 `{0}` `{1}` 严格对应。

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_ipArguments.TcPOU`](../examples/P_Demo_ipArguments.TcPOU)（TwinCAT 3 原生 .TcPOU，可直接拖入 XAE 的 PLC POUs 文件夹）
>
> 导入步骤：右键 PLC 项目下 POUs 文件夹 → Add → Existing Item → 选该文件 → OK

```iecst
// 详见 examples 目录下的 .xml 文件
```

## 7. 业务场景与实际价值

alarm 文本 "电机 {0} 温度 {1}°C 过高" 的两个占位符填值


结构化参数 + EventLogger 自动文本填充，比手写字符串拼接更安全


`SetJsonAttribute` 写 JSON → 适合嵌套数据，本方式更适合标准类型；手写 CONCAT 字符串 → 多语言切换困难


## 8. 参考资料

- **PDF**：[TwinCAT_3_PLC_Lib_Tc3_EventLogger_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc3_EventLogger_EN.pdf) §3.9.9
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tcplclib_tc3_eventlogger/5050737547.html
- **相关**：`FB_TcArguments`, `FB_TcEventBase.ipSourceInfo`, `FB_TcAlarm.Raise`
