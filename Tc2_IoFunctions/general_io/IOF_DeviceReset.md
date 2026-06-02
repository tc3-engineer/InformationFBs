# IOF_DeviceReset

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc2_IoFunctions` |
| Library Version | `1.5.3` |
| Type | `FUNCTION_BLOCK` |
| Category | `General IO FBs` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_IoFunctions_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tcplclib_tc2_iofunctions/59085835.html |
| Verified | 2026-05-21 ✅ |
| InfoSys-checked | ✅ 2026-05-21 |
| Status | `verified` |
| Example | [`examples/P_Demo_IOF_DeviceReset.TcPOU`](../examples/P_Demo_IOF_DeviceReset.TcPOU) |

---

## 1. 功能简述

对指定 I/O 设备（例如现场总线卡 / 耦合器接口卡）执行在线复位，等价于在 TwinCAT System Manager 中右键 **I/O → Devices → Device xyz** 菜单选择 *Reset Device*。复位会让设备重新走完上电握手、清掉先前积累的错误状态。`RESET` 上升沿触发一次，FB 通过 `BUSY` / `ERR` / `ERRID` 反映异步结果。

## 2. 接口定义

### VAR_INPUT

```iecst
VAR_INPUT
    NETID : T_AmsNetId;
    DEVICEID : UDINT;
    RESET : BOOL;
    TMOUT : TIME := DEFAULT_ADS_TIMEOUT;
END_VAR
```

| 名称 | 类型 | 默认值 | 说明 |
|---|---|---|---|
| `NETID` | `T_AmsNetId` | - | 目标 TwinCAT 计算机的 AMS Net ID；本机用空串 `''`，远端填对端 AMS Net ID（例如 `'5.84.32.27.1.1'`）。 |
| `DEVICEID` | `UDINT` | - | TwinCAT 配置时由系统自动分配的 I/O 设备 ID（不可由用户配置）。可在 System Manager 中查看，或通过 `IOF_GetDeviceIDByName` 由设备名查得。 |
| `RESET` | `BOOL` | - | 上升沿触发一次设备复位命令；调用期间保持高电平，完成后由用户决定何时清零。 |
| `TMOUT` | `TIME` | `DEFAULT_ADS_TIMEOUT` | ADS 命令执行允许的最大时长。默认 `DEFAULT_ADS_TIMEOUT`（约 5 秒）。若现场总线设备应答慢需要适当放大。 |

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
| `BUSY` | `BOOL` | FB 激活到收到反馈期间保持 TRUE。`bBusy = TRUE` 时不接受新的上升沿触发。 |
| `ERR` | `BOOL` | 命令传输出错时在 `bBusy` 下降之后置 TRUE。下次成功上升沿触发后自动清零。 |
| `ERRID` | `UDINT` | 错误号；ADS 类错误参考 Beckhoff **ADS Return Codes** 在线表；FB 自定义错误号在 §4 列出（若 PDF 列出）。0 = 无错。 |

### VAR_IN_OUT

无。

## 3. 行为说明

`RESET` 上升沿触发一次复位命令：`BUSY := TRUE`，FB 把 reset 请求经 ADS 发到 `DEVICEID` 标识的 I/O 设备驱动。设备复位完成后 ADS 回复，`BUSY := FALSE`，若成功 `ERR := FALSE`、`ERRID := 0`；若失败 `ERR := TRUE`、`ERRID` 给出 ADS 错误号。命令超时由 `TMOUT` 控制（默认 5 秒），超时返回 `0x745` (ADSERR_CLIENT_SYNCTIMEOUT)。**触发语义**：必须上升沿；`RESET` 维持高电平不会重复发命令，需要再次复位时先回 FALSE 再回 TRUE。**典型用法**：现场总线偶发卡死 / 出现一长串硬件错误后调用一次让总线恢复；不要循环周期调用，复位本身会暂时打断 IO 通讯几十毫秒到几秒。

## 4. 错误码 / 返回值

本 FB 通过 `bError` / `ERR` + `nErrId` / `ERRID` 输出报告错误：

- `bError = FALSE` 且 `nErrId = 0`：调用成功。
- `bError = TRUE`：调用失败，错误号在 `nErrId`。

常见错误号（按 ADS Return Codes 表）：

| 错误号（十六进制） | 含义 |
|---|---|
| `0x06` | 目标端口未找到（ADSERR_DEVICE_NOTFOUND）—— 设备未启用或 DeviceId 错 |
| `0x07` | 目标机不在线（ADSERR_DEVICE_NOTREADY） |
| `0x745` | ADS 通讯超时（ADSERR_CLIENT_SYNCTIMEOUT）—— `TMOUT` 太短或现场总线响应慢 |
| 其他 | 见 Beckhoff **ADS Return Codes** 在线表，及现场总线主站特有的错误码（PDF 未列入本节） |

⚠️ PDF / InfoSys 未在本 FB 处列具体的现场总线错误号，需配合主站手册查询。

## 5. 使用注意 / 常见坑

- ADS 错误号需要查 Beckhoff 在线 **ADS Return Codes** 表理解，本 FB 自身不附带具体码表。
- 触发输入（如 `bExecute` / `START` / `RESET` 等）必须给上升沿一次性触发，不能持续给 TRUE。持续高电平时只有第一次进入会启动一次新请求，之后不会重新触发。（工程经验补充）
- 不要在 `BUSY = TRUE` 期间修改其它输入参数，结果未定义。等 `BUSY` 落回 FALSE 后再准备下一次的入参。（工程经验补充）
- 现场总线设备未上电 / 未通讯时 `ERRID` 会带 `0x06` (port not found) 或硬件接口特有错误号，不一定是 ADS 通讯本身问题。（工程经验补充）
- **复位会短暂中断 IO 通讯**：调用瞬间该设备的过程映像数据会失效，依赖其输入的逻辑必须能容忍 1-3 秒空窗；不要在运动中的关键回路里复位。（工程经验补充）
- **不要做自动循环复位**：若某设备频繁报错而触发循环复位，会掩盖真正的硬件故障并打乱诊断；应人工触发 + 报警。

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_IOF_DeviceReset.TcPOU`](../examples/P_Demo_IOF_DeviceReset.TcPOU)（TwinCAT 3 原生 .TcPOU，可直接拖入 XAE 的 PLC POUs 文件夹）
>
> 导入步骤：右键 PLC 项目下 POUs 文件夹 → Add → Existing Item → 选该文件 → OK

