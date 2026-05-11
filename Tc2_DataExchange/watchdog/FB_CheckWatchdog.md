# FB_CheckWatchdog

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc2_DataExchange` |
| Library Version | `1.2.2` |
| Type | `FUNCTION_BLOCK` |
| Category | `Watchdog function blocks` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_DataExchange_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tcplclib_tc2_dataexchange/54802699.html |
| Verified | 2026-05-11 ✅ |
| InfoSys-checked | ✅ 2026-05-11 |
| Status | `verified` |
| Example | [`examples/P_Demo_FB_CheckWatchdog.xml`](../examples/P_Demo_FB_CheckWatchdog.xml) |

---

## 1. 功能简述

接收端 watchdog 监视器。两台 TwinCAT 设备通过 ADS 互联时，发送端用 `FB_WriteWatchdog` 周期性把一个递增计数器写到接收端的某个内存地址；接收端用 `FB_CheckWatchdog` 读取这个计数器，看它在指定的时间窗口 `tWatchdogTime` 内是否变过。**变过表示链路正常**（`bWatchdog := FALSE`）；**超过 `tWatchdogTime` 没变表示链路或对端死了**（`bWatchdog := TRUE`，即"看门狗咬人了"）。

注意输出语义反直觉：**`bWatchdog = FALSE` 是健康状态**，`TRUE` 是故障状态。这与"watchdog 触发即报警"的工业惯例一致。

## 2. 接口定义

### VAR_INPUT

```iecst
VAR_INPUT
    bEnable        :  BOOL := FALSE;
    tWatchdogTime  :  TIME := t#0s;
    nCnt           :  UDINT;
END_VAR
```

| 名称 | 类型 | 默认值 | 说明 |
|---|---|---|---|
| `bEnable` | `BOOL` | `FALSE` | 使能本 FB。`FALSE` 时不做任何监视，`bWatchdog` 保持当前值 |
| `tWatchdogTime` | `TIME` | `t#0s` | 容许 `nCnt` 静止不变的时长。**特例**：`t#0s` 时强制 `bWatchdog := FALSE`（监视功能被关闭，永远报"健康"）。InfoSys 建议设为发送端周期的 5-10 倍 |
| `nCnt` | `UDINT` | — | 当前从对端读到的 watchdog 计数值（通常由用户代码先用 ADS 读对端再喂给本 FB） |

### VAR_OUTPUT

```iecst
VAR_OUTPUT
    bWatchdog  : BOOL := FALSE;
    nLastCnt   : UDINT;
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `bWatchdog` | `BOOL` | `FALSE` = 链路健康（`nCnt` 在 `tWatchdogTime` 内变过）；`TRUE` = 链路超时（看门狗咬人）。**注意反向语义** |
| `nLastCnt` | `UDINT` | 最近一次观察到变化时的计数值快照。用于诊断：与当前 `nCnt` 对比可看出对端是否还活着 |

### VAR_IN_OUT

无。

## 3. 行为说明

**触发**：每个 PLC 周期调用一次。内部维护一个计时器和上一次的 `nCnt` 快照。

**状态机**（仅 `bEnable = TRUE` 时生效）：

1. 当前 `nCnt` 与上次保存的 `nLastCnt` 不同 → 复位计时器 + 更新 `nLastCnt := nCnt` + 输出 `bWatchdog := FALSE`
2. `nCnt` 与 `nLastCnt` 相同 → 累加计时器；累加值未达 `tWatchdogTime` → `bWatchdog := FALSE` 维持；累加值 ≥ `tWatchdogTime` → `bWatchdog := TRUE`

**两个特殊分支**：

- `tWatchdogTime = t#0s`：直接 `bWatchdog := FALSE`，不进入超时判断（用来临时禁用监视）
- `bEnable = FALSE`：FB 不做任何更新，`bWatchdog` 保留之前的值（**不**会自动复位为 FALSE，重新使能后需要 `nCnt` 真正变化才回 FALSE）

`bWatchdog` 一旦变 `TRUE`，只要下一次 `nCnt` 变化即立刻回 `FALSE`，无需手动清错。

## 4. 错误码 / 返回值

本 FB 无 `bError` / `nErrorId` 输出；状态仅通过 `bWatchdog` 反映（FALSE = OK，TRUE = 超时）。无 HRESULT 返回。

（注：发送端 `FB_WriteWatchdog` 才有 ADS 错误输出。早期 doc 把它的错误码段错抄到本文档，已修正。）

## 5. 使用注意 / 常见坑

