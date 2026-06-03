# FB_EcGetSlaveCrcErrorEx

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc2_EtherCAT` |
| Library Version | `1.9.5` |
| Type | `FUNCTION_BLOCK` |
| Category | `EtherCAT Diagnostic` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_EtherCAT_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tcplclib_tc2_ethercat/2239483787.html |
| Verified | 2026-06-03 ✅ |
| InfoSys-checked | ✅ 2026-06-03 |
| Status | `verified` |
| Example | [`examples/P_Demo_FB_EcGetSlaveCrcErrorEx.TcPOU`](../examples/P_Demo_FB_EcGetSlaveCrcErrorEx.TcPOU) |

---

## 1. 功能简述

读取 4 端口从站（典型 EK1122 分支耦合器）所有端口 A、D、B、C 的 CRC 错误计数。返回 `ST_EcCrcErrorEx` 结构。是 `FB_EcGetSlaveCrcError`（3 端口版）的扩展版本，多了 D 端口。

## 2. 接口定义

### VAR_INPUT

```iecst
VAR_INPUT
    sNetId      :  T_AmsNetId;
    nSlaveAddr  :  UINT;
    bExecute    :  BOOL;
    tTimeout    :  TIME;
END_VAR
```

| 名称 | 类型 | 默认值 | 说明 |
|---|---|---|---|
| `sNetId` | `T_AmsNetId` | — | EtherCAT 主站 AMS NetID |
| `nSlaveAddr` | `UINT` | — | 要查询的从站固定地址 |
| `bExecute` | `BOOL` | — | 上升沿触发一次读 |
| `tTimeout` | `TIME` | — | ADS 调用超时（无默认值，需显式传） |

### VAR_OUTPUT

```iecst
VAR_OUTPUT
    bBusy     :  BOOL;
    bError    :  BOOL;
    nErrId    :  UDINT;
    CrcError  :  ST_EcCrcErrorEx;
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `bBusy` | `BOOL` | 命令进行中 |
| `bError` | `BOOL` | 出错置 `TRUE` |
| `nErrId` | `UDINT` | ADS 错误码 |
| `CrcError` | `ST_EcCrcErrorEx` | 4 端口 CRC 错误计数（A、D、B、C 各 1 个 BYTE，详见 §13.5） |

### VAR_IN_OUT

无。

## 3. 行为说明

**触发**：`bExecute` 上升沿；`bBusy` 落沿后读 `CrcError`。

**端口命名顺序**：PDF 明确写 A、D、B、C —— D 端口在 A 之后；这是 EK1122 物理布局决定的。结构体字段顺序需对照 `ST_EcCrcErrorEx`。

**EK1122 分支拓扑**：上游进 A，下游级联线接 B，两条分支接 C 和 D。当某分支线缆质量差时，对应端口计数会单独累加。

**典型用法**：用 `FB_EcGetAllSlaveCrcErrors` 锁定问题 EK1122 之后调本 FB 进一步分端口；尤其当 EK1122 接的两个分支链路一好一坏时，本 FB 是定位关键。

**典型陷阱**：
- 误把 3 端口从站地址传入 → D 端口字段值无意义
- `tTimeout` 无默认值，必须显式传 `DEFAULT_ADS_TIMEOUT`

## 4. 错误码 / 返回值

| `nErrId` | 含义 | 处理建议 |
|---|---|---|
| `0` | 成功 | 读 `CrcError` |
| `1861` (`0x745`) | ADS 超时 | 增大 `tTimeout` |

## 5. 使用注意 / 常见坑

- **仅 4 端口从站**：EK1122 / EP1122 / 部分 EK1101 衍生型号；3 端口从站用 `FB_EcGetSlaveCrcError`
- **`tTimeout` 必填**：不传会立即超时
- **现场端口对应**（工程经验补充）：EK1122 物理上"A/D 在上层、B/C 在下层"，按实际机柜布线 vs 计数判断哪条物理线松动

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_FB_EcGetSlaveCrcErrorEx.TcPOU`](../examples/P_Demo_FB_EcGetSlaveCrcErrorEx.TcPOU)
>
> 导入步骤：右键 PLC 项目下 POUs 文件夹 → Add → Existing Item → 选该文件 → OK

详见 example xml 文件。

## 7. 业务场景与实际价值

- **场景**：某 EK1122 接两条 EtherCAT 分支（D 出主控柜、C 出辅控柜）。主控柜 CRC 偶发增长，辅控柜不发生 —— 本 FB 一查发现仅 D 端口在涨 → 主控柜布线问题
- **价值**：4 端口精度的 CRC 定位，是 3 端口版无法做到的
- **替代方案对比**：FPRD 读 ESC 寄存器 → 手算偏移繁琐；本 FB → 1 次调用拿结构体

## 8. 参考资料

- **PDF**：[TwinCAT_3_PLC_Lib_Tc2_EtherCAT_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_EtherCAT_EN.pdf) §4.13
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tcplclib_tc2_ethercat/2239483787.html
- **相关 FB / FC**：`FB_EcGetSlaveCrcError`（3 端口）、`FB_EcGetAllSlaveCrcErrors`、`ST_EcCrcErrorEx`
