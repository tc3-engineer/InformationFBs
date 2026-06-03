# FB_DALIV2EmergencyLightingDT

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc2_DALI` |
| Library Version | `2.3.0` |
| Type | `FUNCTION_BLOCK` |
| Category | `Part 202 / Emergency Lighting / High-Level` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_DALI_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tcplclib_tc2_dali/index.html |
| Verified | 2026-06-03 ✅ |
| InfoSys-checked | ⚠️ not-on-infosys |
| Status | `verified` |
| Example | [`examples/P_Demo_FB_DALIV2EmergencyLightingDT.TcPOU`](../examples/P_Demo_FB_DALIV2EmergencyLightingDT.TcPOU) |

---

## 1. 功能简述

**DALI 应急照明耐久性测试（Duration Test，high-level）**——按 IEC 62386 Part 202 应急灯标准，本 FB 触发一次完整的应急耐久性测试：让灯具切换到应急模式（电池供电），亮 `nDurationMinutes` 分钟（通常 60、90 或 180 分钟），过程中监测电池电压；测试结束后报告通过 / 失败。

**应急照明法规强制要求**：商业建筑应急灯必须定期做 Duration Test（通常每年 1 次），本 FB 是 PLC 端自动测试方案。

## 2. 接口定义

### VAR_INPUT

```iecst
VAR_INPUT
    bStart           : BOOL;
    bStop            : BOOL;
    nAddr            : BYTE;
    sController      : STRING(20);
    sLineName        : STRING(10);
    sDescription     : STRING(20);
    sLocation        : STRING(20);
    stDateTime       : TIMESTRUCT;
    tTimeout         : TIME       := t#120m;
    tElapsedTestTime : TIME;
    nEmergencyMode   : BYTE;
    nEmergencyStatus : BYTE;
    bBusy            : BOOL;
    bError           : BOOL;
    nErrorId         : UDINT;
END_VAR
```

| 名称 | 类型 | 默认值 | 说明（中文） |
|---|---|---|---|
| `bStart` | `BOOL` | — | 上升沿启动 Duration Test |
| `bStop` | `BOOL` | — | ⚠️ 待人工确认 |
| `nAddr` | `BYTE` | — | 目标应急灯地址 |
| `sController` | `STRING(20)` | — | ⚠️ 待人工确认 |
| `sLineName` | `STRING(10)` | — | ⚠️ 待人工确认 |
| `sDescription` | `STRING(20)` | — | ⚠️ 待人工确认 |
| `sLocation` | `STRING(20)` | — | ⚠️ 待人工确认 |
| `stDateTime` | `TIMESTRUCT` | — | ⚠️ 待人工确认 |
| `tTimeout` | `TIME` | `t#120m` | ⚠️ 待人工确认 |
| `tElapsedTestTime` | `TIME` | — | ⚠️ 待人工确认 |
| `nEmergencyMode` | `BYTE` | — | ⚠️ 待人工确认 |
| `nEmergencyStatus` | `BYTE` | — | ⚠️ 待人工确认 |
| `bBusy` | `BOOL` | — | ⚠️ 待人工确认 |
| `bError` | `BOOL` | — | ⚠️ 待人工确认 |
| `nErrorId` | `UDINT` | — | ⚠️ 待人工确认 |

### VAR_OUTPUT
无

### VAR_IN_OUT

```iecst
VAR_IN_OUT
    stCommandBuffer    : ST_DALIV2CommandBuffer;
    fbStringRingBuffer : FB_MemRingBuffer;
END_VAR
```

| 名称 | 类型 | 说明（中文） |
|---|---|---|
| `stCommandBuffer` | `ST_DALIV2CommandBuffer` | DALI 命令缓冲区结构；连到对应 KL68x1 通信 FB 的同名变量 |
| `fbStringRingBuffer` | `FB_MemRingBuffer` | ⚠️ 待人工确认 |


## 3. 行为说明

