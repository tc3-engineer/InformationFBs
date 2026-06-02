# FB_FileTimeToTzSpecificLocalTime

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc2_Utilities` |
| Library Version | `2.18.2` |
| Type | `FUNCTION_BLOCK` |
| Category | `[obsolete]` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_Utilities_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tcplclib_tc2_utilities/34988683.html |
| Verified | 2026-05-12 ✅ |
| InfoSys-checked | ✅ 2026-05-12 |
| Status | `verified · deprecated` |
| Example | [`examples/P_Demo_FB_FileTimeToTzSpecificLocalTime.TcPOU`](../examples/P_Demo_FB_FileTimeToTzSpecificLocalTime.TcPOU) |

---

## 1. 功能简述

⚠️ **本 FB 已弃用**。PDF 与 InfoSys 都明确写 "Obsolete function — use the function block `FB_FileTime64ToTzSpecificLocalTime` instead"。**新代码请用 `FB_FileTime64ToTzSpecificLocalTime`**。

`FB_FileTimeToTzSpecificLocalTime` 把 32 位 `T_FILETIME` 格式的 UTC 时间根据提供的时区信息转换为本地时间（仍是 `T_FILETIME` 格式）。同时输出附加的时区 ID 与"B 时间"标志，专门处理夏令时与标准时切换造成的"局部时间重复"现象。

被弃用的原因：底层时间戳类型 `T_FILETIME` 是 32 位结构，对未来 Y2038 类问题以及更精细的纳秒级时间分辨率不足。新 FB `FB_FileTime64ToTzSpecificLocalTime` 使用 64 位 `T_FILETIME64` 格式，时间范围更广、精度更高。

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
| `in` | `T_FILETIME` | 待转换的 UTC 时间（FILETIME 格式）。**必须连续单调递增**——时间跳变会导致 FB 内部"上次输出"缓存失效，输出错误（PDF 明确警告） |
| `tzInfo` | `ST_TimeZoneInformation` | 操作系统当前的时区信息结构体。常用 `WEST_EUROPE_TZI` 常量；其他时区可通过 `FB_GetTimeZoneInformation` 从 OS 取 |

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
| `out` | `T_FILETIME` | 转换后的本地时间（FILETIME 格式） |
| `eTzID` | `E_TimeZoneID` | 时区 ID：`eTimeZoneID_Daylight`（夏令时） / `eTimeZoneID_Standard`（标准时） / `eTimeZoneID_Unknown`（启动初始值） |
| `bB` | `BOOL` | "B 时间"标志：本地时间因夏令时切换出现"重复"区间（如 02:00 → 02:59 出现两次）时，第二次（标准时那次）期间 `bB := TRUE`。重复区间过后自动复位为 `FALSE`。区分歧义时间的关键标志 |

### VAR_IN_OUT

无。

### 动作（Action）

| 名称 | 说明 |
|---|---|
| `A_Reset()` | 调用此动作把 FB 内部"上次输出"缓存和输出全部清零。在时间源切换或检测到时间跳变时调用，避免缓存导致的转换错误 |

## 3. 行为说明

**算法本质**：把 UTC 时间加上时区偏移得到本地时间。但本地时间在夏令时切换时刻**不是连续的**：

1. **从夏令时回退到标准时**（如 10 月最后一周日凌晨 03:00 回退到 02:00）：本地时间 02:00–02:59 区间会出现**两次**。FB 用内部缓存的"上次输出"判断现在是第一次（夏令时段 `bB = FALSE`、`eTzID = Daylight`）还是第二次（标准时段 `bB = TRUE`、`eTzID = Standard`）。
2. **从标准时切换到夏令时**（如 3 月最后一周日凌晨 02:00 跳到 03:00）：本地时间 02:00–02:59 区间被**跳过**，不会产生输出歧义；FB 直接按新时区给出 03:00。

**为什么 `in` 必须单调递增**：FB 通过"当前 `in` 与上次 `in` 比较"判断是否跨越切换时刻、是否进入重复区。`in` 时间跳变 / 倒退 / 重复输入会让缓存判断失误，输出错误的本地时间。**`in` 必须连续递增**——这就是 PDF 强调"only suitable for continuous UTC timestamp information"的意思。

**初始化**：FB 第一次被调用时 `eTzID := eTimeZoneID_Unknown`（默认值），第一个 `in` 的转换从这里开始建缓存。

**`A_Reset()` 用途**：
- 时间源切换（如从手动设置切到 NTP 同步）
- 检测到时间跳变后清缓存
- 跨年初始化（理论上不必要但稳妥）

**单 PLC 周期同步完成**：FB 不做 ADS 通讯，仅做时区算术，调用即返回。

## 4. 错误码 / 返回值

本 FB 没有 `bError` / `nErrorId` 输出。所有"错误"都表现为 `out` / `eTzID` 输出不符合预期。

PDF 未列出错误条件清单，但可推断的失败场景：
- `in` 时间跳变 / 倒退 → `out` 输出错乱，需调 `A_Reset()` 重置
- `tzInfo` 是无效 / 零值结构 → `out` 等于 `in`（无偏移），等效于"不做时区转换"
- 时区数据库与 OS 不一致（如手动构造 `tzInfo`）→ DST 切换时刻判断错误

## 5. 使用注意 / 常见坑

- **本 FB 已弃用**：新代码请用 `FB_FileTime64ToTzSpecificLocalTime`。本文档为旧工程维护保留。
- **`in` 必须连续单调递增** —— 这是头号陷阱。手动调时钟、从 NTP 跳变、跨设备拷贝时间值都会破坏单调性。检测到时间不连续后必须调 `A_Reset()`。
- **`bB` 一年只可能在切换点 TRUE 几小时** —— 业务侧把它当"夏令时切换检测信号"用是有意义的。
- **不要把这个 FB 用于"显示用本地时间"以外的目的** —— PDF 明确建议时间戳本身用 UTC，本地时间仅在可视化层做最终转换。**不要**把转换结果存进日志或数据库，会让 DST 周年发生时数据出现重复 / 跳跃。
- **跨日 / 跨年时不必额外处理** —— FB 内部已正确处理。
- **`tzInfo` 通常用现成常量**：`WEST_EUROPE_TZI` 覆盖德 / 法 / 中欧；其他地区可调 `FB_GetTimeZoneInformation` 从 OS 读取。
- **`A_Reset()` 调用语法**：`fbConv.A_Reset();` 一行——不是 `fbConv.A_Reset := TRUE;`。Action 是方法式调用。
- **不要在 PLC 调度抖动期间频繁触发本 FB**：抖动会让"上次 in"与"当前 in"差变小甚至倒序（同周期重入），缓存逻辑混乱。

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_FB_FileTimeToTzSpecificLocalTime.TcPOU`](../examples/P_Demo_FB_FileTimeToTzSpecificLocalTime.TcPOU)（TwinCAT 3 原生 .TcPOU，可直接拖入 XAE 的 PLC POUs 文件夹）
>
> 导入步骤：右键 PLC 项目下 POUs 文件夹 → Add → Existing Item → 选该文件 → OK
> 详见 [`examples/README.md`](../examples/README.md)

