# FB_DALIV2GetSettings

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc2_DALI` |
| Library Version | `2.3.0` |
| Type | `FUNCTION_BLOCK` |
| Category | `Part 102 / Settings (High-Level)` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_DALI_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tcplclib_tc2_dali/index.html |
| Verified | 2026-06-03 ✅ |
| InfoSys-checked | ⚠️ not-on-infosys |
| Status | `verified` |
| Example | [`examples/P_Demo_FB_DALIV2GetSettings.TcPOU`](../examples/P_Demo_FB_DALIV2GetSettings.TcPOU) |

---

## 1. 功能简述

**批量读取灯具所有 DALI 配置寄存器**——一次调用读出灯具的 `ACTUAL DIM LEVEL`、`POWER ON LEVEL`、`SYSTEM FAILURE LEVEL`、`MIN VALUE`、`MAX VALUE`、`FADE RATE`、`FADE TIME`、`RANDOM ADDRESS`、`SHORT ADDRESS`、`SEARCH ADDRESS`、组归属、场景 0..15 值等约 30 项配置。结果填入 `ST_DALIV2DeviceSettings`。

**工程上线后批量校验所有灯配置时的核心 FB**——比逐个调 `QueryXxx` 快得多。

## 2. 接口定义

### VAR_INPUT

```iecst
VAR_INPUT
    bStart           : BOOL;
    bCancel          : BOOL;
    eCommandPriority : E_DALIV2CommandPriority := eDALIV2CommandPriorityMiddle;
    nOptions         : DWORD;
END_VAR
```

| 名称 | 类型 | 默认值 | 说明（中文） |
|---|---|---|---|
| `bStart` | `BOOL` | — | 上升沿启动批量读取 |
| `bCancel` | `BOOL` | — | ⚠️ 待人工确认 |
| `eCommandPriority` | `E_DALIV2CommandPriority` | `eDALIV2CommandPriorityMiddle` | 优先级（建议 Low） |
| `nOptions` | `DWORD` | — | ⚠️ 待人工确认 |

### VAR_OUTPUT

```iecst
VAR_OUTPUT
    bBusy             : BOOL;
    bError            : BOOL;
    nErrorId          : UDINT;
    nCurrentShortAddr : BYTE;
END_VAR
```

| 名称 | 类型 | 说明（中文） |
|---|---|---|
| `bBusy` | `BOOL` | 读取中 |
| `bError` | `BOOL` | 出错 |
| `nErrorId` | `UDINT` | 错误号 |
| `nCurrentShortAddr` | `BYTE` | ⚠️ 待人工确认 |

### VAR_IN_OUT

```iecst
VAR_IN_OUT
    stCommandBuffer       : ST_DALIV2CommandBuffer;
    arrDALIDeviceSettings : ARRAY [0..63] OF ST_DALIV2DeviceSettings;
END_VAR
```

| 名称 | 类型 | 说明（中文） |
|---|---|---|
| `stCommandBuffer` | `ST_DALIV2CommandBuffer` | DALI 命令缓冲区结构；连到对应 KL68x1 通信 FB 的同名变量 |
| `arrDALIDeviceSettings` | `ARRAY [0..63] OF ST_DALIV2DeviceSettings` | ⚠️ 待人工确认 |


## 3. 行为说明

**整体流程**：本 FB 内部依次调用约 30 条 DALI 查询命令；每条间隔约 30 ms（受 DALI 总线时间限制）；总耗时约 1 秒。结果实时填入 `stSettings` VAR_IN_OUT。

**优先级**：建议 `Low`——读取期间约 30 条命令排队，用 Low 不影响主业务调光命令。

**典型应用**：（1）工程上线批量检查所有灯配置是否符合设计文档；（2）HMI 维护页显示某灯具完整状态；（3）现场调试灯具行为异常时查全部寄存器找原因。

**典型陷阱**：① 读取期间灯具被其它 FB 改配置 → 读到不一致的快照；② 广播无意义（多灯应答冲突）；③ `stSettings` 结构较大（约 30 字节），多个 FB 实例共用一个 stSettings 时要互斥访问。

## 4. 错误码 / 返回值

`nErrorId` 复用 `Tc2_DALI` 全库错误码（见 [`error_handling/Error_Codes.md`](../error_handling/Error_Codes.md)）。

| `nErrorId` | 含义 | 处理建议 |
|---|---|---|
| `16#0000` | 无错 | — |
| `16#0xxx` | 命令缓冲区溢出 | 缩短 `FB_KL68x1Communication` 任务节拍 |
| `16#1xxx` | 目标设备无响应 | 用 `FB_DALIV2QueryControlGearPresent` 确认设备在线 |
| `16#2xxx` | `nAddr` 越界或 `eAddrType` 不匹配 | 校验范围 |

## 5. 使用注意 / 常见坑

- 广播无意义——必须单灯。
- 总耗时约 1 秒，避免在主循环里同步等。
- `stSettings` 较大，多 FB 共用需互斥。

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_FB_DALIV2GetSettings.TcPOU`](../examples/P_Demo_FB_DALIV2GetSettings.TcPOU)
>
> 导入步骤：右键 PLC 项目下 POUs 文件夹 → Add → Existing Item → 选该文件 → OK

完整可运行版本（包含 KL68x1 通信链上下文）见配套 TcPOU 文件。

## 7. 业务场景与实际价值

- **场景**：工程上线验收——按设计文档校验所有灯具配置是否正确。本 FB 循环对每盏 short addr 调用，PLC 把读到的 stSettings 与设计文档对比，不符的列入整改清单。
- **价值**：替代逐个调 ~30 条 QueryXxx FB；一次调用拿全部配置，HMI / 验收效率高。
- **替代方案对比**：1) 逐个调 `FB_DALIV2QueryXxx`：代码冗长、效率低；2) **本 FB**：批量读取，标准方案。

## 8. 参考资料

- **PDF**：[TwinCAT_3_PLC_Lib_Tc2_DALI_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_DALI_EN.pdf) §4.1.1.1.3.1
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tcplclib_tc2_dali/142927643.html
- **相关**：[`FB_DALIV2GetSettingsSingleDevice`](FB_DALIV2GetSettingsSingleDevice.md)、[`FB_DALIV2SetSettings`](FB_DALIV2SetSettings.md)、`ST_DALIV2DeviceSettings`（DUT 结构）