详见 example xml 文件。

## 7. 业务场景与实际价值

- **场景**：印刷机老线现场总线（例如 Profibus FC310x 卡）偶发通讯抖动 → 触发 `IOF_DeviceReset` 让该总线主站重新初始化，比断电重启 PLC 整机轻量。也用于固件升级后由 PLC 程序触发一次复位让新固件生效，或把运维工单上的「在线复位 IO 卡」做成 HMI 按钮。
- **价值**：把 System Manager 里需要手点的 *Reset Device* 操作做成 PLC 程序里可触发的一次调用，方便从 HMI 按钮触发，也方便诊断故障树自动执行。
- **替代方案对比**：
  - 手点 System Manager 菜单：能做但需要人值守 + 工程模式，不适合现场
  - 断电重启 PLC：能复位但代价大（所有 IO 同时停摆 + 程序重启）
  - 调 `ADSWRTCTL` 给驱动发 control code：底层做法，需要查 ADS 索引 group/offset，繁琐
  - **本 FB**：一行调用即得 System Manager 同等效果，是程序里复位 IO 设备的标准方式

## 8. 参考资料

- **PDF**：[TwinCAT_3_PLC_Lib_Tc2_IoFunctions_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_IoFunctions_EN.pdf) §3.1.1
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tcplclib_tc2_iofunctions/59085835.html
- **相关 FB / FC**：`IOF_GetDeviceCount`, `IOF_GetDeviceIDByName`, `IOF_GetDeviceType`
