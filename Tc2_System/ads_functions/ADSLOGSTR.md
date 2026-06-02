# ADSLOGSTR

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc2_System` |
| Library Version | `1.17.3` |
| Type | `FUNCTION` |
| Category | `ADS functions` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_System_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tcplclib_tc2_system/31033611.html |
| Verified | 2026-05-20 ✅ |
| InfoSys-checked | ✅ 2026-05-20 |
| Status | `verified` |
| Example | [`examples/P_Demo_ADSLOGSTR.TcPOU`](../examples/P_Demo_ADSLOGSTR.TcPOU) |

---

## 1. 功能简述

ADSLOGSTR 是一个函数（FUNCTION）：和 `ADSLOGDINT` 行为相同，差别是嵌入文本的值类型为 `STRING`（`T_MaxString`），占位符 `%s`。返回 `DINT`：0 = 成功，其他为错误码。**必须边沿触发**。

## 2. 接口定义

### VAR_INPUT

```iecst
VAR_INPUT
    msgCtrlMask  : DWORD;
    msgFmtStr    : T_MaxString;
    strArg       : T_MaxString;
END_VAR
```

| 名称 | 类型 | 默认值 | 说明 |
|---|---|---|---|
| `msgCtrlMask` | `DWORD` | - | 消息控制位掩码，含义同 `ADSLOGDINT`。 |
| `msgFmtStr` | `T_MaxString` | - | 格式化字符串。`%s` 占位符位置嵌入 `strArg`。消息长度上限 253 字节。 |
| `strArg` | `T_MaxString` | - | 要嵌入到消息文本中的字符串值。 |

### VAR_OUTPUT

```iecst
(* FUNCTION 返回 DINT：0 = 成功，其他 = 错误码 *)
FUNCTION ADSLOGSTR : DINT
```

FUNCTION 返回值类型：`DINT`（详见 §4）。

### VAR_IN_OUT

无。

## 3. 行为说明

**调用语义**：FUNCTION 类型，同步执行。返回 0 = 成功，其他为错误码。

**`%s` 占位符**：第一个 `%s` 替换为 `strArg`；多 `%s` 时只有第一个被替换。

**必须边沿触发**：与 `ADSLOGDINT` 完全相同。PDF 示例用 `SFCError` 触发 `R_TRIG`，把当前 `SFCErrorStep` 字符串嵌入消息。

**典型用法**：(1) SFC 卡步告警把 `SFCErrorStep` 名称写入日志；(2) 流程异常时把当前状态机状态名嵌入消息；(3) 用户操作日志带上操作员名。

**陷阱**：`%s` 嵌入后总长度仍受 253 字节限制；如果格式串本身较长 + strArg 较长会被截断。

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

- **必须边沿触发**（PDF 明确）。
- 总长度 253 字节上限——格式串 + 嵌入字符串合计不能超。
- Windows CE 不支持 MSGBOX。
- 想嵌入多个字段时不能用多个 `%s`，要在 PLC 端先用 `CONCAT` 拼好再传 strArg。（工程经验补充）

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_ADSLOGSTR.TcPOU`](../examples/P_Demo_ADSLOGSTR.TcPOU)（TwinCAT 3 原生 .TcPOU，可直接拖入 XAE 的 PLC POUs 文件夹）。
>
> 导入步骤：右键 PLC 项目下 POUs 文件夹 → Add → Existing Item → 选该文件 → OK

详见 example xml 文件。

## 7. 业务场景与实际价值

- **场景**：SFC 工程出错时把当前阻塞步名称（如 `'Step_LoadMaterial'`）嵌入告警消息推到 Windows 事件日志，运维一眼定位故障工位。
- **价值**：替代手写 `CONCAT('卡步:', strSFCErrorStep)` 再调日志接口，一行完成。
- **替代方案对比**：DINT 用 `ADSLOGDINT`；浮点用 `ADSLOGLREAL`；字符串或拼好的复合消息用本函数。

## 8. 参考资料

- **PDF**：[TwinCAT_3_PLC_Lib_Tc2_System_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_System_EN.pdf) §4.2.3
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tcplclib_tc2_system/31033611.html
- **相关 FB / FC**：`ADSLOGDINT`、`ADSLOGLREAL`
