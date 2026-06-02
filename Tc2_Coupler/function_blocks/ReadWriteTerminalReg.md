# ReadWriteTerminalReg

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc2_Coupler` |
| Library Version | `1.1.1` |
| Type | `FUNCTION_BLOCK` |
| Category | `Function blocks` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_Coupler_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tcplclib_tc2_coupler/42591243.html |
| Verified | 2026-05-11 ✅ |
| InfoSys-checked | ✅ 2026-05-11 |
| Status | `verified` |
| Example | [`examples/P_Demo_ReadWriteTerminalReg.TcPOU`](../examples/P_Demo_ReadWriteTerminalReg.TcPOU) |

---

## 1. 功能简述

通过端子通道的 control/status 字节，对智能 KL/KS 端子（如 KL3xxx 模拟输入、KL4xxx 模拟输出、KL5xxx 计数器等）内部的寄存器做**点对点读/写**。智能端子在标准运行模式下用过程映像里的 data input / data output 字交换工艺数据；本功能块用 control/status 字节做一次"握手"，把通道临时切到寄存器通信模式，把指定寄存器号的值从 data output / data input 字搬过去，搬完再切回工艺数据模式。

`READ` 上升沿读寄存器、`WRITE` 上升沿写寄存器（写时本 FB 会自动解除该寄存器的写保护、写完后再重新开启写保护）。写访问内部会"先写后读回"，读回的值出现在 `CURRREGVALUE`，调用方可借此验证写入是否真正成功。

前提：在 TwinCAT System Manager 里必须把 `STATE` / `DATAIN` / `CTRL` / `DATAOUT` **链接到对应端子通道的 IO 变量**（要求端子按 complex mapping 映射，compact mapping 不暴露 control/status 字节）；并且寄存器的修改要**持久化必须断电重启耦合器**——只在线写不重启，断电后改动会丢。

## 2. 接口定义

### VAR_INPUT

```iecst
VAR_INPUT
    STATE       : BYTE;
    DATAIN      : WORD;
    REGNO       : BYTE;
    READ        : BOOL;
    WRITE       : BOOL;
    TMOUT       : TIME;
    NEWREGVALUE : WORD;
END_VAR
```

| 名称 | 类型 | 默认值 | 说明 |
|---|---|---|---|
| `STATE` | `BYTE` | — | 端子通道的状态字节。必须在 System Manager 链接到对应端子 channel 的 status byte 输入 |
| `DATAIN` | `WORD` | — | 端子通道的数据输入字（PLC 视角的 input）。寄存器读出后的值经此字传回 |
| `REGNO` | `BYTE` | — | 要读 / 写的寄存器号（0..63；具体范围参考端子手册：通用寄存器 0-31 与厂家功能寄存器 32-63） |
| `READ` | `BOOL` | — | 上升沿激活一次读访问。读成功后 `CURRREGVALUE` 输出当前寄存器值 |
| `WRITE` | `BOOL` | — | 上升沿激活一次写访问。把 `NEWREGVALUE` 写入 `REGNO` 指定寄存器，写完自动读回，`CURRREGVALUE` 输出读回值 |
| `TMOUT` | `TIME` | — | 单次访问的最大允许时间。超时后 `ERR := TRUE`、`ERRID := 16#100` |
| `NEWREGVALUE` | `WORD` | — | 写访问时要写入的数值（读访问时忽略） |

### VAR_OUTPUT

```iecst
VAR_OUTPUT
    CTRL        : BYTE;
    DATAOUT     : WORD;
    BUSY        : BOOL;
    ERR         : BOOL;
    ERRID       : UDINT;
    CURREGVALUE : WORD;
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `CTRL` | `BYTE` | 端子通道的控制字节，由本 FB 驱动；必须在 System Manager 链接到对应 channel 的 control byte 输出 |
| `DATAOUT` | `WORD` | 端子通道的数据输出字（PLC 视角的 output）。写访问时本 FB 把 `NEWREGVALUE` 经此字送给端子 |
| `BUSY` | `BOOL` | FB 激活后保持 TRUE，直到本次读 / 写完成或超时；外部代码不要在 `BUSY = TRUE` 时再触发新的上升沿 |
| `ERR` | `BOOL` | 发生错误时本输出在 `BUSY` 下降之后置 TRUE |
| `ERRID` | `UDINT` | `ERR = TRUE` 时给出错误号，见下方错误码表 |
| `CURREGVALUE` | `WORD` | 一次成功的读或写访问完成后，存放当前寄存器的实际值 |

### VAR_IN_OUT

无。

## 3. 行为说明

**两类触发**：`READ` 上升沿做一次读、`WRITE` 上升沿做一次写。同周期同时来 `READ` 与 `WRITE` 上升沿，由实现选其一（建议程序上互斥）。

**单次读访问的内部时序**：
1. `READ` 上升沿 → `BUSY := TRUE`，FB 把 `CTRL` 的高位置位切到寄存器通信模式，再把 `REGNO` 编码进 control/data 字节。
2. 等端子在 `STATE` 中应答（握手）。在 `TMOUT` 内未应答 → `ERR := TRUE`，`ERRID := 16#100`，`BUSY := FALSE`。
3. 应答后端子把寄存器值通过 `DATAIN` 送回。FB 读出后写入 `CURRREGVALUE`，把 `CTRL` 切回工艺数据模式，`BUSY := FALSE`，`ERR := FALSE`。

