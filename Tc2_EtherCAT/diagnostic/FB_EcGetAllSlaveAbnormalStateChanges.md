# FB_EcGetAllSlaveAbnormalStateChanges

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc2_EtherCAT` |
| Library Version | `1.9.5` |
| Type | `FUNCTION_BLOCK` |
| Category | `EtherCAT Diagnostic` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_EtherCAT_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tcplclib_tc2_ethercat/2239479947.html |
| Verified | 2026-06-03 ✅ |
| InfoSys-checked | ✅ 2026-06-03 |
| Status | `verified` |
| Example | [`examples/P_Demo_FB_EcGetAllSlaveAbnormalStateChanges.TcPOU`](../examples/P_Demo_FB_EcGetAllSlaveAbnormalStateChanges.TcPOU) |

---

## 1. 功能简述

读取主站连接的所有从站发生过的"非预期状态切换"计数。所谓非预期 (abnormal) 是指未由主站请求、由从站自发触发的状态降级，例如 OP 状态忽然回退到 SAFEOP_ERR。`pAddrBuf` 指向的 UDINT 数组按主站从站顺序填入每个从站的计数值。

## 2. 接口定义

### VAR_INPUT

```iecst
VAR_INPUT
    sNetId   :  T_AmsNetId;
    pAddrBuf :  POINTER TO ARRAY [0..EC_MAX_SLAVES] OF UDINT;
    cbBufLen :  UDINT;
    bExecute :  BOOL;
    tTimeout :  TIME;
END_VAR
```

| 名称 | 类型 | 默认值 | 说明 |
|---|---|---|---|
| `sNetId` | `T_AmsNetId` | — | EtherCAT 主站的 AMS NetID。本机用空串 `''` |
| `pAddrBuf` | `POINTER TO ARRAY [0..EC_MAX_SLAVES] OF UDINT` | — | 接收数组首地址；按从站排序填入每个从站的非预期状态切换次数 |
| `cbBufLen` | `UDINT` | — | 数组字节容量；至少 `nSlaves * 4` 字节 |
| `bExecute` | `BOOL` | — | 上升沿触发一次读 |
| `tTimeout` | `TIME` | — | ADS 调用超时上限 |

### VAR_OUTPUT

```iecst
VAR_OUTPUT
    bBusy   : BOOL;
    bError  : BOOL;
    nErrId  : UDINT;
    nSlaves : UINT; 
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `bBusy` | `BOOL` | 命令进行中 |
| `bError` | `BOOL` | `bBusy` 落沿后若出错则置 `TRUE` |
| `nErrId` | `UDINT` | ADS 错误码；`1798 (0x706)` 空指针、`1797 (0x705)` 缓冲过小 |
| `nSlaves` | `UINT` | 主站连接的从站总数 |

### VAR_IN_OUT

无。

## 3. 行为说明

**触发**：`bExecute` 上升沿启动一次 ADS 读。`bBusy = TRUE` 期间每周期继续调用让 ADS 状态机推进；落沿后才能读 `nSlaves` 和数组。

**计数语义**：每个从站对应数组中一个 UDINT。计数值在主站启动后单调递增，每发生一次"非预期"状态变化（从站自己掉到 SAFEOP_ERR、ERR 等）就 +1。主站请求引起的正常 OP↔SAFEOP↔PREOP 切换不计入。

**典型用法**：周期 1 Hz 或 0.1 Hz 调用本 FB 与上一次结果做差，若某从站新增计数 ≥ 1 → 该从站期间发生了非预期降级，可能是 sync 错乱、链路抖动、温度过热触发安全停机等。

**典型陷阱**：
- 主站重启计数清零，差值算法需要识别 wrap
- 若主站负载高，本 FB 的 ADS 调用本身可能 1861 超时，应分散调用周期
- 该计数是"次数"不是"当前是否在错误状态"。要看当前状态用 `FB_EcGetAllSlaveStates`

## 4. 错误码 / 返回值

| `nErrId` | 含义 | 处理建议 |
|---|---|---|
| `0` | 成功 | 数组可读 |
| `1798` (`0x706`) | `pAddrBuf` 空指针 | 检查 `ADR(arr)` |
| `1797` (`0x705`) | 缓冲区过小 | 数组维度扩大到 `EC_MAX_SLAVES` |
| `1861` (`0x745`) | ADS 超时 | 增大 `tTimeout` |

## 5. 使用注意 / 常见坑

- **`tTimeout` 必须显式赋值**：本 FB 的 `tTimeout` 没有默认值（PDF 原型未带 `:= DEFAULT_ADS_TIMEOUT`），漏填会编译过但 0 ms 立即超时
- **`nSlaves` 与配置一致**：若实际比配置少，说明有从站离线，可结合 `FB_EcGetAllSlavePresentStateChanges` 定位
- **历史日志归零**（工程经验补充）：现场期望"清零计数重新统计"时，应记录本 FB 当前值做基线，PLC 端做差值

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_FB_EcGetAllSlaveAbnormalStateChanges.TcPOU`](../examples/P_Demo_FB_EcGetAllSlaveAbnormalStateChanges.TcPOU)
>
> 导入步骤：右键 PLC 项目下 POUs 文件夹 → Add → Existing Item → 选该文件 → OK

详见 example xml 文件。

## 7. 业务场景与实际价值

- **场景**：某产线 EL3204 温度模块运行中偶发掉到 SAFEOP_ERR 又自动回 OP，PLC 周期日志没抓到瞬时；用本 FB 每 5 s 读一次计数差值，定位是否真有非预期切换发生及哪一台
- **价值**：抓住短时抖动事件 —— 主站缓存的"当前状态"可能已经回到 OP，但本 FB 给出累计次数，能告诉你"过去 5 秒发生过 X 次"
- **替代方案对比**：`FB_EcGetAllSlaveStates` 看的是当前瞬时状态；本 FB 看的是历史累计，互补

## 8. 参考资料

- **PDF**：[TwinCAT_3_PLC_Lib_Tc2_EtherCAT_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_EtherCAT_EN.pdf) §4.2
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tcplclib_tc2_ethercat/2239479947.html
- **相关 FB / FC**：`FB_EcGetAllSlavePresentStateChanges`（断线计数）、`FB_EcGetAllSlaveStates`（当前状态）
