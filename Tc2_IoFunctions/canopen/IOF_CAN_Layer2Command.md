# IOF_CAN_Layer2Command

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc2_IoFunctions` |
| Library Version | `1.5.3` |
| Type | `FUNCTION_BLOCK` |
| Category | `CANopen` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_IoFunctions_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tcplclib_tc2_iofunctions/59113227.html |
| Verified | 2026-05-21 ✅ |
| InfoSys-checked | ✅ 2026-05-21 |
| Status | `verified` |
| Example | [`examples/P_Demo_IOF_CAN_Layer2Command.TcPOU`](../examples/P_Demo_IOF_CAN_Layer2Command.TcPOU) |

---

## 1. 功能简述

向 CAN 主站发送一个 layer-2 命令（10 字节）。本 FB 是访问 CAN 层 2（原始 CAN 帧）的接口，绕过 CANopen 协议栈直接发原始 CAN 报文，用于诊断或与非 CANopen 设备通讯。PDF 明确："本功能 TwinCAT 3 目前不支持"（适配的硬件 HILSCHER CIF3xx 老 ISA 卡）。

## 2. 接口定义

### VAR_INPUT

```iecst
VAR_INPUT
    NETID : T_AmsNetId;
    DEVICEID : UDINT;
    BOXADDR : WORD;
    START : BOOL;
    TMOUT : TIME := DEFAULT_ADS_TIMEOUT;
END_VAR
```

| 名称 | 类型 | 默认值 | 说明 |
|---|---|---|---|
| `NETID` | `T_AmsNetId` | - | 目标 TwinCAT 计算机的 AMS Net ID；本机用空串 `''`，远端填对端 AMS Net ID（例如 `'5.84.32.27.1.1'`）。 |
| `DEVICEID` | `UDINT` | - | TwinCAT 配置时由系统自动分配的 I/O 设备 ID（不可由用户配置）。可在 System Manager 中查看，或通过 `IOF_GetDeviceIDByName` 由设备名查得。 |
| `BOXADDR` | `WORD` | - | CAN 设备地址（layer-2 命令的目标节点）。 |
| `START` | `BOOL` | - | 上升沿触发一次执行；调用期间保持高电平，完成后由用户决定何时回 FALSE 准备下次触发。 |
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

`START` 上升沿触发一次发送：`BUSY := TRUE`，FB 把 `SRCADDR` 指向的 `LEN` 字节 layer-2 命令通过 ADS 发到 CAN 主站。完成后 `BUSY := FALSE`；出错 `ERR := TRUE`、`ERRID` 给出 ADS 错误号。触发语义为上升沿一次性，调用者需要在 `BUSY` 落回后再决定下一次是否重新触发。注意：本 FB 的 VAR_INPUT 在 PDF VAR 区只列了 NETID / DEVICEID / BOXADDR / START / TMOUT，但描述列还提到 `LEN` (UDINT) 和 `SRCADDR` (PVOID)；这两个字段实际存在但被 PDF VAR 区漏列。⚠️ 调用时按 PDF 描述列填，名称按 PDF 写法。

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
- **TwinCAT 3 不支持本功能**（PDF 明确说明），HILSCHER CIF3xx 是早期 ISA 卡。
- PDF VAR_INPUT 漏列 `LEN` 和 `SRCADDR`；实际接口含这两参数，按 PDF 描述列填。（工程经验补充）
- layer-2 直发原始 CAN 报文需要懂 CAN 协议帧结构；用错可能干扰总线上其它节点。（工程经验补充）

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_IOF_CAN_Layer2Command.TcPOU`](../examples/P_Demo_IOF_CAN_Layer2Command.TcPOU)（TwinCAT 3 原生 .TcPOU，可直接拖入 XAE 的 PLC POUs 文件夹）
>
> 导入步骤：右键 PLC 项目下 POUs 文件夹 → Add → Existing Item → 选该文件 → OK

详见 example xml 文件。

## 7. 业务场景与实际价值

- **场景**：维护老线：HILSCHER CIF30 ISA 卡接 CANopen 网络，用本 FB 发原始 CAN 报文做诊断（如发 NMT 复位命令）。
- **价值**：绕过 CANopen 栈访问底层 CAN 帧。
- **替代方案对比**：
  - 在 TwinCAT 3 上跑：不支持
  - 用 Tc3_CANopen 库：标准做法
  - **本 FB**：仅维护早期工程

## 8. 参考资料

- **PDF**：[TwinCAT_3_PLC_Lib_Tc2_IoFunctions_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_IoFunctions_EN.pdf) §3.7.1
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tcplclib_tc2_iofunctions/59113227.html
- **相关 FB / FC**：`IOF_DeviceReset`
