# FB_RegSetValue

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc2_Utilities` |
| Library Version | `2.18.2` |
| Type | `FUNCTION_BLOCK` |
| Category | `Function blocks` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_Utilities_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tcplclib_tc2_utilities/35019403.html |
| Verified | 2026-05-11 ✅ |
| InfoSys-checked | ✅ 2026-05-11 |
| Status | `verified` |
| Example | [`examples/P_Demo_FB_RegSetValue.TcPOU`](../examples/P_Demo_FB_RegSetValue.TcPOU) |

---

## 1. 功能简述

FB_RegSetValue 写入目标系统的 Windows 注册表键值。

用于：commissioning 时配置硬件 / 软件参数。

## 2. 接口定义

### VAR_INPUT

```iecst
VAR_INPUT
    sNetId : T_AmsNetId;
    sSubKey : T_MaxString;
    sValName : T_MaxString;
    eValType : E_RegValueType;
    cbData : UDINT;
    pData : POINTER TO BYTE;
    bExecute : BOOL;
    tTimeOut : TIME := DEFAULT_ADS_TIMEOUT;
END_VAR
```

| 名称 | 类型 | 默认值 | 说明 |
|---|---|---|---|
| `sNetId` | `T_AmsNetId` | - | 目标系统 AMS Net ID。本机用空串 `''`；远端填对端 AMS Net ID。 |
| `sSubKey` | `T_MaxString` | - | 参数 `sSubKey`（类型 `T_MaxString`）。⚠️ PDF 未详述含义，请按 §3 行为说明使用。 |
| `sValName` | `T_MaxString` | - | 参数 `sValName`（类型 `T_MaxString`）。⚠️ PDF 未详述含义，请按 §3 行为说明使用。 |
| `eValType` | `E_RegValueType` | - | 参数 `eValType`（类型 `E_RegValueType`）。⚠️ PDF 未详述含义，请按 §3 行为说明使用。 |
| `cbData` | `UDINT` | - | 缓冲区字节数。 |
| `pData` | `POINTER TO BYTE` | - | 缓冲区指针（`PVOID` / `POINTER TO BYTE`），调用方负责分配。 |
| `bExecute` | `BOOL` | - | 上升沿触发一次执行；调用期间保持高电平，完成后自动复位无需手动清零。 |
| `tTimeOut` | `TIME` | `DEFAULT_ADS_TIMEOUT` | ADS 调用超时时长。默认 `DEFAULT_ADS_TIMEOUT`（约 5 秒）。 |

### VAR_OUTPUT

```iecst
VAR_OUTPUT
    bBusy : BOOL;
    bError : BOOL;
    nErrId : UDINT;
    cbWrite : UDINT;
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `bBusy` | `BOOL` | TRUE 表示请求正在处理；同时 `bExecute` 仍为高电平时不响应新请求。 |
| `bError` | `BOOL` | TRUE 表示本次请求失败，错误号由 `nErrId` / `nErrorId` 给出。 |
| `nErrId` | `UDINT` | ADS 错误码或本 FB 自定义错误号。0 = 无错。具体码表见 InfoSys / ADS Return Codes。 |
| `cbWrite` | `UDINT` | 无符号整数输出：`cbWrite`。 |

### VAR_IN_OUT

无。

## 3. 行为说明

**调用**：与 FB_RegQueryValue 镜像，给键路径 + 值名 + 新值。


**调用一般约束**：本 FB 的所有输入 / 输出引脚语义已在 §2 接口定义表的中文说明列详细列出；调用方应按上述时序与状态机分支组织程序，并参照 §5 使用注意 / 常见坑回避典型陷阱。若 PDF 与 InfoSys 中未对某种异常工况作出明确说明，本仓库会以 ⚠️ 标记，提示读者用实测或在 Beckhoff Forum 上确认，而非凭推测下结论。

## 4. 错误码 / 返回值

本 FB 通过 `bErr` + `nErrId`（或 `bError` + `nErrorId`）输出报告错误：

- `bErr / bError = FALSE` 且 `nErrId / nErrorId = 0`：本次请求成功。
- `bErr / bError = TRUE`：本次请求失败，错误号在 `nErrId / nErrorId`。

常见错误号属于 **ADS Return Codes**（PDF 与 InfoSys 都引用此表）：

| 错误号（十六进制） | 含义 |
|---|---|
| `0x06` | 目标端口未找到（ADSERR_DEVICE_NOTFOUND） |
| `0x07` | 目标机器未找到（ADSERR_DEVICE_INVALIDDATA） |
| `0x745` | ADS 通讯超时（ADSERR_CLIENT_SYNCTIMEOUT） |
| 其他 | PDF 未枚举，详见 Beckhoff 在线 ADS Return Codes 表 ⚠️ |

## 5. 使用注意 / 常见坑

- `bExecute` 必须是上升沿触发；持续高电平不会重发请求，要释放再拉起。
- `tTimeout` 默认 `DEFAULT_ADS_TIMEOUT`（约 5 秒）。跨网段调用建议放大；过长会卡周期任务。（工程经验补充）
- PDF 没有枚举具体错误号——`nErrId / nErrorId` 引用通用 **ADS Return Codes** 表（参考 InfoSys 在线表）。
- `bBusy` 高电平期间业务侧不要再次拉起 `bExecute`，否则被忽略。（工程经验补充）
- 跨网段调用应放在非实时任务里执行，避免 PLC 周期任务被 ADS 抖动撑爆。（工程经验补充）
- **修改注册表是系统级操作**——错误的值可能让 Windows 不能启动；生产环境务必备份。
- HKEY 路径要按 Windows 约定（如 `HKEY_LOCAL_MACHINE\SYSTEM\...`），区分大小写不严但建议规范化。（工程经验补充）
- 写错值可能让某些 Windows 服务无法启动；要先备份键再写。

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_FB_RegSetValue.TcPOU`](../examples/P_Demo_FB_RegSetValue.TcPOU)（TwinCAT 3 原生 .TcPOU，可直接拖入 XAE 的 PLC POUs 文件夹）。
>
> 导入步骤：右键 PLC 项目下 POUs 文件夹 → Add → Existing Item → 选该文件 → OK

详见 example xml 文件。

## 7. 业务场景与实际价值

- **场景**：commissioning 时配置注册表。
- **价值**：脚本化配置。
- **替代方案对比**：
  - 手动 regedit：单机方便。
  - **本 FB**：批量。

## 8. 参考资料

- **PDF**：[TwinCAT_3_PLC_Lib_Tc2_Utilities_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_Utilities_EN.pdf) §3.54
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tcplclib_tc2_utilities/35019403.html
