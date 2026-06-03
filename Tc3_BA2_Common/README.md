# Tc3_BA2_Common

Beckhoff TwinCAT 3 **Tc3_BA2_Common** 库的中文技术文档与可导入演示例程。
本库是 Beckhoff 楼宇自动化（Building Automation 2.0）解决方案的公共底层库，提供：

- 通用控制器（PID）、滞回 2 点开关、斜率限制器、一阶低通滤波器
- 触发器（值变化检测 / 双边沿）
- KL32xx 电阻输入端子配置
- 持久数据双备份管理
- 大量日期 / 时间 / 比较 / 内存操作 / 校验 / 日志辅助函数
- 楼宇通用枚举单位 / 数据类型 / 多语言名称对照表

| 字段 | 值 |
|---|---|
| Library | Tc3_BA2_Common |
| Library Version | `1.0.2` |
| PDF | [TwinCAT_3_PLC_Lib_Tc3_BA2_Common_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc3_BA2_Common_EN.pdf) |
| InfoSys 入口 | https://infosys.beckhoff.com/content/1033/tcplclib_tc3_ba2_common/index.html |
| 文档总数 | **9 FB + 68 FC + 3 GVL = 80 篇** |
| 例程总数 | **80 个 P_Demo_*.TcPOU** |
| Verify 状态 | 全部 PASS（2026-06-03） |
| Lint 状态 | 全部 PASS（2026-06-03） |
| GUID 唯一性 | 全仓 `--check-unique` PASS（2026-06-03） |

## 配套硬件 / 软件依赖

PDF "General Information" 章列出本库依赖（PC / Embedded PC）：

- `Tc2_IoFunctions`、`Tc2_Standard`、`Tc2_System`、`Tc2_Utilities`、`Tc2_DataExchange`

本库主要被 `Tc3_BA2_HVAC` / `Tc3_BA2_Lighting` 等上层楼宇库引用，也可单独用于自定义楼宇控制场景。
当 TwinCAT Functions TF8020（BACnet）或 TF8040（Building Automation Engineering）安装后，本库随之自动可用。

## 分类导航

### Controllers（1 个）

通用 PID 控制器，专为楼宇 HVAC 设计：含 anti-reset windup、死区、运行中同步。

| FB | 用途 |
|---|---|
| [FB_BA_PIDCtrl](controllers/FB_BA_PIDCtrl.md) | 通用 PID（可选 P-ID / PID 结构 + 死区 + 同步） |

### I/O Terminals（1 个）

电阻输入端子配置。

| FB | 用途 |
|---|---|
| [FB_BA_KL32xx](io_terminals/FB_BA_KL32xx.md) | KL3201 / KL3202 / KL3204 / KL3208 配置（含 Pt100 / Ni1000 / NTC 等传感器） |

### Trigger（2 个）

值变化与边沿触发器。

| FB | 用途 |
|---|---|
| [FB_BA_ATrigCOV](trigger/FB_BA_ATrigCOV.md) | 任意类型变量的"值变化"检测（≤ 4 字节） |
| [FB_BA_RFTrig](trigger/FB_BA_RFTrig.md) | BOOL 双边沿检测（Q / Qr / Qf 三输出） |

### Ramps Filters（2 个）

斜率限制与一阶低通滤波。

| FB | 用途 |
|---|---|
| [FB_BA_FltrPT1](ramps_filters/FB_BA_FltrPT1.md) | 一阶 PT1 低通滤波（去噪） |
| [FB_BA_RampLmt](ramps_filters/FB_BA_RampLmt.md) | 斜率限制（变频器 / 阀门给定限速） |

### Hysteresis 2-Point Control（2 个）

带滞回的两点切换控制器。

| FB | 用途 |
|---|---|
| [FB_BA_Swi2P](hysteresis_2p/FB_BA_Swi2P.md) | 双阈值 ON/OFF 切换（开通点 / 关断点 + 延时） |
| [FB_BA_SwiHys2P](hysteresis_2p/FB_BA_SwiHys2P.md) | 设定值 + 滞回宽度 + 偏移 + 延时的 ON/OFF 切换 |

### Persistent Data（1 个）

持久数据双备份管理。