```iecst
// 场景：维护一个 TC2 时代的批次报表系统：内部时间戳全部以 UTC FILETIME 存储，
//       HMI 显示时按西欧时区转成本地时间。本 FB 是这套旧系统转时区的标准工具。
//
// 价值：保留旧报表系统的时区转换；要做新工程请改用 FB_FileTime64ToTzSpecificLocalTime。
//
// 验证：登录后给 ftUtcInput 写一个固定 UTC FILETIME（例如 2026 夏季某时刻），
//       观察 ftLocalOutput 的小时数应比 UTC 多 2（CEST 是 UTC+2）；冬季的同样
//       UTC 时刻经转换应只多 1 小时（CET 是 UTC+1）。可通过 DT_TO_FILETIME 等
//       辅助函数构造测试输入。
PROGRAM P_Demo_FB_FileTimeToTzSpecificLocalTime
VAR
    fbConvertUtcToLocal   : FB_FileTimeToTzSpecificLocalTime;
    ftUtcInput            : T_FILETIME;
    ftLocalOutput         : T_FILETIME;
    eDstStatus            : E_TimeZoneID;
    bInBTime              : BOOL;            // 切换重复区第二次为 TRUE
    bDoResetCache         : BOOL := FALSE;   // 在线写 TRUE 一次以清缓存
END_VAR

// 用 WEST_EUROPE_TZI 常量做时区数据
fbConvertUtcToLocal(
    in     := ftUtcInput,
    tzInfo := WEST_EUROPE_TZI,
    out    => ftLocalOutput,
    eTzID  => eDstStatus,
    bB     => bInBTime
);

// 时间源跳变后调 Reset 清缓存
IF bDoResetCache THEN
    bDoResetCache := FALSE;
    fbConvertUtcToLocal.A_Reset();
END_IF
```

## 7. 业务场景与实际价值

- **场景**：TC2 时代旧报表 / 旧 HMI 的时区转换。批次记录、报警时间戳等用 UTC 存储，显示时转本地。
- **价值**：维护性——让旧工程继续工作，不强迫整体迁移到 64 位时间格式。
- **替代方案对比**：
  - **新工程**：必须用 `FB_FileTime64ToTzSpecificLocalTime`（64 位时间，更大范围、更高精度）
  - **混合工程**：本 FB 处理旧 32 位时间戳，新逻辑用 64 位版本，两套并行
  - **不做时区转换**：所有时间一律 UTC——这是工业现场最推荐的做法，本地化只在 HMI / 报表显示层做一次

## 8. 参考资料

- **PDF**：[TwinCAT_3_PLC_Lib_Tc2_Utilities_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_Utilities_EN.pdf) §3.1.3
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tcplclib_tc2_utilities/34988683.html
- **替代 FB**：`FB_FileTime64ToTzSpecificLocalTime`（64 位时间格式）
- **相关类型**：`T_FILETIME`、`ST_TimeZoneInformation`、`E_TimeZoneID`、`WEST_EUROPE_TZI`
- **配对 FB**：[`FB_TzSpecificLocalTimeToFileTime`](FB_TzSpecificLocalTimeToFileTime.md)（反向转换，也已弃用）
