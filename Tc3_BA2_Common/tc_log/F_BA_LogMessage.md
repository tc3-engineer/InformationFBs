# F_BA_LogMessage

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc3_BA2_Common` |
| Library Version | `1.0.2` |
| Type | `FUNCTION` |
| Category | `Functions / Universal / TcLog` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc3_BA2_Common_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tcplclib_tc3_ba2_common/10785106187.html |
| Verified | 2026-06-03 ✅ |
| InfoSys-checked | ✅ 2026-06-03 |
| Status | `verified` |
| Example | [`examples/P_Demo_F_BA_LogMessage.TcPOU`](../examples/P_Demo_F_BA_LogMessage.TcPOU) |

---

## 1. 功能简述

把一条文本消息写入 TwinCAT ADS Logger。`nLogType` 决定消息分类掩码（默认 ERROR），`sLogCode` 为前缀代码，`sLogText` 为消息正文。内部用 `FB_FormatString` + ADSLOG 实现。

## 2. 接口定义

### 完整声明

```iecst
FUNCTION F_BA_LogMessage
VAR_INPUT
  nLogType    : DWORD     := ADSLOG_MSGTYPE_ERROR;
  sLogCode    : STRING    := '';
  sLogText    : T_MaxString;
END_VAR
```

### VAR_INPUT 引脚

| 名称 | 类型 | 默认值 | 说明 |
|---|---|---|---|
| `nLogType` | `DWORD` | `ADSLOG_MSGTYPE_ERROR` | 日志类型 , which can be set as a mask. The message is then output depending on the setting of this mask. The mask for ADSLOG_MSGTYPE_LOG is set internally as well. |
| `sLogCode` | `STRING` | `''` | 附加在消息前的文本前缀. |
| `sLogText` | `T_MaxString` | - | 消息正文 |

### VAR_IN_OUT

无。


## 3. 行为说明

把一条文本消息写入 TwinCAT ADS Logger。`nLogType` 决定消息分类掩码（默认 ERROR），`sLogCode` 为前缀代码，`sLogText` 为消息正文。内部用 `FB_FormatString` + ADSLOG 实现。 接入参数：`nLogType`, `sLogCode`, `sLogText`。每个参数的类型与默认值见 §2 接口定义。 本 FC 是 *无状态* 的纯函数：每次调用独立计算结果，不维护任何内部历史；多任务 / 多线程调用安全；可在 PRG / FB / METHOD / 表达式中任意位置使用。 日志通过 ADSLOG 接口送到 TwinCAT 输出窗口与系统事件日志；运行期一直产生日志会拖慢调试输出，发布版建议把 `nLogType` 至少调到 WARNING 或更高级别。 典型工程场景：调试期把关键事件（参数变化、模式切换）写入 ADS Log 便于事后排查。

## 4. 错误码 / 返回值



PDF + InfoSys 均未列错误码（无返回值或返回类型未明确）。

## 5. 使用注意 / 常见坑

- 调用前必须确认 `Tc3_BA2_Common` 库已 reference（版本 ≥ 1.0.2）。
- FC 类无状态，多线程 / 多 task 调用安全；GVL 是常量集合，运行时只读。
- LogMessage 日志会输出到 TwinCAT 调试输出窗口，发布时建议把 `nLogType` 改为 WARNING 或更高级别避免日志泛滥。（工程经验补充）

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_F_BA_LogMessage.TcPOU`](../examples/P_Demo_F_BA_LogMessage.TcPOU)
>
> 导入步骤：右键 PLC 项目下 POUs 文件夹 → Add → Existing Item → 选该文件 → OK

详见 example xml 文件。

## 7. 业务场景与实际价值

- **场景**：调试期把关键事件（参数变化、模式切换）写入 ADS Log 便于事后排查。
- **价值**：一行 FC 替代手工调用 `ADSLOGSTR` + 拼接前缀的多步骤。
- **替代方案对比**：`ADSLOGSTR(...)` 加自定义前缀格式化（与本 FC/GVL 相比，体现统一化 / 跨平台正确性 / 代码量节省等优势）。

## 8. 参考资料

- **PDF**：[TwinCAT_3_PLC_Lib_Tc3_BA2_Common_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc3_BA2_Common_EN.pdf) §4.3.1.4.3.1
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tcplclib_tc3_ba2_common/10785106187.html
- **相关枚举 / 结构**：见 PDF §4.1（DUTs）