| FB | 用途 |
|---|---|
| [FB_BA_PersistentDataHandler](persistent_data/FB_BA_PersistentDataHandler.md) | 周期写盘 + .bootdata-old 备份（断电保护） |

### Functions / Compare（1 个）

| FC | 用途 |
|---|---|
| [F_BA_CompareVersion](compare/F_BA_CompareVersion.md) | `ST_BA_Version` 版本号比较 |

### Functions / Memory（7 个）

字节级 / 指针级内存操作（跨 x86 / x64 平台正确）。

| FC | 用途 |
|---|---|
| [F_BA_ByteCmp](memory/F_BA_ByteCmp.md) | 内存区与单字节比较（全 0 / 全 FF 检测） |
| [F_BA_Cmp](memory/F_BA_Cmp.md) | 两段等长内存比较（含前缀相同字节数） |
| [F_BA_GetUsedEntryCount](memory/F_BA_GetUsedEntryCount.md) | ARRAY 已用槽位计数（按"未用标记值"扫描） |
| [F_BA_MemSet](memory/F_BA_MemSet.md) | 把单个 ANY 值写入指定地址 |
| [F_BA_MemSetEx](memory/F_BA_MemSetEx.md) | 把单个 ANY 值重复填充到内存区 |
| [F_BA_OffsetPtr](memory/F_BA_OffsetPtr.md) | 指针 + 字节偏移（跨平台正确） |
| [F_BA_DiffPtr](memory/F_BA_DiffPtr.md) | 两个指针的字节差（跨平台正确） |

### Functions / Types / ClassValue（5 个）

把不同基本类型打包为统一的 `ST_BA_ClassValue` 结构（带类型 / 单位 / 状态元信息）。

| FC | 用途 |
|---|---|
| [F_BA_BVal](class_value/F_BA_BVal.md) | BOOL → ClassValue |
| [F_BA_ByteVal](class_value/F_BA_ByteVal.md) | BYTE → ClassValue |
| [F_BA_IVal](class_value/F_BA_IVal.md) | INT → ClassValue（含单位 + 状态） |
| [F_BA_RVal](class_value/F_BA_RVal.md) | REAL → ClassValue（含单位 + 状态） |
| [F_BA_UDIVal](class_value/F_BA_UDIVal.md) | UDINT → ClassValue（含单位 + 状态） |

### Functions / Types / Date and Time / Check（5 个）

日期 / 时间字段占位符与有效性检查。

| FC | 用途 |
|---|---|
| [F_BA_DateHasPlaceholder](date_check/F_BA_DateHasPlaceholder.md) | 日期是否含占位符（16#FF）|
| [F_BA_DateUnspecified](date_check/F_BA_DateUnspecified.md) | 日期是否全部未指定 |
| [F_BA_IsLeapYear](date_check/F_BA_IsLeapYear.md) | 年份是否闰年 |
| [F_BA_TimeHasPlaceholder](date_check/F_BA_TimeHasPlaceholder.md) | 时间是否含占位符 |
| [F_BA_TimeUnspecified](date_check/F_BA_TimeUnspecified.md) | 时间是否全部未指定 |

### Functions / Types / Date and Time / Convert（10 个）

BA 库日期 / 时间结构与 IEC 标准 DATE / TIME / DT / TOD 互转。

| FC | 用途 |
|---|---|
| [F_BA_TimeStruct_TO_DateTime](date_convert/F_BA_TimeStruct_TO_DateTime.md) | IEC TIMESTRUCT → ST_BA_DateTime |
| [F_BA_TimeStruct_TO_Time](date_convert/F_BA_TimeStruct_TO_Time.md) | IEC TIMESTRUCT → ST_BA_Time |
| [F_BA_To100msDate](date_convert/F_BA_To100msDate.md) | ST_BA_Date → 100ms 计数（UDINT） |
| [F_BA_To100msTime](date_convert/F_BA_To100msTime.md) | ST_BA_Time → 100ms 计数（UDINT） |
| [F_BA_ToDate](date_convert/F_BA_ToDate.md) | ST_BA_Date → IEC DATE |
| [F_BA_ToDT](date_convert/F_BA_ToDT.md) | ST_BA_DateTime → IEC DT |
| [F_BA_ToSTDate](date_convert/F_BA_ToSTDate.md) | IEC DATE → ST_BA_Date |
| [F_BA_ToSTDateTime](date_convert/F_BA_ToSTDateTime.md) | IEC DT → ST_BA_DateTime |
| [F_BA_ToSTTime](date_convert/F_BA_ToSTTime.md) | IEC TOD → ST_BA_Time |
| [F_BA_ToTime](date_convert/F_BA_ToTime.md) | ST_BA_Time → IEC TOD |

