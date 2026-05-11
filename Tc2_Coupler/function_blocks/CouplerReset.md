# CouplerReset

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc2_Coupler` |
| Library Version | `1.1.1` |
| Type | `FUNCTION_BLOCK` |
| Category | `Function blocks` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_Coupler_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tcplclib_tc2_coupler/42592779.html |
| Verified | 2026-05-11 ✅ |
| InfoSys-checked | ✅ 2026-05-11 |
| Status | `verified` |
| Example | [`examples/P_Demo_CouplerReset.xml`](../examples/P_Demo_CouplerReset.xml) |

---

## 1. 功能简述

通过 **2-byte PLC interface** 触发 BC / BK 系列耦合器的复位。复位完成后耦合器会：经 K-bus 重新扫描端子配置（让刚刚热插上的新端子被识别）、重新初始化 K-bus 通信、清除当前现有的 K-bus 错误状态。这是在线检测/解除"K-bus 故障"的关键 FB——许多老线在端子掉电瞬间报 K-bus error，光复位 PLC 没用，必须复位耦合器本身。

握手协议走 2-byte PLC interface：调用方在 System Manager 里把现场总线（Profibus / Lightbus / Interbus 等）耦合器的 control word 和 status word 各 2 字节链接到本 FB 的 `STATE`（输入：耦合器 → PLC 的 status word）和 `CONTROL`（输出：PLC → 耦合器的 control word）。FB 内部按 Beckhoff 私有的 2-byte 协议驱动 control word 完成一次复位握手。

注意输入名 `STATE` / 输出名 `CONTROL` 在 PDF 里都是 `PLCINTFSTRUCT`（两个 BYTE 的结构体）。`PLCINTFSTRUCT` 详见同库的 Data types §5.1。

## 2. 接口定义

### VAR_INPUT

```iecst
VAR_INPUT
    STATE   : PLCINTFSTRUCT;
    START   : BOOL;
    TMOUT   : TIME;
END_VAR
```

| 名称 | 类型 | 默认值 | 说明 |
|---|---|---|---|
| `STATE` | `PLCINTFSTRUCT` | — | 2-byte PLC interface 的状态字（耦合器 → PLC 方向）；在 System Manager 中链接到耦合器的 PLC interface status word |
| `START` | `BOOL` | — | 上升沿触发一次复位。复位过程中即使把本输入恢复 FALSE 也不影响当前进度 |
| `TMOUT` | `TIME` | — | 整个复位握手允许的最大时长。K-bus 重新扫描端子需 1-3 秒，建议设 ≥ T#5S 留充分余量 |

### VAR_OUTPUT

```iecst
VAR_OUTPUT
    CONTROL  : PLCINTFSTRUCT;
    BUSY     : BOOL;
    ERR      : BOOL;
    ERRID    : UDINT;
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `CONTROL` | `PLCINTFSTRUCT` | 2-byte PLC interface 的控制字（PLC → 耦合器方向）；必须链接到耦合器的 PLC interface control word |
| `BUSY` | `BOOL` | FB 激活后置 TRUE，复位完成或超时后清零 |
| `ERR` | `BOOL` | 错误发生时在 `BUSY` 下降之后置 TRUE |
| `ERRID` | `UDINT` | `ERR = TRUE` 时给出错误号，见下方错误码表 |

### VAR_IN_OUT

无。

## 3. 行为说明

**触发**：`START` 上升沿启动一次复位。`BUSY := TRUE` 全程保持，直到 K-bus 扫完所有端子、耦合器返回新的 status word 表示就绪，或 `TMOUT` 到时强制结束。

**内部时序**：
1. `START` 上升沿 → `BUSY := TRUE`，FB 把 `CONTROL` 中对应的 reset bit 置位（2-byte PLC interface 协议规定的固定位，PDF 未公开具体位号，由库内部处理）。
2. 耦合器收到 reset 命令后开始：① 断 K-bus 通信 → ② 重新枚举挂在 K-bus 上的所有端子 → ③ 重建端子表 → ④ 在 `STATE` 中应答"复位完成"。这一过程通常耗时 1-3 秒，挂的端子多时更长。
3. FB 看到应答后清零 `CONTROL` 的 reset bit，`BUSY := FALSE`，`ERR := FALSE`。
4. 若 `TMOUT` 时间到仍未收到应答 → `BUSY := FALSE`，`ERR := TRUE`，`ERRID := 16#300`。

