# TC_Config

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc2_Utilities` |
| Library Version | `2.18.2` |
| Type | `FUNCTION_BLOCK` |
| Category | `Function blocks` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_Utilities_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tcplclib_tc2_utilities/35033099.html |
| Verified | 2026-05-11 ✅ |
| InfoSys-checked | ✅ 2026-05-11 |
| Status | `verified` |
| Example | [`examples/P_Demo_TC_Config.xml`](../examples/P_Demo_TC_Config.xml) |

---

## 1. 功能简述

TC_Config 通过 ADS 把目标 TwinCAT 系统切到 **Config 模式**——TwinCAT 配置模式（停止所有 PLC，进入设备配置态）。

用于：远程做硬件配置变更（ADS 修改 EtherCAT 配置）、维护重启前先入 Config。

## 2. 接口定义

### VAR_INPUT

```iecst
VAR_INPUT
    NETID : T_AmsNetId;
    SET : BOOL;
    TMOUT : TIME := DEFAULT_ADS_TIMEOUT;
END_VAR
```

| 名称 | 类型 | 默认值 | 说明 |
|---|---|---|---|
| `NETID` | `T_AmsNetId` | - | 参数 `NETID`（类型 `T_AmsNetId`）。⚠️ PDF 未详述含义，请按 §3 行为说明使用。 |
| `SET` | `BOOL` | - | 输入布尔标志：`SET`。具体语义见 §3 行为说明。 |
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

**调用**：`bExecute` 上升沿。FB 把 SystemService 切到 Config 模式，所有 PLC 任务停止。

**完成判定**：`bBusy → bDone`；切换成功后所有 PLC 程序被停止，业务侧需要在外部协调（HMI 提示用户）。


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
- **切到 Config 会停所有 PLC**——本 PLC 自身如果调用本 FB 会把自己也停掉，调用立即生效但后续代码就不再执行了。
- 应该用外部机器（工程师 PC）的 PLC 程序去切目标机器的 Config，而不是目标机器自切。（工程经验补充）

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_TC_Config.xml`](../examples/P_Demo_TC_Config.xml)（PLCopenXML，可直接导入 TwinCAT 3 XAE）。
>
> 导入步骤：右键 PLC 项目 → Import PLCopenXML → 选该文件 → OK

详见 example xml 文件。

## 7. 业务场景与实际价值

- **场景**：工程师 PC 远程把生产 PLC 切到 Config 做硬件维护。
- **价值**：脚本化运维。
- **替代方案对比**：
  - 手动 XAE 切 Config：单机方便。
  - **本 FB**：批量 / 远程可控。

## 8. 参考资料

- **PDF**：[TwinCAT_3_PLC_Lib_Tc2_Utilities_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_Utilities_EN.pdf) §3.82
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tcplclib_tc2_utilities/35033099.html
- **相关 FB**：`TC_Restart`, `TC_Stop`