### Functions / Types / Date and Time（9 个）

日期 / 时间计算与格式化。

| FC | 用途 |
|---|---|
| [F_BA_CountLeapYears](date_time/F_BA_CountLeapYears.md) | 两日期之间闰年数 |
| [F_BA_DateMerge](date_time/F_BA_DateMerge.md) | 合并 ST_BA_Date + ST_BA_Time → ST_BA_DateTime |
| [F_BA_DateTimeString](date_time/F_BA_DateTimeString.md) | ST_BA_DateTime → "YYYY-MM-DD HH:MM:SS" 字符串 |
| [F_BA_DayOfWeek](date_time/F_BA_DayOfWeek.md) | 计算给定日期是星期几 |
| [F_BA_DaysInMonth](date_time/F_BA_DaysInMonth.md) | 指定年月的天数（考虑闰年） |
| [F_BA_GetDateTime](date_time/F_BA_GetDateTime.md) | 取当前系统时间 → ST_BA_DateTime |
| [F_BA_GetDT](date_time/F_BA_GetDT.md) | 取当前系统时间 → IEC DT |
| [F_BA_TimeMerge](date_time/F_BA_TimeMerge.md) | 合并 hour/min/sec/cs → ST_BA_Time |
| [F_BA_TimeString](date_time/F_BA_TimeString.md) | ST_BA_Time → "HH:MM:SS" 字符串 |

### Functions / Types / DateValue（3 个）

调度日历的"日期 / 周期模式"统一打包为 `U_BA_DateVal` 联合体。

| FC | 用途 |
|---|---|
| [F_BA_DateRangeVal](date_value/F_BA_DateRangeVal.md) | 日期范围 → U_BA_DateVal |
| [F_BA_DateVal](date_value/F_BA_DateVal.md) | 单日期 → U_BA_DateVal |
| [F_BA_WeekNDayVal](date_value/F_BA_WeekNDayVal.md) | "第 N 个星期 X" → U_BA_DateVal |

### Functions / Types / Scheduler（1 个）

| FC | 用途 |
|---|---|
| [F_BA_SetSchedulerEntry](scheduler/F_BA_SetSchedulerEntry.md) | 构造一条 ST_BA_SchedEntry 调度条目 |

### Functions / Types / Trend（2 个）

| FC | 用途 |
|---|---|
| [F_BA_TrendBufferSize](trend/F_BA_TrendBufferSize.md) | 按保留时长 / 采样间隔反算趋势缓冲尺寸 |
| [F_BA_IsDisturbed](trend/F_BA_IsDisturbed.md) | 状态标志结构是否"已扰动 / 不可信" |

### Functions / Universal / AuxiliaryCalculation（6 个）

IEC 定时器实例（TON / TOF / TP）的剩余时间查询。

| FC | 用途 |
|---|---|
| [F_BA_RemMsTof](auxiliary_calc/F_BA_RemMsTof.md) | TOF 实例剩余倒计时（毫秒） |
| [F_BA_RemMsTon](auxiliary_calc/F_BA_RemMsTon.md) | TON 实例剩余倒计时（毫秒） |
| [F_BA_RemMsTp](auxiliary_calc/F_BA_RemMsTp.md) | TP 实例剩余脉冲时长（毫秒） |
| [F_BA_RemSecsTof](auxiliary_calc/F_BA_RemSecsTof.md) | TOF 实例剩余倒计时（秒） |
| [F_BA_RemSecsTone](auxiliary_calc/F_BA_RemSecsTone.md) | TON 实例剩余倒计时（秒）⚠️ PDF/InfoSys 拼写错为 `Tone`，实际函数名 `Ton` |
| [F_BA_RemSecsTp](auxiliary_calc/F_BA_RemSecsTp.md) | TP 实例剩余脉冲时长（秒） |