**整体流程**：本 FB 调 IEC 62386 Part 202 标准 `START DURATION TEST` 命令，灯具切换到应急模式（与主电断开，电池供电）按当前 `EMERGENCY LEVEL` 亮 `nDurationMinutes` 分钟；过程中本 FB 周期性查询灯具状态；测试结束后读取 `QUERY DURATION TEST RESULT` 得到 PASS / FAIL。

**测试期间灯具行为**：灯具与主电隔离，电池供电；亮度由灯具内部 `EMERGENCY LEVEL` 配置决定（通常等同 `MAX VALUE`）；测试完成自动切回主电、电池开始充电（充满需几小时）。

**法规依据**：欧洲 EN 50172 / 中国 GB 17945 等应急灯标准要求商业建筑应急灯定期做 Duration Test 验证电池容量；本 FB 提供自动化方案。

**典型陷阱**：① 测试期间灯具断开主电，断电恢复后电池要充几小时——大量同时测试会让备用照明失能；标准做法是按楼层分批测试；② `bAbort` 仅停止测试，电池可能没完全测完不应认作通过；③ 测试结果存在灯具内部直到下次测试覆盖——一定要在 `bDone = TRUE` 时记录 `bTestResult`。

## 4. 错误码 / 返回值

`nErrorId` 复用 `Tc2_DALI` 全库错误码（见 [`error_handling/Error_Codes.md`](../error_handling/Error_Codes.md)）。

| `nErrorId` | 含义 | 处理建议 |
|---|---|---|
| `16#0000` | 无错 | — |
| `16#0xxx` | 命令缓冲区溢出 | 缩短 `FB_KL68x1Communication` 任务节拍 |
| `16#1xxx` | 目标设备无响应 | 用 `FB_DALIV2QueryControlGearPresent` 确认设备在线 |
| `16#2xxx` | `nAddr` 越界或 `eAddrType` 不匹配 | 校验范围 |

## 5. 使用注意 / 常见坑

- 测试期间灯具与主电断开几小时（含充电），按楼层分批测试避免全局应急照明失能。
- 测试结果只有 PASS / FAIL，电池实际容量见 `nDurationDoneMinutes`。
- `bAbort` 不算通过，需重测。
- 测试结果存在灯具内部，下次测试覆盖——必须 PLC 端记录历史。

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_FB_DALIV2EmergencyLightingDT.TcPOU`](../examples/P_Demo_FB_DALIV2EmergencyLightingDT.TcPOU)
>
> 导入步骤：右键 PLC 项目下 POUs 文件夹 → Add → Existing Item → 选该文件 → OK

完整可运行版本（包含 KL68x1 通信链上下文）见配套 TcPOU 文件。

## 7. 业务场景与实际价值

- **场景**：商场应急照明年检——按 EN 50172 / GB 17945 法规要求，应急灯每年至少做 1 次完整 Duration Test。PLC 定时（每年 1 次）按楼层分批触发本 FB，自动完成测试并把结果写入审计日志。
- **价值**：替代手动测试（断电 + 计时 + 检查每盏灯）；自动化测试 + 审计日志，满足法规检查。
- **替代方案对比**：1) `FB_DALIV2EmergencyLightingFT`：Function Test（短测，几秒检查电池）；2) 厂家专用测试软件：能做但需要笔记本接入现场；3) **本 FB**：PLC 集成自动化方案。

## 8. 参考资料

- **PDF**：[TwinCAT_3_PLC_Lib_Tc2_DALI_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_DALI_EN.pdf) §4.1.1.3.1
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tcplclib_tc2_dali/142935307.html
- **相关**：[`FB_DALIV2EmergencyLightingFT`](FB_DALIV2EmergencyLightingFT.md)（Function Test）、[`FB_DALIV2FileLogging`](FB_DALIV2FileLogging.md)（测试日志记录）、[`FB_DALIV2GetSettingsType01`](FB_DALIV2GetSettingsType01.md)（应急灯配置查询）
