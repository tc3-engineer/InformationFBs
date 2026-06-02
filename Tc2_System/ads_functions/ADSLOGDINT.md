# ADSLOGDINT

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc2_System` |
| Library Version | `1.17.3` |
| Type | `FUNCTION` |
| Category | `ADS functions` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_System_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tcplclib_tc2_system/31030539.html |
| Verified | 2026-05-20 ✅ |
| InfoSys-checked | ✅ 2026-05-20 |
| Status | `verified` |
| Example | [`examples/P_Demo_ADSLOGDINT.TcPOU`](../examples/P_Demo_ADSLOGDINT.TcPOU) |

---

## 1. 功能简述

ADSLOGDINT 是一个函数（FUNCTION）：在调用瞬间向屏幕弹一个可定制文本的消息框并在系统事件日志里写一条记录。文本里可以用 `%d` 占位符嵌入一个 DINT（4 字节有符号整型）值。返回 `DINT`：0 = 成功，其他为错误码。**必须配 R_TRIG / F_TRIG 边沿触发使用**——PLC 程序周期性执行，直接周期调用会瞬间刷屏。

## 2. 接口定义

### VAR_INPUT

```iecst
VAR_INPUT
    msgCtrlMask : DWORD;
    msgFmtStr   : T_MaxString;
    dintArg     : DINT;
END_VAR
```

| 名称 | 类型 | 默认值 | 说明 |
|---|---|---|---|
| `msgCtrlMask` | `DWORD` | - | 消息控制位掩码，决定消息类型与输出方式（弹框 / 写日志）。详见下方常量表。 |
| `msgFmtStr` | `T_MaxString` | - | 格式化字符串。可在任意位置嵌 `%d` 用于 `dintArg` 占位。消息长度上限 253 字节（含字符串终止符）。 |
| `dintArg` | `DINT` | - | 要嵌入到消息文本中的整数值。 |

### VAR_OUTPUT

```iecst
(* FUNCTION 返回 DINT：0 = 成功，其他 = 错误码 *)
FUNCTION ADSLOGDINT : DINT
```

FUNCTION 返回值类型：`DINT`（详见 §4）。

### VAR_IN_OUT

无。

## 3. 行为说明

**调用语义**：FUNCTION 类型，同步执行，调用即出值。返回值 0 = 成功，其他为错误码。

**`%d` 占位符**：格式化字符串中第一个 `%d` 会被 `dintArg` 替换；不带 `%d` 则原文输出。

**必须边沿触发**：PLC 程序周期执行，如果在主循环直接调用会每周期都弹框/日志。标准用法：用 `R_TRIG` 把业务事件转成 `Q` 上升沿，再 `IF R_TRIG.Q THEN ADSLOGDINT(...); END_IF;`，这样事件每次出现只弹一次。

**`msgCtrlMask` 组合**：典型 `ADSLOG_MSGTYPE_HINT OR ADSLOG_MSGTYPE_MSGBOX`（提示 + 弹框）；`ADSLOG_MSGTYPE_ERROR OR ADSLOG_MSGTYPE_LOG`（错误 + 只写日志不弹框，适合生产）。

**陷阱**：消息长度 253 字节，超出会被截断；MSGBOX 在 Windows CE 不可用，CE 上只能用 LOG。

## 4. 错误码 / 返回值

返回 `DINT`：0 = 成功；其他错误码 PDF/InfoSys 在本节未列出（⚠️ 待人工确认），属 ADS 通用错误码范围。


**`msgCtrlMask` 控制位**（可 OR 组合）：

| 常量 | 含义 |
|---|---|
| `ADSLOG_MSGTYPE_HINT` | 消息类型为提示 |
| `ADSLOG_MSGTYPE_WARN` | 消息类型为警告 |
| `ADSLOG_MSGTYPE_ERROR` | 消息类型为错误 |
| `ADSLOG_MSGTYPE_LOG` | 消息写入系统日志 |
| `ADSLOG_MSGTYPE_MSGBOX` | 弹消息框（**Windows CE 不可用**） |
| `ADSLOG_MSGTYPE_STRING` | 消息直接以字符串形式给出（默认） |

## 5. 使用注意 / 常见坑

- **必须边沿触发**（PDF 明确）；周期调用会刷屏 / 刷日志。
- 消息总长度 253 字节上限。
- MSGBOX 在 Windows CE 不可用，CE 平台只能用 LOG 路径。
- 生产环境推荐 LOG 而非 MSGBOX——MSGBOX 弹出会阻塞维护人员操作。（工程经验补充）

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_ADSLOGDINT.TcPOU`](../examples/P_Demo_ADSLOGDINT.TcPOU)（TwinCAT 3 原生 .TcPOU，可直接拖入 XAE 的 PLC POUs 文件夹）。
>
> 导入步骤：右键 PLC 项目下 POUs 文件夹 → Add → Existing Item → 选该文件 → OK

详见 example xml 文件。

## 7. 业务场景与实际价值

- **场景**：包装线 'feed 速率过高' 告警出现时弹一次消息框，并在系统日志里留一条带速率值的记录便于事后查；feed 一次超阈值就只弹一次而不是每周期刷屏。
- **价值**：替代手写 `WriteString` 到日志文件 + 启动外部弹框程序；一行调用搞定。
- **替代方案对比**：`ADSLOGLREAL` 嵌浮点；`ADSLOGSTR` 嵌字符串；纯整数告警量用本函数最简洁。

## 8. 参考资料

- **PDF**：[TwinCAT_3_PLC_Lib_Tc2_System_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_System_EN.pdf) §4.2.1
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tcplclib_tc2_system/31030539.html
- **相关 FB / FC**：`ADSLOGLREAL`（嵌浮点）、`ADSLOGSTR`（嵌字符串）
