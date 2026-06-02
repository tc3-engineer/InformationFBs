# FB_SetLedColorEx_BAPI

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc2_System` |
| Library Version | `1.17.3` |
| Type | `FUNCTION_BLOCK` |
| Category | `General function blocks` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_System_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tcplclib_tc2_system/14675051403.html |
| Verified | 2026-05-20 ✅ |
| InfoSys-checked | ✅ 2026-05-20 |
| Status | `verified` |
| Example | [`examples/P_Demo_FB_SetLedColorEx_BAPI.TcPOU`](../examples/P_Demo_FB_SetLedColorEx_BAPI.TcPOU) |

---

## 1. 功能简述

FB_SetLedColorEx_BAPI 通过 BIOS API 切换 IPC / 嵌入式 PC 上**任一**用户 LED（USR / U1 / U2）的颜色。是 `FB_SetLedColor_BAPI` 的扩展版本：新增 `nLedID` 选 LED。`nLedID = 0` 选 USR（单灯设备），1 选 U1，2 选 U2。

## 2. 接口定义

### VAR_INPUT

```iecst
VAR_INPUT
    sNetID         : T_AmsNetID;
    nLedID         : USINT
    eNewColor      : E_UsrLED_Color;
    bExecute       : BOOL;
    tTimeout       : TIME;
END_VAR
```

| 名称 | 类型 | 默认值 | 说明 |
|---|---|---|---|
| `sNetID` | `T_AmsNetID` | - | 目标设备 AMS Net ID。本机用空串 `''` 或本机 Net ID。 |
| `nLedID` | `USINT` | - | 用户 LED 选择。单 LED 设备：`nLedID = 0` 选 USR LED（默认 0）。多 LED 设备：1 = U1 LED，2 = U2 LED。 |
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

**调用约束**：与 `FB_SetLedColor_BAPI` 相同——周期调用，`bExecute` 上升沿启动一次 BAPI 写。

**`nLedID` 选灯**：CX52xx 等带多颗用户 LED 的设备上，可单独切换 U1 和 U2。`nLedID = 0` 是兼容路径（与旧 `FB_SetLedColor_BAPI` 等价，操作 USR LED）。具体硬件支持哪几颗 LED 看设备 BIOS 文档；不存在的 LED ID 会通过 `bError + nErrID` 报错。

**典型用法**：U1 显示 PLC 运行状态（绿/红），U2 显示通讯链路状态（绿 = 连上 PLC，蓝 = 等待对端）；现场维护扫一眼就知道是 PLC 故障还是网络故障。

**陷阱**：与 `FB_SetLedColor_BAPI` 相同——必须等 `bBusy` 落沿；本 FB 不能并发同灯。

## 4. 错误码 / 返回值

`nErrID` 是 ADS 错误码或命令特定错误码。0 = 成功；非 0 时参考『ADS Return Codes』⚠️ 待人工确认。常见 1861 = 调用超时，6 = ADS 端口未找到，硬件不支持该 nLedID 会返回 BAPI 特定错误码。

## 5. 使用注意 / 常见坑

- 本 FB 自 Tc2_System v3.6.1 起可用，旧版本只有 `FB_SetLedColor_BAPI`。
- 目标 PC 必须支持 BAPI 且硬件实际带对应 LED；不存在的 `nLedID` 会报错。
- 把 U1 / U2 各做不同含义建议在文档里画一张对照表贴现场柜门内侧避免维护人员误解。（工程经验补充）

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_FB_SetLedColorEx_BAPI.TcPOU`](../examples/P_Demo_FB_SetLedColorEx_BAPI.TcPOU)（TwinCAT 3 原生 .TcPOU，可直接拖入 XAE 的 PLC POUs 文件夹）。
>
> 导入步骤：右键 PLC 项目下 POUs 文件夹 → Add → Existing Item → 选该文件 → OK

详见 example xml 文件。

## 7. 业务场景与实际价值

- **场景**：CX5230 双 LED 控制器：U1 显示 PLC 状态（绿 = 运行 / 红 = 故障），U2 显示与远程 SCADA 的链路状态（绿 = 已连 / 蓝 = 等待）。
- **价值**：用一个 FB 控制两颗灯，业务侧只关心枚举语义；不用为两颗灯各写一份 ADS 命令。
- **替代方案对比**：旧 `FB_SetLedColor_BAPI` 只能控 USR；想分别控 U1 / U2 必须用本 FB 并通过 `nLedID` 选择。

## 8. 参考资料

- **PDF**：[TwinCAT_3_PLC_Lib_Tc2_System_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_System_EN.pdf) §3.1.6
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tcplclib_tc2_system/14675051403.html
- **相关 FB / FC**：`FB_SetLedColor_BAPI`（单 USR LED 旧版本）
