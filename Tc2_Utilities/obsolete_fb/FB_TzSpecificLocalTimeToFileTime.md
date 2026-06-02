# FB_TzSpecificLocalTimeToFileTime

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc2_Utilities` |
| Library Version | `2.18.2` |
| Type | `FUNCTION_BLOCK` |
| Category | `[obsolete]` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_Utilities_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tcplclib_tc2_utilities/35027083.html |
| Verified | 2026-05-12 ✅ |
| InfoSys-checked | ✅ 2026-05-12 |
| Status | `verified · deprecated` |
| Example | [`examples/P_Demo_FB_TzSpecificLocalTimeToFileTime.TcPOU`](../examples/P_Demo_FB_TzSpecificLocalTimeToFileTime.TcPOU) |

---

## 1. 功能简述

⚠️ **本 FB 已弃用**。PDF 与 InfoSys 都明确写 "Obsolete function — use the function block `FB_TzSpecificLocalTimeToFileTime64` instead"。**新代码请用 `FB_TzSpecificLocalTimeToFileTime64`**。

`FB_TzSpecificLocalTimeToFileTime` 是 [`FB_FileTimeToTzSpecificLocalTime`](FB_FileTimeToTzSpecificLocalTime.md) 的反向操作：把本地时间（`T_FILETIME` 格式）按提供的时区信息转换为 UTC 时间（仍是 `T_FILETIME` 格式）。同样输出附加的时区 ID 与"B 时间"标志，专门处理夏令时切换造成的"本地时间重复"歧义。

被弃用的原因与正向 FB 一致：32 位 `T_FILETIME` 类型时间范围 / 精度受限。新 FB `FB_TzSpecificLocalTimeToFileTime64` 用 64 位 `T_FILETIME64`。

注意：PDF 明确建议**工程实践中尽量用 UTC 时间做时间戳**，只在最终展示层做本地化——这样可以**完全避开**本 FB 的反向转换需求。本 FB 只有在"用户输入了本地时间，要落库 UTC"这类罕见场景才用得上。

## 2. 接口定义

### VAR_INPUT

```iecst
VAR_INPUT
    in     : T_FILETIME;
    tzInfo : ST_TimeZoneInformation;
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `in` | `T_FILETIME` | 待转换的本地时间（FILETIME 格式）。**必须连续单调递增**——但可以包含夏令时切换造成的"跳变"（FB 内部能正确识别） |
| `tzInfo` | `ST_TimeZoneInformation` | 操作系统当前的时区信息结构体。常用 `WEST_EUROPE_TZI` |

### VAR_OUTPUT

```iecst
VAR_OUTPUT
    out   : T_FILETIME;
    eTzID : E_TimeZoneID := eTimeZoneID_Unknown;
    bB    : BOOL;
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `out` | `T_FILETIME` | 转换后的 UTC 时间（FILETIME 格式）。是连续单调的（UTC 没有 DST 跳变） |
| `eTzID` | `E_TimeZoneID` | 时区 ID：`eTimeZoneID_Daylight` / `eTimeZoneID_Standard` / `eTimeZoneID_Unknown` |
| `bB` | `BOOL` | "B 时间"标志：本地时间因 DST 回退出现重复区间时，第二次（标准时段）期间为 `TRUE` |

### VAR_IN_OUT

无。

### 动作（Action）

| 名称 | 说明 |
|---|---|
| `A_Reset()` | 把 FB 内部"上次输出"缓存和输出全部清零。在时间源切换或检测到时间跳变时调用 |

## 3. 行为说明

**算法本质**：本地时间减去时区偏移得到 UTC。难点在于本地时间在 DST 切换时是**不连续**且**有歧义**的：

1. **从夏令时回退到标准时**：本地时间 02:00–02:59 重复出现两次。本 FB 通过内部缓存的"上次输出"判断这次输入是第一次（夏令时段 `bB = FALSE`、对应 UTC-2）还是第二次（标准时段 `bB = TRUE`、对应 UTC-1）。
2. **从标准时切换到夏令时**：本地时间 02:00–02:59 被跳过。这段时间不存在合法的本地时间输入；若 `in` 落入这区间 PDF 未明说行为 ⚠️——保守假设输出可能错乱。

**单调性要求**：`in` 必须连续递增。允许 DST 跳变（FB 能处理），但不允许任意跳变 / 倒退。检测到时间源换了请调 `A_Reset()`。

**反向转换的固有歧义**：DST 回退时段的本地时间 02:30 既可能对应 UTC 00:30（夏令时段）也可能对应 UTC 01:30（标准时段）。本 FB 用"时间在序列中的位置"决定属于哪个——前提是 `in` 连续递增。要"任意时刻给一个本地时间问对应的 UTC"，本 FB 力不能及（理论上是不可解的歧义）。

**单 PLC 周期同步完成**：无 ADS 通讯，纯算术。

## 4. 错误码 / 返回值

本 FB 无 `bError` / `nErrorId` 输出。所有问题表现为 `out` 输出不正确（时间偏差 1 小时即可能是 DST 误判）或 `eTzID` 错误。

可能的失败场景：
- `in` 时间跳变 → `out` 错乱，需 `A_Reset()`
- `in` 落入 DST 跳过区间（不存在的本地时间）→ PDF 未明说 ⚠️
- `tzInfo` 无效 → 输出等于输入（不做转换）

## 5. 使用注意 / 常见坑

- **本 FB 已弃用**：新代码请用 `FB_TzSpecificLocalTimeToFileTime64`。本文档为旧工程维护保留。
- **`in` 必须连续单调递增**：与正向 FB 一致，时间不连续会让缓存判断失败。
- **DST 跳过区间的本地时间是"不存在的"**：03:00 切换那天 02:00–02:59 不存在，给它做反向转换没有合法 UTC 对应。**业务侧应在 HMI 输入层就拦掉这种输入**。
- **更推荐的做法**：所有时间戳用 UTC 存储与传递，HMI 只在最终显示层用正向 FB 转本地——这样根本不需要本 FB。
- **`bB` 标志**：仅在 DST 回退重复时段出现 `TRUE`。可作"夏令时切换检测"信号。
- **`A_Reset()`**：方法式调用 `fb.A_Reset();`，不是赋值。
- **`tzInfo` 用现成常量**：`WEST_EUROPE_TZI` 或通过 `FB_GetTimeZoneInformation` 从 OS 读取。
- **不要把转换结果存回 32 位 FILETIME 长时间归档**：未来需要纳秒精度或 2038 之后的时间会撞类型上限。归档建议用 64 位时间或 ISO8601 字符串。

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_FB_TzSpecificLocalTimeToFileTime.TcPOU`](../examples/P_Demo_FB_TzSpecificLocalTimeToFileTime.TcPOU)（TwinCAT 3 原生 .TcPOU，可直接拖入 XAE 的 PLC POUs 文件夹）
>
> 导入步骤：右键 PLC 项目下 POUs 文件夹 → Add → Existing Item → 选该文件 → OK
> 详见 [`examples/README.md`](../examples/README.md)

