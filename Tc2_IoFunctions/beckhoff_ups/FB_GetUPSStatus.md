# FB_GetUPSStatus

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc2_IoFunctions` |
| Library Version | `1.5.3` |
| Type | `FUNCTION_BLOCK` |
| Category | `Beckhoff UPS (configured with Windows UPS Service` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_IoFunctions_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tcplclib_tc2_iofunctions/59184523.html |
| Verified | 2026-05-21 ✅ |
| InfoSys-checked | ✅ 2026-05-21 |
| Status | `verified` |
| Example | [`examples/P_Demo_FB_GetUPSStatus.TcPOU`](../examples/P_Demo_FB_GetUPSStatus.TcPOU) |

---

## 1. 功能简述

读取 Beckhoff UPS（不间断电源）状态，从 PLC 程序就能拿到当前电源是否在用 UPS、电池剩余电量、是否处于断电倒计时等。本 FB 是 **电平触发**（不是边沿）：`bEnable = TRUE` 时周期读取（约每 4.5 秒一次），`bValid` 表示最新读到的数据是否有效。前提：已安装 Beckhoff UPS 软件组件（Windows 7+ 在 *Start → Programs → Beckhoff → UPS Software Components*）。

## 2. 接口定义

### VAR_INPUT

```iecst
VAR_INPUT
    sNetId : T_AmsNetId;
    nPort : T_AmsPort;
    bEnable : BOOL;
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `sNetId` | `T_AmsNetId` | 本机用空串；远端填对端 AMS Net ID。 |
| `nPort` | `T_AmsPort` | ADS 端口号；目前固定 0（= Windows UPS Service / Windows Battery Driver）。 |
| `bEnable` | `BOOL` | TRUE 电平使能周期读 UPS 状态；FALSE 停止。 |

### VAR_OUTPUT

```iecst
VAR_OUTPUT
    bValid : BOOL;
    bError : BOOL;
    nErrId : UDINT;
    stStatus : ST_UPSStatus;
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `bValid` | `BOOL` | TRUE = 最新 `stStatus` 数据有效；FALSE = 数据未就绪 / 读取出错。 |
| `bError` | `BOOL` | TRUE = 上次读取失败。 |
| `nErrId` | `UDINT` | ADS 错误号。 |
| `stStatus` | `ST_UPSStatus` | UPS 状态结构（电池电量 / 在 AC 还是 battery / 是否倒计时关机等），详见 `ST_UPSStatus`。 |

### VAR_IN_OUT

无。

## 3. 行为说明

`bEnable = TRUE` 时 FB 每隔约 4.5 秒经 ADS 读一次 UPS 状态（间隔由 FB 内部控制，无需外部触发），结果填入 `stStatus`。`bValid` 反映最近一次读取是否成功：TRUE 表示 `stStatus` 数据可信；FALSE 表示当前读取在进行 / 出错。出错时 `bError := TRUE`、`nErrId` 给出 ADS 错误号；错误原因消失后下次循环会自动复位。本 FB 是 **电平**（level-triggered）模式：`bEnable = FALSE` 时停止读取，`bValid` 也会落到 FALSE。不同于其它 ADS FB 的"上升沿触发"，本 FB 一旦 enable 就持续工作直到 disable。`nPort = 0` 对应 Windows UPS Service / Windows Battery Driver；其它端口号保留为未来扩展。

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

- **电平触发**，不是上升沿——业务侧直接给 `bEnable := TRUE` 即可，不需要发脉冲。
- 约 4.5 秒读一次，**不要期待秒级实时**。若需要立刻得到 UPS 状态，断电后 0-4.5 秒会出现陈旧数据。（工程经验补充）
- 需要事先安装 Beckhoff UPS 软件组件且正确配置；驱动未装时 ADS 调用会返回端口错误（`0x6`）。（工程经验补充）
- 远端读取（`sNetId` 非空）目前是预留能力——大部分 UPS 工作场景都是本机读本机 UPS（`sNetId := ""`）。（工程经验补充）

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_FB_GetUPSStatus.TcPOU`](../examples/P_Demo_FB_GetUPSStatus.TcPOU)（TwinCAT 3 原生 .TcPOU，可直接拖入 XAE 的 PLC POUs 文件夹）
>
> 导入步骤：右键 PLC 项目下 POUs 文件夹 → Add → Existing Item → 选该文件 → OK

详见 example xml 文件。

## 7. 业务场景与实际价值

- **场景**：CX5020 工控机配 Beckhoff CB3011 UPS：PLC 程序周期读 UPS 状态，断电时立即把关键 retain 数据写盘并发报警。
- **价值**：掉电不丢数据：UPS 给约 2 秒延迟，本 FB 让 PLC 程序在掉电瞬间就知道断电了，并执行保护逻辑。
- **替代方案对比**：
  - 不读 UPS 状态：断电瞬间 PLC 不知道，retain 不写盘
  - 用单独的 IO 给 UPS 报警继电器接 PLC DI：能做但要硬件接线
  - **本 FB**：纯软件方式读 UPS

## 8. 参考资料

- **PDF**：[TwinCAT_3_PLC_Lib_Tc2_IoFunctions_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_IoFunctions_EN.pdf) §3.5.1
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tcplclib_tc2_iofunctions/59184523.html
- **相关 FB / FC**：`FB_S_UPS_CB3011 (Tc2_SUPS)`, `FB_S_UPS_BAPI (Tc2_SUPS)`