**复位的副作用**：
- 现有的 K-bus 错误（在 `STATE` 中表现的 fieldbus / K-bus error 位）会被**清除**。这是清错的合法手段。
- 现场总线（Profibus / Lightbus 等）通信**不**会断——复位仅作用于 K-bus 侧。
- 复位期间端子的过程数据**全部停止刷新**：AI 值冻结、AO 值保持上次写入的值；恢复后从新值开始。这意味着不能在工艺正常运行时随便复位耦合器。

**典型用法**：① 检测 `STATE` 的 K-bus error 位被置位时（端子掉电、端子热插拔后未识别）→ 上升沿触发本 FB 复位耦合器尝试自动恢复；② 维护时手动按按钮复位让耦合器重新扫描刚换上的备件端子；③ 上电后做一次软复位确保耦合器从干净状态开始。

**与硬件复位的区别**：本 FB 等价于"耦合器面板上的 reset 按钮"，但不重启耦合器固件，比断电更快、对其它通讯无影响。要彻底重启耦合器仍需断电。

## 4. 错误码 / 返回值

本 FB 无 HRESULT 返回；通过 `ERR` / `ERRID` 表达错误（PDF §3.2 错误号表）：

| `ERRID` | 含义 | 常见原因 |
|---|---|---|
| `0` | 无错 | — |
| `16#100` | 2-byte PLC interface 通信初始化失败 | `STATE` / `CONTROL` 没在 System Manager 链接到耦合器真实 PLC interface；耦合器配置不支持 2-byte PLC interface（某些早期 BK 需要 KS2000 单独打开此选项） |
| `16#200` | 通信过程中错误 | 复位期间耦合器异常断开、应答帧损坏 |
| `16#300` | 超时 | K-bus 上端子过多 / 有故障端子卡住扫描 / `TMOUT` 设得过短 |
| `16#400` | 寄存器号参数错 | 对 CouplerReset 来说几乎遇不到（本 FB 不暴露寄存器号给用户），但库内部下层共用错误码空间 |
| `16#500` | 表号参数错 | 同上 |

## 5. 使用注意 / 常见坑