```iecst
// 场景：TC2 时代的旧 HMI 维护工程：操作员在 HMI 输入"启动时间"按本地时间录入，
//       但内部存储要 UTC（避免 DST 引起的日历问题）。本 FB 在 HMI 提交时把
//       本地时间转换为 UTC 后入库。
//
// 价值：保留旧 HMI 输入流程；新工程一律推荐 HMI 也用 UTC，根本不必反向转换。
//
// 验证：登录后构造一个 CEST 夏令时本地时间（如 2026-07-01 14:00 CEST）写入
//       ftLocalInput，观察 ftUtcOutput 应比输入早 2 小时（UTC 12:00）；
//       构造冬季 CET 本地时间（如 2026-01-01 14:00 CET）观察 ftUtcOutput 应
//       比输入早 1 小时（UTC 13:00）。
PROGRAM P_Demo_FB_TzSpecificLocalTimeToFileTime
VAR
    fbConvertLocalToUtc   : FB_TzSpecificLocalTimeToFileTime;
    ftLocalInput          : T_FILETIME;
    ftUtcOutput           : T_FILETIME;
    eDstStatus            : E_TimeZoneID;
    bInBTime              : BOOL;
    bDoResetCache         : BOOL := FALSE;
END_VAR

fbConvertLocalToUtc(
    in     := ftLocalInput,
    tzInfo := WEST_EUROPE_TZI,
    out    => ftUtcOutput,
    eTzID  => eDstStatus,
    bB     => bInBTime
);

IF bDoResetCache THEN
    bDoResetCache := FALSE;
    fbConvertLocalToUtc.A_Reset();
END_IF
```

## 7. 业务场景与实际价值

- **场景**：TC2 旧 HMI 工程的"本地时间录入 → UTC 落库"路径；极罕见用法。
- **价值**：维护性。
- **替代方案对比**：
  - **强烈推荐**：HMI 也用 UTC 输入 / 显示，根本不做反向转换——避开所有 DST 歧义
  - **新工程必须本地输入**：用 `FB_TzSpecificLocalTimeToFileTime64`
  - **旧工程**：本 FB 仍可用，但建议把"本地输入"改造成"UTC 输入"作为升级路径

## 8. 参考资料

- **PDF**：[TwinCAT_3_PLC_Lib_Tc2_Utilities_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_Utilities_EN.pdf) §3.1.4
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tcplclib_tc2_utilities/35027083.html
- **替代 FB**：`FB_TzSpecificLocalTimeToFileTime64`（64 位时间格式）
- **相关类型**：`T_FILETIME`、`ST_TimeZoneInformation`、`E_TimeZoneID`、`WEST_EUROPE_TZI`
- **配对 FB**：[`FB_FileTimeToTzSpecificLocalTime`](FB_FileTimeToTzSpecificLocalTime.md)（正向转换，也已弃用）