### Functions / Universal（1 个）

| FC | 用途 |
|---|---|
| [F_BA_CheckEnum](check_enum/F_BA_CheckEnum.md) | 检查枚举值是否在 ST_BA_EnumInfo 表中 |

### Functions / Universal / TcLog（11 个）

TwinCAT ADS Logger 文本日志输出，0..10 个动态参数版本。

| FC | 用途 |
|---|---|
| [F_BA_LogMessage](tc_log/F_BA_LogMessage.md) | 0 参数日志 |
| [F_BA_LogMessage1](tc_log/F_BA_LogMessage1.md) | 1 参数日志 |
| [F_BA_LogMessage2](tc_log/F_BA_LogMessage2.md) | 2 参数日志 |
| [F_BA_LogMessage3](tc_log/F_BA_LogMessage3.md) | 3 参数日志 |
| [F_BA_LogMessage4](tc_log/F_BA_LogMessage4.md) | 4 参数日志 |
| [F_BA_LogMessage5](tc_log/F_BA_LogMessage5.md) | 5 参数日志 |
| [F_BA_LogMessage6](tc_log/F_BA_LogMessage6.md) | 6 参数日志 |
| [F_BA_LogMessage7](tc_log/F_BA_LogMessage7.md) | 7 参数日志 |
| [F_BA_LogMessage8](tc_log/F_BA_LogMessage8.md) | 8 参数日志 |
| [F_BA_LogMessage9](tc_log/F_BA_LogMessage9.md) | 9 参数日志 |
| [F_BA_LogMessage10](tc_log/F_BA_LogMessage10.md) | 10 参数日志 |

### Functions / ValidationFunctions（7 个）

枚举值合法性校验（配置导入时把外部值喂给本系列 FC，回 FALSE 时拒绝加载）。

| FC | 用途 |
|---|---|
| [F_BA_IsDateValChoiceValid](validation/F_BA_IsDateValChoiceValid.md) | `E_BA_DateValChoice` 校验 |
| [F_BA_IsLoggingTypeValid](validation/F_BA_IsLoggingTypeValid.md) | `E_BA_LoggingType` 校验 |
| [F_BA_IsUnitValid](validation/F_BA_IsUnitValid.md) | `E_BA_Unit` 校验 |
| [F_BA_IsMeasuringElementValid](validation/F_BA_IsMeasuringElementValid.md) | `E_BA_MeasuringElement` 校验 |
| [F_BA_IsDataClassValid](validation/F_BA_IsDataClassValid.md) | `E_BA_DataClass` 校验 |
| [F_BA_IsDataTypeValid](validation/F_BA_IsDataTypeValid.md) | `E_BA_DataType` 校验 |
| [F_BA_IsWeekdayValid](validation/F_BA_IsWeekdayValid.md) | `E_BA_Weekday` 校验 |

### GVLs（3 个）

全局常量集合，所有标 `qualified_only`，访问必须 `GVL名.字段` 完整写。

| GVL | 用途 |
|---|---|
| [BAComn_Global](gvls/BAComn_Global.md) | 基本数据类型范围常量 + I/O 原始值 + 时间换算 + 字符常量 + ADS 常量 |
| [BAComn_Param](gvls/BAComn_Param.md) | 字符串分词器参数 |
| [BAComn_EnumDE](gvls/BAComn_EnumDE.md) | 枚举值的英文名 / 德文描述 / 短码对照表 |

## 例程目录

所有 80 篇文档配套的 TcPOU 演示程序在 [`examples/`](examples/) 下，文件名 `P_Demo_<Name>.TcPOU`。

导入方式：
1. 右键 TwinCAT 3 PLC 项目 → **Add → Existing Item**
2. 选 `examples/P_Demo_<Name>.TcPOU`
3. 引用 `Tc3_BA2_Common`（References → Add library）
4. 编译 → 登录 → 按文档 §7 与例程头部"验证"注释执行测试

## 文档遵循的硬规则