- **`STATE` / `CONTROL` 必须在 System Manager 链接到耦合器的 2-byte PLC interface IO**。许多老配置默认是 0-byte PLC interface（不映射 control/status），这种情况下 FB 永远 `BUSY = TRUE`，到时间报 `16#100`。在 Lightbus / Profibus 这种总线上可以在 System Manager 直接给耦合器选 2-byte interface；Interbus S 等需要先用 KS2000 配置软件打开。
- **复位期间过程数据冻结**。运行中触发会让所有 AI / AO 值短暂停滞 1-3 秒，工艺正在运行时切勿轻易触发——典型事故：印刷机正在跑、操作员见报警就点了"清错"，整个色组的 AO 卡住导致一段废品。建议把复位放到设备 STOP 状态或专用维护页面。
- **`TMOUT` 不要短于 5 秒**。K-bus 端子很多时（30 个以上）扫描需要数秒。设 T#1S 容易误超时然后 ERR = `16#300`。
- **触发逻辑用上升沿，不要电平**。`START` 保持 TRUE 不会反复复位，但下次想复位前必须把 `START` 拉回 FALSE 再置 TRUE，否则 FB 不会再次触发。
- **复位不能解决根本性硬件故障**。如果是端子物理损坏 / 接线断了，复位完 K-bus error 会立即再现。本 FB 是软复位，不替代换硬件。（工程经验补充）
- **不要在 K-bus error 出现的同周期立刻触发复位**。给一点延迟让 status word 稳定，否则可能复位完毕后 error 位又被来不及更新的旧值覆盖。建议错误持续 ≥ 500ms 再触发。（工程经验补充）
- **复位会清除诊断闪烁码缓存**。若想读 `FB_ReadCouplerDiag` 看耦合器的错误闪烁序列，**要在复位前读**，复位后这些诊断信息会被清掉。

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_CouplerReset.xml`](../examples/P_Demo_CouplerReset.xml)（PLCopenXML，可直接导入 TwinCAT 3 XAE）
>
> 导入步骤：右键 PLC 项目 → Import PLCopenXML → 选该文件 → OK
> 详见 [`examples/README.md`](../examples/README.md)

```iecst
// 场景：印刷机控制柜里挂的 BK3120 (Profibus 耦合器) 经常在端子热插拔后报 K-bus
//       error。维护人员希望按一下控制面板上的"K-bus 复位"按钮就自动恢复，无需
//       重启整个站。本程序检测到 K-bus error 位置位 1 秒以上 + 操作员手动触发
//       后，调用 CouplerReset 软复位耦合器。
//
// 价值：不用本 FB 就得：要么走 Profibus 站点 reset（影响整条总线）、要么现场
//       人员去机柜按耦合器面板 reset 按钮（机柜内部高压区不安全）、要么停机
//       断电。本 FB 让 PLC 程序在不影响其它站和操作员人身安全的前提下软复位。
//
// 验证：登录后人为拔掉一个 KLxxx 端子 → 观察 stCouplerStatus.Byte0 的
//       K-bus error 位被置 1；插回端子但 K-bus error 仍不自动清除 →
//       置 bMaintenanceResetRequest := TRUE 一个脉冲 → bResetBusy 闪一下，
//       1-3 秒后 K-bus error 位清零，bResetError = FALSE。
PROGRAM P_Demo_CouplerReset
VAR
    fbResetCoupler             : CouplerReset;
    // —— 在 System Manager 把 BK3120 的 2-byte PLC interface 链到这两个变量 ——
    stCouplerStatus    AT %I*  : PLCINTFSTRUCT;       // 耦合器 -> PLC
    stCouplerControl   AT %Q*  : PLCINTFSTRUCT;       // PLC -> 耦合器

    bMaintenanceResetRequest   : BOOL;                 // 操作员按钮单脉冲
    tResetTimeout              : TIME := T#10S;        // K-bus 端子多时给足时间

    bResetBusy                 : BOOL;
    bResetError                : BOOL;
    nResetErrId                : UDINT;
END_VAR

// 单次调用形式：所有 VAR_INPUT 显式赋值。CONTROL 经 => 截获到链好的 IO 变量
fbResetCoupler(
    STATE   := stCouplerStatus,
    START   := bMaintenanceResetRequest,
    TMOUT   := tResetTimeout,
    CONTROL => stCouplerControl,
    BUSY    => bResetBusy,
    ERR     => bResetError,
    ERRID   => nResetErrId
);
```

## 7. 业务场景与实际价值

- **场景**：BC / BK 系列 K-bus 耦合器在役系统里，端子热插拔、端子掉电恢复、上电时序竞争等情况经常导致 K-bus error。需要"软复位"耦合器让它重新扫描 K-bus 并清错。典型行业：印刷、灌装、纺织、汽车焊装老线。
- **价值**：把"驱动 2-byte PLC interface control word + 等待 K-bus 重扫描完成 + 状态机超时管理"这套低层握手协议封装为一次调用，业务代码只关心"什么时候按下复位"这一件事。比断电重启快 10 倍，且不影响同总线上其它从站。
- **替代方案对比**：
  - 现场按耦合器面板 reset 按钮：机柜内部不安全 / 操作员不方便
  - Profibus 站点 reset（DPV1 service）：会瞬间打断本站所有通信，影响范围大
  - 整柜断电：彻底但工艺中断时间长，对连续工艺（印刷、灌装）代价高
  - **本 FB**：纯软件、PLC 程序内触发、只影响目标耦合器、不打断其它站；是 K-bus 故障自愈策略的标准做法

## 8. 参考资料

- **PDF**：[TwinCAT_3_PLC_Lib_Tc2_Coupler_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_Coupler_EN.pdf) §3.2
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tcplclib_tc2_coupler/42592779.html
- **相关**：`PLCINTFSTRUCT`（Tc2_Coupler §5.1，2 字节结构体）、`FB_ReadCouplerDiag`（读复位前的错误闪烁码）、`FB_ReadCouplerRegs` / `FB_WriteCouplerRegs`（修改耦合器表寄存器后通常配合本 FB 让改动生效）