- **`bWatchdog` 语义反直觉**：FALSE 表示健康。第一次用很容易把判断写反，把"咬人"当成"正常"。建议本地包一层取反：`bLinkAlive := NOT fbCheck.bWatchdog`。
- **`tWatchdogTime` 不能太短**。发送端 ADS 写入本身有抖动，再加上 PLC 任务周期偏差，如果 `tWatchdogTime` 接近发送周期（例如发送 1s 一次、监视 1s），网络稍微卡一下就误报。**InfoSys 明确建议 5-10 倍发送周期**。
- **`nCnt` 必须真的来自对端**。常见错误是用户写 `fbCheck(nCnt := MyLocalCounter)`，本地 PLC 自己递增，监视永远不报警——失去意义。`nCnt` 必须经过 ADS 读取从对端拿回。
- **首次使能时 `nCnt` 未必立刻变化**，初始几个 `tWatchdogTime` 窗口可能直接出超时。可在 `bEnable` 上升沿后延迟若干秒再开始判断结果。（工程经验补充）
- **`bEnable` 撤销不会清错**：从 TRUE → FALSE 后 `bWatchdog` 不会自动复位为 FALSE，下次重新使能后还要等 `nCnt` 真变一次才回 FALSE。需要重置状态时，建议在 `bEnable` 上升沿额外发一个 `nCnt` "+1" 脉冲。（工程经验补充）

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_FB_CheckWatchdog.xml`](../examples/P_Demo_FB_CheckWatchdog.xml)（PLCopenXML，可直接导入 TwinCAT 3 XAE）
>
> 导入步骤：右键 PLC 项目 → Import PLCopenXML → 选该文件 → OK
> 详见 [`examples/README.md`](../examples/README.md)

```iecst
// 场景：本机是接收端，通过 ADS 周期性读取 Master 工控机内一个 UDINT 计数器，
//       监视 Master 是否还活着。tWatchdogTime 设为 5 秒（发送端 1 秒一次的 5 倍）。
//
// 价值：不用本 FB 就得自己写：保存上一次值 + 累加计时器 + 与门限对比 + 重置逻辑。
//       本 FB 把这套逻辑封装好，调用方只关心 nCnt 进来、bWatchdog 出去。
//
// 验证：在线把 nWatchdogCounterFromMaster 在线写值持续递增（模拟 Master 正常工作）→
//       观察 bLinkAlive 保持 TRUE；停止递增超过 5 秒 → 观察 bLinkAlive 翻为 FALSE。
//       恢复递增 → 观察 bLinkAlive 在下一个 PLC 周期立刻回 TRUE。
PROGRAM P_Demo_FB_CheckWatchdog
VAR
    fbCheckWatchdog              : FB_CheckWatchdog;
    nWatchdogCounterFromMaster   : UDINT;            // 在线 monitor / 在线写值模拟
    bEnableLinkMonitor           : BOOL := TRUE;
    tLinkTimeoutWindow           : TIME := T#5S;     // = 5 × Master 发送周期
    bLinkAlive                   : BOOL;             // 取反后语义友好
    nLastSeenCounter             : UDINT;            // 诊断用
END_VAR

// 注：单次调用形式，所有 VAR_INPUT 显式赋值；输出端用 => 截获
fbCheckWatchdog(
    bEnable       := bEnableLinkMonitor,
    tWatchdogTime := tLinkTimeoutWindow,
    nCnt          := nWatchdogCounterFromMaster,
    bWatchdog     => bLinkAlive,                     // 此处 bLinkAlive 会反过来：咬人=TRUE
    nLastCnt      => nLastSeenCounter
);

// 业务侧取反更直觉
bLinkAlive := NOT bLinkAlive;                        // 现在 TRUE = 链路活着
```

## 7. 业务场景与实际价值

- **场景**：双 PLC 主备热备 / PLC ↔ HMI 通讯 / PLC ↔ 远程 IO 节点。本机负责"看护"对端，对端死了要立刻切到备份链路或报警停机。典型行业：印刷机、灌装线、PLC 主备冗余。
- **价值**：业务代码只需提供"从对端读到的计数器"和"超时门限"两个量，超时判定、状态复位、首次启动初始化全部由本 FB 处理，省下约 15-20 行手写状态机。结合 `FB_WriteWatchdog`（发送端）形成一对完整的链路保活方案。
- **替代方案对比**：
  - 手写状态机：能做但容易在边界条件出 bug（首次启动、重新使能、`tWatchdogTime = 0` 特例）
  - 用 ADS 通讯库自带超时（`tTimeout`）：只检测单次 ADS 失败，无法检测对端 PLC 程序"假活"（ADS 通但用户程序卡死）
  - **本 FB**：通过对端用户程序递增的计数器证明对端**用户层**还在跑，比 ADS 层超时更可靠

## 8. 参考资料

- **PDF**：[TwinCAT_3_PLC_Lib_Tc2_DataExchange_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_DataExchange_EN.pdf) §4.1
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tcplclib_tc2_dataexchange/54802699.html
- **相关 FB**：`FB_WriteWatchdog`（发送端，配套使用）、`F_CmpLibVersion`（Tc2_System，版本对比辅助）