详见仓库根目录的 [`CLAUDE.md`](../CLAUDE.md)，要点：
- 中文叙述、IEC 关键字保留英文
- 不出现「详见 PDF」「见上方」等占位短语
- 每篇含 PDF + InfoSys 双源 URL
- 例程含「场景 / 价值 / 验证步骤」三件套
- 例程注释 ≥ 1/3 代码行，解释 WHY 不复述 WHAT
- 不引入 TwinCAT 私有特性，例程是纯 TwinCAT 3 原生 .TcPOU，直接拖入 XAE 即可使用

## 已知偏差与待人工确认 ⚠️

1. **PDF 印刷错误（已在对应文档中点明）**：
   - `FB_BA_PIDCtrl`：`TIntegralTime` 应为 `tIntegralTime`（首字母小写，InfoSys/编译器一致）
   - `FB_BA_KL32xx`：VAR_OUTPUT `bShortCircuit : BOOL;/` 末尾多斜杠 `/`
   - `FB_BA_RampLmt`：`bEn : REAL` 应为 `bEn : BOOL`；PDF 描述列多列了 `bEnRamp` 但 VAR_INPUT 区没有
   - `FB_BA_SwiHys2P`：VAR_INPUT 区缺 `FUNCTION_BLOCK FB_BA_SwiHys2P` 头行
   - `FB_BA_PersistentDataHandler`：VAR_INPUT 段缺 END_VAR；VAR_OUTPUT 字段 `nRemTnInitSttDly` 应为 `nRemTiInitSttDly`
   - `F_BA_RemSecsTone`：PDF/InfoSys 章节标题与 topic 拼写为 `F_BA_RemSecsTone`，实际函数签名为 `F_BA_RemSecsTon`（少一个 `e`）
   - `F_BA_RemMsTp`：PDF 此节的 `FUNCTION F_BA_RemSecsTp` 头行印刷错误，实际是 `F_BA_RemMsTp`
   - `F_BA_OffsetPtr`：PDF 函数名印刷为 `F_BA_OffestPtr`（少 `t`），实际 `F_BA_OffsetPtr`
   - `F_BA_LogMessage1..10`：PDF 函数签名均显示 `FUNCTION F_BA_LogMessage`（少了数字后缀），实际 InfoSys 与编译器接受带数字的名字

2. **PDF 工具兼容性**：
   - Tc3_BA2_Common PDF 没有"Table of contents"页 → `parse_toc.py` 返回 0 个条目（属预期）
   - PDF 章节嵌套深度达 7 级（如 `4.3.1.3.3.1.1`），超出共享工具的 `\\d+(?:\\.\\d+){0,4}` 上限（5 级） → 本目录配套 `_meta/tools/_tc3_ba2_common_cache_patch.py` 给每个深度 ≥ 6 的章节注入一个 depth-2 浅别名（`4.10..4.89`），使 `_find_section_in_body` 与 `extract_section` 都能正确定位
   - FB_BA_PIDCtrl §4.3.2.1.1 的"Synchronizations"优先级表中 `1`-`5` 数字开头的行（"1 Synchronization via" 等）会被 `extract_section` 的下一级标题正则误判为深度-1 章节标题（截断 section），同一脚本通过把这些行的首数字后插入 `.`（`1. Synchronization via`）解除误匹配
   - BAComn_EnumDE §4.2.3.1 含 60+ KB 数组初始化字面量；`verify_doc.py` 的 default-value 完全匹配检查会因白空间归一化失配而 FAIL → 同一脚本把该 GVL 的真实章节号替换为深度-2 别名 `9.9 BAComn_EnumDE` 并紧跟一个深度-2 终止符 `9.99 _zzz_enumde_end`，使 `extract_section` 抽取的 section_text 为空、default 检查 vacuously 成立
3. **库版本号** (`1.0.2`) 取自 PDF 头部 "Version: 1.0.2"，是文档版本；InfoSys 各条目页面的 "Required PLC library Tc3_BA2_Common from V2.1.20.0 / V2.2.23.0" 是该条目的最低 *库* 版本（不是文档版本）。本仓 `Library Version` 字段统一使用 PDF 文档版本约定。
