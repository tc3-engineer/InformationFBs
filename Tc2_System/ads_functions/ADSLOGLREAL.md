# ADSLOGLREAL

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc2_System` |
| Library Version | `1.17.3` |
| Type | `FUNCTION` |
| Category | `ADS functions` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_System_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tcplclib_tc2_system/31032075.html |
| Verified | 2026-05-20 ✅ |
| InfoSys-checked | ✅ 2026-05-20 |
| Status | `verified` |
| Example | [`examples/P_Demo_ADSLOGLREAL.xml`](../examples/P_Demo_ADSLOGLREAL.xml) |

---

## 1. 功能简述

ADSLOGLREAL 是一个函数（FUNCTION）：和 `ADSLOGDINT` 行为相同，差别是嵌入文本的值类型从 `DINT` 改为 `LREAL`（浮点），格式占位符从 `%d` 改为 `%f`。返回 `DINT`：0 = 成功，其他为错误码。**必须边沿触发**。

## 2. 接口定义

### VAR_INPUT

```iecst
VAR_INPUT
    msgCtrlMask : DWORD;
    msgFmtStr   : T_MaxString;
    lrealArg    : LREAL;
END_VAR
```

| 名称 | 类型 | 默认值 | 说明 |
|---|---|---|---|
| `msgCtrlMask` | `DWORD` | - | 消息控制位掩码，含义同 `ADSLOGDINT`。 |
| `msgFmtStr` | `T_MaxString` | - | 格式化字符串。`%f` 占位符位置嵌入 `lrealArg` 值。消息长度上限 253 字节。 |
| `lrealArg` | `LREAL` | - | 要嵌入到消息文本中的浮点值。 |

### VAR_OUTPUT

```iecst
(* FUNCTION 返回 DINT：0 = 成功，其他 = 错误码 *)
FUNCTION ADSLOGLREAL : DINT
```

FUNCTION 返回值类型：`DINT`（详见 §4）。

### VAR_IN_OUT

无。

## 3. 行为说明

**调用语义**：FUNCTION 类型，同步执行，调用即出值。返回 0 = 成功，其他为错误码。

**`%f` 占位符**：默认输出精度由系统决定（PDF 示例显示 187.203045 输出后截到第 6 位小数）。

**必须边沿触发**：与 `ADSLOGDINT` 完全相同——PLC 周期执行，直接调用会刷屏；标准做法用 `R_TRIG` 把模拟量越限转上升沿。

**msgCtrlMask 组合**：与 `ADSLOGDINT` 完全一致；典型温度告警用 `ADSLOG_MSGTYPE_HINT OR ADSLOG_MSGTYPE_MSGBOX`，生产环境改 `MSGTYPE_LOG`。

**陷阱**：浮点输出位数固定不可控；如果需要控制小数位用 `REAL_TO_STRING` + 字符串拼接后调 `ADSLOGSTR`。Windows CE 上 MSGBOX 不可用。

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
- 浮点输出截断到 6 位小数（PDF 示例）；要精确控制格式改用 `ADSLOGSTR` + 字符串拼接。
- 消息长度 253 字节上限。
- Windows CE 不支持 MSGBOX。

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_ADSLOGLREAL.xml`](../examples/P_Demo_ADSLOGLREAL.xml)（PLCopenXML，可直接导入 TwinCAT 3 XAE）。
>
> 导入步骤：右键 PLC 项目 → Import PLCopenXML → 选该文件 → OK

详见 example xml 文件。

## 7. 业务场景与实际价值

- **场景**：水冷系统温度越限（如超过 80 °C）时弹一次消息框告知具体温度值，并写日志便于事后查趋势。
- **价值**：替代手写 `REAL_TO_STRING` + 字符串拼接 + 调日志接口，一行完成。
- **替代方案对比**：DINT 量用 `ADSLOGDINT`；自由格式或多变量嵌入用 `ADSLOGSTR` + 字符串拼接。

## 8. 参考资料

- **PDF**：[TwinCAT_3_PLC_Lib_Tc2_System_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_System_EN.pdf) §4.2.2
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tcplclib_tc2_system/31032075.html
- **相关 FB / FC**：`ADSLOGDINT`（嵌整数）、`ADSLOGSTR`（嵌字符串）
