# FB_WritePersistentData

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc2_Utilities` |
| Library Version | `2.18.2` |
| Type | `FUNCTION_BLOCK` |
| Category | `Function blocks` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_Utilities_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tcplclib_tc2_utilities/35029387.html |
| Verified | 2026-05-11 ✅ |
| InfoSys-checked | ✅ 2026-05-11 |
| Status | `verified` |
| Example | [`examples/P_Demo_FB_WritePersistentData.xml`](../examples/P_Demo_FB_WritePersistentData.xml) |

---

## 1. 功能简述

FB_WritePersistentData 通过 ADS 把指定 PLC 项目里的 `PERSISTENT` 变量手动写到磁盘（默认 TwinCAT 已自动保存，本 FB 用于强制立即保存）。

用于：关键操作后强制持久化（如 commissioning 配置变更）。

## 2. 接口定义

### VAR_INPUT

```iecst
VAR_INPUT
    NETID : T_AmsNetId;
    PORT : UINT;
    START : BOOL;
    TMOUT : TIME := DEFAULT_ADS_TIMEOUT;
    MODE : E_PersistentMode;
END_VAR
```

| 名称 | 类型 | 默认值 | 说明 |
|---|---|---|---|
| `NETID` | `T_AmsNetId` | - | 参数 `NETID`（类型 `T_AmsNetId`）。⚠️ PDF 未详述含义，请按 §3 行为说明使用。 |
| `PORT` | `UINT` | - | 无符号整数输入：`PORT`。 |
| `START` | `BOOL` | - | 输入布尔标志：`START`。具体语义见 §3 行为说明。 |
| `TMOUT` | `TIME` | `DEFAULT_ADS_TIMEOUT` | 时间值：`TMOUT`。 |
| `MODE` | `E_PersistentMode` | - | 参数 `MODE`（类型 `E_PersistentMode`）。⚠️ PDF 未详述含义，请按 §3 行为说明使用。 |

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

**调用**：`bExecute` 上升沿，向目标 PLC 端口发『保存 persistent』命令。

**响应**：本地几十 ms；persistent 数据量大可能数秒。


**调用一般约束**：本 FB 的所有输入 / 输出引脚语义已在 §2 接口定义表的中文说明列详细列出；调用方应按上述时序与状态机分支组织程序，并参照 §5 使用注意 / 常见坑回避典型陷阱。若 PDF 与 InfoSys 中未对某种异常工况作出明确说明，本仓库会以 ⚠️ 标记，提示读者用实测或在 Beckhoff Forum 上确认，而非凭推测下结论。

## 4. 错误码 / 返回值

本 FB 无显式错误输出。状态可以通过 `bBusy` / `bValid` / `bDone` 等过程信号间接判断。

## 5. 使用注意 / 常见坑

- `bExecute` 必须是上升沿触发；持续高电平不会重发请求，要释放再拉起。
- `tTimeout` 默认 `DEFAULT_ADS_TIMEOUT`（约 5 秒）。跨网段调用建议放大；过长会卡周期任务。（工程经验补充）
- PDF 没有枚举具体错误号——`nErrId / nErrorId` 引用通用 **ADS Return Codes** 表（参考 InfoSys 在线表）。
- `bBusy` 高电平期间业务侧不要再次拉起 `bExecute`，否则被忽略。（工程经验补充）
- 跨网段调用应放在非实时任务里执行，避免 PLC 周期任务被 ADS 抖动撑爆。（工程经验补充）
- **文件操作受 SystemService 权限限制**——CX 设备的 `C:\TwinCAT\Boot` 等敏感目录可能不可写。（工程经验补充）
- 绝对路径建议带盘符；相对路径以 `ePath` 枚举为基准（`PATH_GENERIC` = TwinCAT 安装目录）。（工程经验补充）
- 文件 I/O 是异步操作，触发后在 `bBusy → bDone` 之间业务侧不能假设文件已可见。
- **TwinCAT 默认在 shutdown 时自动保存 persistent**——日常无需主动调用。频繁调用会写磁盘磨损 SD 卡。
- `PERSISTENT` 与 `RETAIN` 不同：persistent 写文件，retain 在 PLC 内存断电保护区。本 FB 只管 persistent。（工程经验补充）

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_FB_WritePersistentData.xml`](../examples/P_Demo_FB_WritePersistentData.xml)（PLCopenXML，可直接导入 TwinCAT 3 XAE）。
>
> 导入步骤：右键 PLC 项目 → Import PLCopenXML → 选该文件 → OK

详见 example xml 文件。

## 7. 业务场景与实际价值

- **场景**：关键配置变更后强制持久化。
- **价值**：替代等待自动保存。
- **替代方案对比**：
  - 等 TwinCAT 自动保存：可能丢配置变更（突然掉电时）。
  - **本 FB**：业务时机可控。

## 8. 参考资料

- **PDF**：[TwinCAT_3_PLC_Lib_Tc2_Utilities_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_Utilities_EN.pdf) §3.62
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tcplclib_tc2_utilities/35029387.html
- **相关 FB**：`WritePersistentData`
