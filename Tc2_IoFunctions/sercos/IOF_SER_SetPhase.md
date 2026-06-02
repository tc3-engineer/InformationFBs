# IOF_SER_SetPhase

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc2_IoFunctions` |
| Library Version | `1.5.3` |
| Type | `FUNCTION_BLOCK` |
| Category | `SERCOS` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_IoFunctions_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tcplclib_tc2_iofunctions/59120779.html |
| Verified | 2026-05-21 ✅ |
| InfoSys-checked | ✅ 2026-05-21 |
| Status | `verified` |
| Example | [`examples/P_Demo_IOF_SER_SetPhase.TcPOU`](../examples/P_Demo_IOF_SER_SetPhase.TcPOU) |

---

## 1. 功能简述

设置 SERCOS 环到指定 phase。常用于把环手动降到 phase 2 做参数访问，或升到 phase 4 进入运行。

## 2. 接口定义

### VAR_INPUT

```iecst
VAR_INPUT
    NETID : T_AmsNetId;
    DEVICEID : UDINT;
    PHASE : BYTE;
    SET : BOOL;
    TMOUT : TIME := DEFAULT_ADS_TIMEOUT;
END_VAR
```

| 名称 | 类型 | 默认值 | 说明 |
|---|---|---|---|
| `NETID` | `T_AmsNetId` | - | 本机用空串。 |
| `DEVICEID` | `UDINT` | - | SERCOS 主站 Device Id。 |
| `PHASE` | `BYTE` | - | 目标 phase 值（0..4）。PDF VAR 表写 BOOL 是排版错，实际是 BYTE。 |
| `SET` | `BOOL` | - | 上升沿触发一次 phase 切换。 |
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

`SET` 上升沿触发一次 phase 切换：`BUSY := TRUE`，FB 经 ADS 让 SERCOS 主站启动 phase 切换流程。`PHASE` 输入是目标 phase（0..4）。完成后 `BUSY := FALSE`；可用 `IOF_SER_GetPhase` 验证。注意：phase 切换涉及全总线握手，切换时间可达数秒，`TMOUT` 建议给 ≥ 10 秒。从高 phase 切回低 phase（例如 4 → 2）会**停止所有 motion**，所以运行中切换前必须先把 drive 停下。PDF VAR 表把 `PHASE` 标为 BOOL，但描述列说"通讯 phase 值"——VAR 区拼写错误，实际是 BYTE。

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

- SERCOS 是早期 motion 总线（SERCANS SCS-P ISA / PCI / Beckhoff FC750x PCI）；现代工程多用 EtherCAT + EL72xx。本系列 FB 用于维护老线。
- SERCOS 通讯有 5 个 phase（0..4），通讯参数访问要求处于特定 phase（通常 phase 2）。（工程经验补充）
- ADS 错误号见 Beckhoff ADS Return Codes 在线表；SERCOS 自定义错误号见对应 IDN 的应答字段。（工程经验补充）
- drive 参数（S / P 参数）通过 IDN（Identification Number）寻址：S = 0..32767，P = 32768..65535。（工程经验补充）
- **从 phase 4 切回低 phase 会停所有 motion**——必须先把 drive 停下，否则可能机械损坏。
- phase 切换耗时数秒，`TMOUT` 给 ≥ 10 秒。（工程经验补充）
- PDF VAR 区 `PHASE : BOOL` 是排版错（应为 BYTE）——以描述列与正常使用为准。（工程经验补充）

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_IOF_SER_SetPhase.TcPOU`](../examples/P_Demo_IOF_SER_SetPhase.TcPOU)（TwinCAT 3 原生 .TcPOU，可直接拖入 XAE 的 PLC POUs 文件夹）
>
> 导入步骤：右键 PLC 项目下 POUs 文件夹 → Add → Existing Item → 选该文件 → OK

详见 example xml 文件。

## 7. 业务场景与实际价值

- **场景**：SERCOS 调试：先用本 FB 把环切到 phase 2 改 drive 参数 → 再切回 phase 4 进入运行。
- **价值**：让 phase 切换可被 PLC 程序控制，封装到工程师"调试模式"流程里。
- **替代方案对比**：
  - SERCANS 工具：要带工具
  - 重启 PLC 让 phase 自动升：代价大
  - **本 FB**：精细控制

## 8. 参考资料

- **PDF**：[TwinCAT_3_PLC_Lib_Tc2_IoFunctions_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_IoFunctions_EN.pdf) §3.12.4
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tcplclib_tc2_iofunctions/59120779.html
- **相关 FB / FC**：`IOF_SER_GetPhase`, `IOF_SER_IDN_Read`, `IOF_SER_IDN_Write`