**单次写访问的内部时序**：
1. `WRITE` 上升沿 → `BUSY := TRUE`，FB 先写**密码寄存器 31** 解除写保护（端子内部协议固定动作，调用方无需处理）。
2. 把 `NEWREGVALUE` 经 `DATAOUT` 写入 `REGNO` 寄存器。
3. 立即再读一次同一寄存器，读回值放进 `CURRREGVALUE`。如果读回值 ≠ 写入值 → `ERR := TRUE`，`ERRID := 16#300`（可能是该寄存器只读、或写保护未生效）。
4. 再写回密码寄存器 0 恢复写保护，`BUSY := FALSE`。

**典型用法**：上电时一次性读端子型号寄存器（reg 8）校验现场布线，或运行时改 KL3xxx / KL4xxx 的 feature register（reg 32）切换量程 / 滤波 / 用户标定等参数。

**典型陷阱**：寄存器修改在端子内是**易失**的——掉电后回到 EEPROM 中存的值。如果改动要持久化，**必须重启耦合器**让端子把寄存器值写回 EEPROM；不重启的话下次断电后改动全丢，现场常发生"调好的量程一停机就回到出厂值"的情况。

## 4. 错误码 / 返回值

本 FB 无 HRESULT 返回；通过 `ERR` / `ERRID` 表达错误（PDF §3.1 错误号表）：

| `ERRID` | 含义 | 常见原因 |
|---|---|---|
| `0` | 无错 | — |
| `16#100` | 超时 | `STATE` / `CTRL` 没在 System Manager 链接到端子真实 IO；端子离线；`TMOUT` 设得过短（建议 ≥ T#100ms） |
| `16#200` | 参数错 | `REGNO` 越界或对该端子无意义 |
| `16#300` | 读回值 ≠ 写入值 | 该寄存器只读、写保护未能解除、或写入数据格式不符合该寄存器规定 |

## 5. 使用注意 / 常见坑

- **必须是 complex mapping**。在 System Manager 里给端子选 "Standard"（compact）映射时不暴露 control/status 字节，本 FB 永远 `BUSY = TRUE`、永不返回。换成 "Complex" / "Compact + Status" 映射后才能用。
- **不要把本 FB 放在循环里反复 read/write**。PDF NOTICE 明确警告：寄存器写在端子内部走 EEPROM，循环写会**烧死 EEPROM**（典型寿命 10 万次量级）。本库定位是"调试 / 配置时使用"，不是工艺数据通道。
- **`STATE`/`CTRL`/`DATAIN`/`DATAOUT` 必须是同一个通道的同一对 IO**。常见错误：链接到了相邻通道的 control 字节（KL3404 这种 4 通道端子很容易接错），现象是 FB 不报错但读到的寄存器值像是别的通道的；排查方法是先用 reg 8（端子型号）验通道编号。
- **改寄存器后必须重启耦合器才能持久**。在线写完别忘了断电再上电；许多团队把这一步漏掉，每次开机要现场重新调一遍参数。（工程经验补充）
- **`READ` / `WRITE` 用上升沿，不是电平**。上升沿后保持 `READ := TRUE` 不会一直读，要先复位再次置位才能再触发；切勿把 `READ := bSomeFlag` 然后让 bSomeFlag 一直为 TRUE。
- **`TMOUT` 不要短于 T#100ms**。K-bus 一次完整握手通常 20-50ms，再加 PLC 任务周期 jitter，T#50ms 这种值会偶发误超时。建议 T#500ms 起步。
- **多 FB 实例不要同时操作同一通道**：两个 `ReadWriteTerminalReg` 实例链接到同一通道的 control 字节会互相打架，必须串行化（用 SR 锁、或同周期只触发一个）。

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_ReadWriteTerminalReg.TcPOU`](../examples/P_Demo_ReadWriteTerminalReg.TcPOU)（TwinCAT 3 原生 .TcPOU，可直接拖入 XAE 的 PLC POUs 文件夹）
>
> 导入步骤：右键 PLC 项目下 POUs 文件夹 → Add → Existing Item → 选该文件 → OK
> 详见 [`examples/README.md`](../examples/README.md)

```iecst
// 场景：现场有一台 BK1120 + KL3464（4 通道 ±10V 模拟输入）端子排，本机 PLC
//       需要：① 上电时读 KL3464 通道 1 的端子型号寄存器（reg 8）校验布线；
//       ② 把通道 1 的 feature register（reg 32）改成 16#0006 启用 user
//       scaling，让后续 AI 值经用户标定后再进 PLC。
//
// 价值：不用本 FB 就得手写 control/status 握手协议、密码寄存器 31 解锁、
//       写后读回校验、超时管理；本 FB 把这些都封装好。
//
// 验证：登录后单脉冲 bReadTerminalIdRequest → 观察 nCurrentRegValue 应为
//       16#0D80（KL3464 的端子号 3456 = 0x0D80）；之后单脉冲
//       bWriteFeatureRegRequest → 观察 nCurrentRegValue 应为 16#0006，
//       bAccessError 保持 FALSE。最后断电重启耦合器让改动生效。
PROGRAM P_Demo_ReadWriteTerminalReg
VAR
    fbTermReg               : ReadWriteTerminalReg;
    // —— Channel 1 IO，需在 System Manager 里链到 KL3464 通道 1 的状态/控制/数据 IO ——
    nKL3464Ch1Status        AT %I*  : BYTE;
    wKL3464Ch1DataIn        AT %I*  : WORD;
    nKL3464Ch1Control       AT %Q*  : BYTE;
    wKL3464Ch1DataOut       AT %Q*  : WORD;

    // —— 业务侧触发与显示 ——
    bReadTerminalIdRequest  : BOOL;                 // 单脉冲：读 reg 8 校验型号
    bWriteFeatureRegRequest : BOOL;                 // 单脉冲：写 reg 32 启用 user scaling
    tAccessTimeout          : TIME := T#500MS;      // 不要短于 100ms
    wNewFeatureRegValue     : WORD := 16#0006;      // bit1=enable user scaling, bit2=enable filter

    bAccessBusy             : BOOL;
    bAccessError            : BOOL;
    nLastAccessErrId        : UDINT;                // 0/16#100/16#200/16#300
    wCurrentRegValue        : WORD;                 // 读 reg 8 应得 16#0D80
