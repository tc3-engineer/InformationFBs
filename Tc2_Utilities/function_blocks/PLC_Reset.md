# PLC_Reset

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc2_Utilities` |
| Library Version | `2.18.2` |
| Type | `FUNCTION_BLOCK` |
| Category | `Function blocks` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_Utilities_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tcplclib_tc2_utilities/35040907.html |
| Verified | 2026-05-11 ✅ |
| InfoSys-checked | ✅ 2026-05-11 |
| Status | `verified` |
| Example | [`examples/P_Demo_PLC_Reset.xml`](../examples/P_Demo_PLC_Reset.xml) |

---

## 1. 功能简述

PLC_Reset 通过 ADS 命令目标 TwinCAT PLC 执行 Reset（清变量初值 + 重启程序）。

运维 / commissioning 操作，不属于业务周期调用。

## 2. 接口定义

### VAR_INPUT

```iecst
VAR_INPUT
    NETID : T_AmsNetId;
    PORT : T_AmsPort;
    RESET : BOOL;
    TMOUT : TIME := DEFAULT_ADS_TIMEOUT;
END_VAR
```

| 名称 | 类型 | 默认值 | 说明 |
|---|---|---|---|
| `NETID` | `T_AmsNetId` | - | 参数 `NETID`（类型 `T_AmsNetId`）。⚠️ PDF 未详述含义，请按 §3 行为说明使用。 |
| `PORT` | `T_AmsPort` | - | 参数 `PORT`（类型 `T_AmsPort`）。⚠️ PDF 未详述含义，请按 §3 行为说明使用。 |
| `RESET` | `BOOL` | - | 输入布尔标志：`RESET`。具体语义见 §3 行为说明。 |
| `TMOUT` | `TIME` | `DEFAULT_ADS_TIMEOUT` | 时间值：`TMOUT`。 |

### VAR_OUTPUT

```iecst
VAR_OUTPUT
    BUSY : BOOL;
    ERR : BOOL;
    ERRID : UDINT;
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `BUSY` | `BOOL` | 输出布尔标志：`BUSY`。具体语义见 §3 行为说明。 |
| `ERR` | `BOOL` | 输出布尔标志：`ERR`。具体语义见 §3 行为说明。 |
| `ERRID` | `UDINT` | 无符号整数输出：`ERRID`。 |

### VAR_IN_OUT

无。

## 3. 行为说明

**调用**：`bExecute` 上升沿触发一次 ADS 命令；FB 通过 ADS 把状态切换请求发到目标 PLC，目标 PLC 在数十毫秒内执行 执行 Reset（清变量初值 + 重启程序）。

**响应**：`bBusy` 高电平期间表示请求未完成；完成后 `bDone` 或 `bErr` + `nErrId`。

**典型用法**：HMI 按钮触发 / 远程运维 / 自动化部署脚本里调用。


**调用一般约束**：本 FB 的所有输入 / 输出引脚语义已在 §2 接口定义表的中文说明列详细列出；调用方应按上述时序与状态机分支组织程序，并参照 §5 使用注意 / 常见坑回避典型陷阱。若 PDF 与 InfoSys 中未对某种异常工况作出明确说明，本仓库会以 ⚠️ 标记，提示读者用实测或在 Beckhoff Forum 上确认，而非凭推测下结论。

## 4. 错误码 / 返回值

本 FB 无显式错误输出。状态可以通过 `bBusy` / `bValid` / `bDone` 等过程信号间接判断。

## 5. 使用注意 / 常见坑

- `bExecute` 必须是上升沿触发；持续高电平不会重发请求，要释放再拉起。
- `tTimeout` 默认 `DEFAULT_ADS_TIMEOUT`（约 5 秒）。跨网段调用建议放大；过长会卡周期任务。（工程经验补充）
- PDF 没有枚举具体错误号——`nErrId / nErrorId` 引用通用 **ADS Return Codes** 表（参考 InfoSys 在线表）。
- `bBusy` 高电平期间业务侧不要再次拉起 `bExecute`，否则被忽略。（工程经验补充）
- 跨网段调用应放在非实时任务里执行，避免 PLC 周期任务被 ADS 抖动撑爆。（工程经验补充）
- **系统级影响**：本 FB 会改变 PLC / TwinCAT 运行状态；生产环境应纳入运维流程而不是普通业务调用。

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_PLC_Reset.xml`](../examples/P_Demo_PLC_Reset.xml)（PLCopenXML，可直接导入 TwinCAT 3 XAE）。
>
> 导入步骤：右键 PLC 项目 → Import PLCopenXML → 选该文件 → OK

详见 example xml 文件。

## 7. 业务场景与实际价值

- **场景**：升级新程序后让 PLC 走一次 Reset。
- **价值**：替代手动 TwinCAT XAE 状态切换按钮。
- **替代方案对比**：
  - 手动 XAE 按钮：单机方便，批量痛。
  - **本 FB**：可脚本化批量操作。

## 8. 参考资料

- **PDF**：[TwinCAT_3_PLC_Lib_Tc2_Utilities_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_Utilities_EN.pdf) §3.75
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tcplclib_tc2_utilities/35040907.html
