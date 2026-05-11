# FB_TcSourceInfo

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc3_EventLogger` |
| Library Version | `1.6.2` |
| Type | `FUNCTION_BLOCK` |
| Category | `Function block` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc3_EventLogger_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tcplclib_tc3_eventlogger/5003264011.html |
| Verified | 2026-05-11 ✅ |
| InfoSys-checked | ✅ 2026-05-11 |
| Status | `verified` |
| Example | [`examples/P_Demo_FB_TcSourceInfo.xml`](../examples/P_Demo_FB_TcSourceInfo.xml) |

---

## 1. 功能简述

`FB_TcSourceInfo` 代表事件的**来源信息**（SourceName / SourceID / SourceGuid），实现 `I_TcSourceInfo` 接口。

在 PLC 里实例化后通过 setter 配置 SourceName/SourceID/SourceGuid，再传给 `FB_TcAlarm.Create()` / `FB_TcMessage.Create()` 等方法的 `ipSourceInfo` 参数；传 `0` 时 EventLogger 用 PLC 实例的符号路径作为默认 SourceName。

## 2. 接口定义

### VAR_INPUT

无。

### VAR_OUTPUT

无。

### VAR_IN_OUT

无。

## 3. 行为说明

FB_TcSourceInfo 不维护状态机，只是一个携带 SourceName/SourceID/SourceGuid 三字段的容器。三个字段都有 getter 与 setter；通常在 FB_init 阶段配置好，之后传给 alarm/message 用。

**方法**：`Clear` 清空全部字段；`ExtendName` 给现有 SourceName 加后缀（适合多工位共享代码场景）；`ResetToDefault` 还原到 EventLogger 默认（用 PLC 符号路径）。

**多 PLC / 多工位场景**：每个工位实例化自己的 FB_TcSourceInfo 配置不同 SourceID，让 EventLogger 能在事件日志里精确区分"哪台机器哪个工位"出的事件。

## 4. 错误码 / 返回值

本方法/属性不返回数值（`VOID` 或 getter 直接返回引用）。状态通过 EventLogger 的事件日志间接反映。

## 5. 使用注意 / 常见坑

- SourceName/SourceID/SourceGuid 三字段都要配，否则 EventLogger 用默认值——可能与本设备实际不符。（工程经验补充）
- 修改 SourceInfo 后只对**未来的事件**生效——已 Raise 过的事件 SourceInfo 已固化。
- 多 alarm 共享同一 FB_TcSourceInfo 时，修改它影响所有 alarm；通常每个 alarm 独立 FB_TcSourceInfo。（工程经验补充）
- 默认 SourceName 是 PLC 实例符号路径——动态生成的 alarm 路径可能不唯一，需要主动 ExtendName。（工程经验补充）

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_FB_TcSourceInfo.xml`](../examples/P_Demo_FB_TcSourceInfo.xml)（PLCopenXML，可直接导入 TwinCAT 3 XAE）
>
> 导入步骤：右键 PLC 项目 → Import PLCopenXML → 选该文件 → OK

```iecst
// 详见 examples 目录下的 .xml 文件
```

## 7. 业务场景与实际价值

多工位共享同一份 PLC 代码：每个工位的 FB 实例初始化时配置自己的 FB_TcSourceInfo 用工位号区分


事后审计能精确定位"哪台设备哪个工位"出故障，而不是只看到 PLC 符号路径


把工位号塞 Arguments → 信息混在事件参数里不够结构化；本 FB 专门承载来源更规范


## 8. 参考资料

- **PDF**：[TwinCAT_3_PLC_Lib_Tc3_EventLogger_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc3_EventLogger_EN.pdf) §3.12
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tcplclib_tc3_eventlogger/5003264011.html
- **相关**：`FB_TcSourceInfo.Clear`, `FB_TcSourceInfo.ExtendName`, `FB_TcSourceInfo.ResetToDefault`, `FB_TcEventBase.ipSourceInfo`