END_VAR

// 单次调用形式：READ 与 WRITE 互斥；同周期同时来上升沿由 FB 内部决定。
// 现实工程里一般在按钮 / 状态机里保证只发其中一个。
fbTermReg(
    STATE       := nKL3464Ch1Status,
    DATAIN      := wKL3464Ch1DataIn,
    REGNO       := 8 * BOOL_TO_BYTE(bReadTerminalIdRequest)
                  + 32 * BOOL_TO_BYTE(bWriteFeatureRegRequest),
    READ        := bReadTerminalIdRequest,
    WRITE       := bWriteFeatureRegRequest,
    TMOUT       := tAccessTimeout,
    NEWREGVALUE := wNewFeatureRegValue,
    CTRL        => nKL3464Ch1Control,
    DATAOUT     => wKL3464Ch1DataOut,
    BUSY        => bAccessBusy,
    ERR         => bAccessError,
    ERRID       => nLastAccessErrId,
    CURREGVALUE => wCurrentRegValue
);
```

## 7. 业务场景与实际价值

- **场景**：基于 BC / BK 系列耦合器 + KLxxx 智能端子的传统现场布线（仍在汽车焊装线、印刷、灌装等行业大量在役）。需要在 PLC 程序里读 / 改端子内部寄存器，例如校验布线时读端子型号、运行时切换 AI 量程、修改用户标定系数、开关 oversampling、读端子故障寄存器等。
- **价值**：把 control/status 字节握手、密码寄存器 31 写保护解 / 锁、写后读回校验、超时检测这一整套底层协议封装成 1 个调用。业务代码只关心"读哪个寄存器 / 写什么值"，省下 30-50 行手写状态机和易错的 K-bus 协议。
- **替代方案对比**：
  - 手写 control/status 握手：能做，但密码寄存器与"先写后读回"细节容易出 bug；调试时常碰到"写完没生效但 FB 报成功"
  - 用 KS2000 配置软件：可视化界面好，但只能离线配置，无法在 PLC 程序运行中根据工艺动态切换寄存器
  - 改用 EtherCAT + EL 端子 + CoE SDO：现代方案，可靠性更好；但要求换硬件，老线改造代价高
  - **本 FB**：在不改硬件的前提下让 BC / BK + KL 设备具备运行时配置能力，是 K-bus 时代的标准做法

## 8. 参考资料

- **PDF**：[TwinCAT_3_PLC_Lib_Tc2_Coupler_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_Coupler_EN.pdf) §3.1
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tcplclib_tc2_coupler/42591243.html
- **相关**：`FB_ReadCouplerRegs`（读耦合器/端子表寄存器，批量）、`FB_WriteCouplerRegs`（写）、`CouplerReset`（改完寄存器复位耦合器）、`FB_ReadCouplerDiag`（读耦合器错误闪烁码）；端子内部寄存器布局见对应 KLxxx 端子手册的 "Object description and parameterization" 章
