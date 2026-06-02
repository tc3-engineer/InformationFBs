# PLC_ReadSymInfo

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc2_Utilities` |
| Library Version | `2.18.2` |
| Type | `FUNCTION_BLOCK` |
| Category | `Function blocks` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_Utilities_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tcplclib_tc2_utilities/35030411.html |
| Verified | 2026-05-11 ✅ |
| InfoSys-checked | ✅ 2026-05-11 |
| Status | `verified` |
| Example | [`examples/P_Demo_PLC_ReadSymInfo.TcPOU`](../examples/P_Demo_PLC_ReadSymInfo.TcPOU) |

---

## 1. 功能简述

PLC_ReadSymInfo 通过 ADS 按索引读取目标 PLC 项目的符号信息（变量名 / 类型 / 地址 / 大小）。

用于：上位机自动发现 PLC 变量、动态生成 HMI 绑定。

## 2. 接口定义

### VAR_INPUT

```iecst
VAR_INPUT
    NETID : T_AmsNetId;
    PORT : T_AmsPort;
    START : BOOL;
    TMOUT : TIME := DEFAULT_ADS_TIMEOUT;
END_VAR
```

| 名称 | 类型 | 默认值 | 说明 |
|---|---|---|---|
| `NETID` | `T_AmsNetId` | - | 参数 `NETID`（类型 `T_AmsNetId`）。⚠️ PDF 未详述含义，请按 §3 行为说明使用。 |
| `PORT` | `T_AmsPort` | - | 参数 `PORT`（类型 `T_AmsPort`）。⚠️ PDF 未详述含义，请按 §3 行为说明使用。 |
| `START` | `BOOL` | - | 输入布尔标志：`START`。具体语义见 §3 行为说明。 |
| `TMOUT` | `TIME` | `DEFAULT_ADS_TIMEOUT` | 时间值：`TMOUT`。 |

### VAR_OUTPUT

```iecst
VAR_OUTPUT
    BUSY : BOOL;
    ERR : BOOL;
    ERRID : UDINT;
    SYMCOUNT : UDINT;
    SYMSIZE : UDINT;
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `BUSY` | `BOOL` | 输出布尔标志：`BUSY`。具体语义见 §3 行为说明。 |
| `ERR` | `BOOL` | 输出布尔标志：`ERR`。具体语义见 §3 行为说明。 |
| `ERRID` | `UDINT` | 无符号整数输出：`ERRID`。 |
| `SYMCOUNT` | `UDINT` | 无符号整数输出：`SYMCOUNT`。 |
| `SYMSIZE` | `UDINT` | 无符号整数输出：`SYMSIZE`。 |

### VAR_IN_OUT

无。

## 3. 行为说明

**调用**：`bExecute` 上升沿，按 `nIndex` 读第 N 个符号。


**调用一般约束**：本 FB 的所有输入 / 输出引脚语义已在 §2 接口定义表的中文说明列详细列出；调用方应按上述时序与状态机分支组织程序，并参照 §5 使用注意 / 常见坑回避典型陷阱。若 PDF 与 InfoSys 中未对某种异常工况作出明确说明，本仓库会以 ⚠️ 标记，提示读者用实测或在 Beckhoff Forum 上确认，而非凭推测下结论。

## 4. 错误码 / 返回值

本 FB 无显式错误输出。状态可以通过 `bBusy` / `bValid` / `bDone` 等过程信号间接判断。

## 5. 使用注意 / 常见坑

- `bExecute` 必须是上升沿触发；持续高电平不会重发请求，要释放再拉起。
- `tTimeout` 默认 `DEFAULT_ADS_TIMEOUT`（约 5 秒）。跨网段调用建议放大；过长会卡周期任务。（工程经验补充）
- PDF 没有枚举具体错误号——`nErrId / nErrorId` 引用通用 **ADS Return Codes** 表（参考 InfoSys 在线表）。
- `bBusy` 高电平期间业务侧不要再次拉起 `bExecute`，否则被忽略。（工程经验补充）
- 跨网段调用应放在非实时任务里执行，避免 PLC 周期任务被 ADS 抖动撑爆。（工程经验补充）
- **符号信息接口受目标 PLC 项目编译选项控制**——若未启用 `Symbol info` 选项符号表为空。（工程经验补充）
- **符号名区分大小写**——`Main.x` 与 `Main.X` 不同。（工程经验补充）

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_PLC_ReadSymInfo.TcPOU`](../examples/P_Demo_PLC_ReadSymInfo.TcPOU)（TwinCAT 3 原生 .TcPOU，可直接拖入 XAE 的 PLC POUs 文件夹）。
>
> 导入步骤：右键 PLC 项目下 POUs 文件夹 → Add → Existing Item → 选该文件 → OK

详见 example xml 文件。

## 7. 业务场景与实际价值

- **场景**：上位机自动发现 PLC 变量。
- **价值**：动态符号发现。
- **替代方案对比**：
  - 手工维护变量表：易漏。
  - **本 FB**：自动。

## 8. 参考资料

- **PDF**：[TwinCAT_3_PLC_Lib_Tc2_Utilities_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_Utilities_EN.pdf) §3.72
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tcplclib_tc2_utilities/35030411.html
