# FB_SetLedColor_BAPI

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc2_System` |
| Library Version | `1.17.3` |
| Type | `FUNCTION_BLOCK` |
| Category | `General function blocks` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_System_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tcplclib_tc2_system/4566933899.html |
| Verified | 2026-05-20 ✅ |
| InfoSys-checked | ✅ 2026-05-20 |
| Status | `verified` |
| Example | [`examples/P_Demo_FB_SetLedColor_BAPI.xml`](../examples/P_Demo_FB_SetLedColor_BAPI.xml) |

---

## 1. 功能简述

FB_SetLedColor_BAPI 通过 BIOS API 切换 IPC / 嵌入式 PC 上的 USR LED 颜色。仅支持带 USR LED 且 BIOS 支持 BAPI 的 Beckhoff PC。可切换关、红、蓝、绿（取决于硬件支持）。

## 2. 接口定义

### VAR_INPUT

```iecst
VAR_INPUT
    sNetID         : T_AmsNetID;
    eNewColor      : E_UsrLED_Color;
    bExecute       : BOOL;
    tTimeout       : TIME;
END_VAR
```

| 名称 | 类型 | 默认值 | 说明 |
|---|---|---|---|
| `sNetID` | `T_AmsNetID` | - | 目标设备 AMS Net ID。本机用空串 `''` 或本机 Net ID。 |
| `eNewColor` | `E_UsrLED_Color` | - | 目标 LED 颜色枚举：`eUsrLED_Off` / `eUsrLED_Red` / `eUsrLED_Blue` / `eUsrLED_Green`。 |
| `bExecute` | `BOOL` | - | 上升沿触发一次切换；调用期间保持 TRUE，`bBusy = FALSE` 后再复位。 |
| `tTimeout` | `TIME` | - | 内部 ADS 通讯超时时长。 |

### VAR_OUTPUT

```iecst
VAR_OUTPUT
    bBusy    : BOOL;
    bError   : BOOL;
    nErrID   : UDINT;
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `bBusy` | `BOOL` | 切换命令执行中，TRUE 期间不接受新的上升沿。 |
| `bError` | `BOOL` | 上次执行检测到错误。 |
| `nErrID` | `UDINT` | ADS 错误码或命令特定错误码；下一次 `bExecute` 上升沿启动新命令时清 0。 |

### VAR_IN_OUT

无。

## 3. 行为说明

**调用约束**：必须周期调用让 ADS 状态机推进。`bExecute` 上升沿后 `bBusy := TRUE`，BAPI 调用收到 BIOS 应答时 `bBusy := FALSE` 同时根据结果设置 `bError`/`nErrID`。

**硬件前提**：CX / IPC 必须含 USR LED 且当前 BIOS 版本支持 BAPI。常见型号如 CX5xxx / C69xx 系列基本支持；纯第三方 IPC 不支持。运行时若 BIOS 不支持本 FB 会通过 `bError + nErrID` 返回错误而非崩溃。

**典型用法**：把设备健康状态映射到面板灯——例如 `eUsrLED_Green` = 正常运行，`eUsrLED_Red` = 故障，`eUsrLED_Blue` = 待机/维护模式；现场不用上 HMI 即可远距离知道控制器状态。

**陷阱**：必须每次 `bBusy` 落沿后再发新命令，否则连续上升沿会被丢弃；多任务同时操作同一灯需自行加锁（FB 本身不重入安全）。

## 4. 错误码 / 返回值

`nErrID` 是 ADS 错误码或命令特定错误码。0 表示成功；非 0 时 PDF 与 InfoSys 均未在本节列举完整对照表（⚠️ 待人工确认按『ADS Return Codes』参考）。常见 1861 = 调用超时，6 = ADS 端口未找到。

## 5. 使用注意 / 常见坑

- 目标 PC 必须具备 USR LED 且 BIOS 支持 BAPI；非 Beckhoff PC 或老 BIOS 直接报错。
- 对带多颗 USR LED（U1 / U2）的设备应改用 `FB_SetLedColorEx_BAPI`，本 FB 只能控制 USR。
- 把设备故障态投到红灯之后必须有逻辑把故障消除后切回绿灯，否则灯会停在红色误导维护人员。（工程经验补充）

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_FB_SetLedColor_BAPI.xml`](../examples/P_Demo_FB_SetLedColor_BAPI.xml)（PLCopenXML，可直接导入 TwinCAT 3 XAE）。
>
> 导入步骤：右键 PLC 项目 → Import PLCopenXML → 选该文件 → OK

详见 example xml 文件。

## 7. 业务场景与实际价值

- **场景**：CX5130 控制器在车间没有 HMI 的工位，把整机健康状态映射到 USR LED：绿 = 正常，红 = 故障，蓝 = 远程维护。
- **价值**：替代外接信号灯柱与数字输出布线，一行调用即得；故障时巡线员从过道扫一眼就知道哪台机出问题。
- **替代方案对比**：手写 ADS 命令到 BAPI 地址需查 BIOS 寄存器手册并组帧；本 FB 已封装协议，业务程序只关心枚举值。

## 8. 参考资料

- **PDF**：[TwinCAT_3_PLC_Lib_Tc2_System_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_System_EN.pdf) §3.1.5
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tcplclib_tc2_system/4566933899.html
- **相关 FB / FC**：`FB_SetLedColorEx_BAPI`（多 LED 版本：U1 / U2）
