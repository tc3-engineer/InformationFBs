# ipSourceInfo

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc3_EventLogger` |
| Library Version | `1.6.2` |
| Type | `PROPERTY` |
| Category | `FB_TcEventBase` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc3_EventLogger_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tcplclib_tc3_eventlogger/5286521355.html |
| Verified | 2026-05-11 ✅ |
| InfoSys-checked | ✅ 2026-05-11 |
| Status | `verified` |
| Example | [`examples/P_Demo_ipSourceInfo.xml`](../examples/P_Demo_ipSourceInfo.xml) |

---

## 1. 功能简述

`FB_TcEventBase.ipSourceInfo` 是只读属性，返回当前事件的 `I_TcSourceInfo` 接口指针——代表事件来源信息（SourceName / SourceID / SourceGuid）。

默认情况下源信息由 EventLogger 在 `Create()` 时自动填——以 PLC 实例的符号路径作为 SourceName。如果手动传入了 `FB_TcSourceInfo` 实例，本属性返回的就是那个实例。

## 2. 接口定义

### VAR_INPUT

无。

### VAR_OUTPUT

无。

### VAR_IN_OUT

无。

## 3. 行为说明

属性 getter 返回 `I_TcSourceInfo` 接口指针。通过该接口可以读出 SourceName / SourceID / SourceGuid 三个字段，或调用 `ExtendName` / `Clear` / `ResetToDefault` 等方法修改源信息。EventLogger 在事件分发与持久化时把 SourceInfo 与事件一起记录，便于事后审计追溯事件的来源设备。

**典型用法**：listener 收到事件后用本属性取 SourceInfo 做日志归档；或在 alarm Raise 之前调`ipSourceInfo.ExtendName(sExtName := 'motor1')` 给默认 SourceName 加后缀，让多工位共享同一份 PLC 代码时每个工位的报警都能精确定位到具体设备。默认情况下 EventLogger 用 PLC 实例的符号路径作为 SourceName，多数场景已经够用。

## 4. 错误码 / 返回值

本方法返回接口指针（interface pointer）。

| 返回值 | 含义 |
|---|---|
| 非 `0` | 调用成功，可继续通过接口调用相关方法 |
| `0` | 未找到匹配实例 / 参数无效 |

## 5. 使用注意 / 常见坑

- 默认 SourceInfo 是 PLC 符号路径——动态生成的 alarm 实例可能符号路径不唯一，需要主动 ExtendName。（工程经验补充）
- 修改 SourceInfo 后只对**未来的事件**生效；已 Raise 过的事件 SourceInfo 已固化。
- 多个 alarm 共享一个 FB_TcSourceInfo 时，修改它会影响所有 alarm——通常每个 alarm 用独立 SourceInfo。（工程经验补充）

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_ipSourceInfo.xml`](../examples/P_Demo_ipSourceInfo.xml)（PLCopenXML，可直接导入 TwinCAT 3 XAE）
>
> 导入步骤：右键 PLC 项目 → Import PLCopenXML → 选该文件 → OK

```iecst
// 详见 examples 目录下的 .xml 文件
```

## 7. 业务场景与实际价值

多工位共享一份代码（数组实例化）时，给每个 alarm 实例指定不同工位号作为 SourceInfo


事后审计能精确定位"哪台机器哪个工位"出的故障，而不是只看到 PLC 符号路径


把工位号塞 Arguments → 信息混在事件参数里不够结构化；用本属性专门承载来源信息更规范


## 8. 参考资料

- **PDF**：[TwinCAT_3_PLC_Lib_Tc3_EventLogger_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc3_EventLogger_EN.pdf) §3.9.10
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tcplclib_tc3_eventlogger/5286521355.html
- **相关**：`FB_TcSourceInfo`, `FB_TcSourceInfo.ExtendName`
