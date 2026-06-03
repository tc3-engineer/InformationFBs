# M_SetAlarm

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc3_PackML_V3` |
| Library Version | `1.0.0` |
| Type | `METHOD` |
| Category | `FB_PMLAdminAlarm` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc3_PackML_V3_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tcplclib_tc3_packml_v3/16004004235.html |
| Verified | 2026-06-03 ✅ |
| InfoSys-checked | ⚠️ not-on-infosys |
| Status | `verified` |
| Example | [`examples/P_Demo_M_SetAlarm.TcPOU`](../examples/P_Demo_M_SetAlarm.TcPOU) |

---

## 1. 功能简述

`FB_PMLAdminAlarm.M_SetAlarm()` 把一条 alarm 写入 PackML Admin-Tag 的 `Alarm[]` 数组：把空位的 `Trigger` 置 TRUE、从 `Admin.PlcDateTime` 读取并写入 `Alarm[].DateTime`，其余字段（`Id` / `Value` / `Message` / `Category`）从入参 `stAlarm` 拷贝。返回 TRUE 表示写入成功。

**V3 与 V2 的差异**：方法签名结构相同，但 V3 的事件结构类型从 `ST_Alarm`（V2 命名）改为 `ST_PMLEvent`（V3 标准命名）。语义不变。

为了让时间戳有效，主程序必须周期调用 `FB_PMLAdminTime`。

## 2. 接口定义

### VAR_INPUT

```iecst
METHOD M_SetAlarm : BOOL
VAR_IN_OUT
  stAdmin          : ST_PMLa;
END_VAR
VAR_INPUT
  stAlarm          : ST_PMLEvent;
END_VAR
```

| 名称 | 类型 | 出现于 | 说明 |
|---|---|---|---|
| `stAdmin` | `ST_PMLa` | `VAR_IN_OUT` | PackML 管理 PackTag。方法读取 `PlcDateTime` 作时间戳、把 alarm 写入 `Alarm[]` 空槽位 |
| `stAlarm` | `ST_PMLEvent` | `VAR_INPUT` | 输入 alarm 结构。调用方填好 `Id` / `Value` / `Message` / `Category`；`Trigger` / `DateTime` / `AckDateTime` 由方法内部填 |

### VAR_OUTPUT

无（返回值 BOOL 通过 METHOD 返回类型给出）。

## 3. 行为说明

`M_SetAlarm` 实现 alarm 上报的标准流程：

1. 在 `stAdmin.Alarm[]` 数组中找第一个 `Trigger = FALSE` 的空槽位（未触发的位置）；
2. 把 `stAlarm.Id` / `Value` / `Message` / `Category` 拷贝到该槽位；
3. 该槽位的 `Trigger := TRUE`；
4. 该槽位的 `DateTime := stAdmin.PlcDateTime`；
5. 返回 `TRUE` 表示写入成功。

**数组满时行为**（PDF 未明确细节）：根据 PackML 标准的环形数组约定，最老一项被覆盖；具体覆盖策略 PDF 没明确（⚠️ 实测）。

**调用语义**：调用即执行——不是上升沿触发。每次想加一条 alarm 就调一次本方法。如果在每周期都调（不带门控），会立刻把数组填满并不停顶替。**正确做法是只在故障检测的上升沿调一次**。

**时间戳依赖**：`stAdmin.PlcDateTime` 由 `FB_PMLAdminTime` 周期填充。如果 `FB_PMLAdminTime` 没在主任务里调用，时间戳全部为 0 或上电初值。

**返回值含义**：PDF 说返回 TRUE = 写入成功。FALSE 的可能原因（PDF 未列）⚠️：数组满+覆盖策略禁止覆盖；输入参数无效（Id=0）等。

## 4. 错误码 / 返回值

| 返回值 | 含义 | 处理建议 |
|---|---|---|
| `TRUE` | 写入成功 | 继续业务 |
| `FALSE` | 写入失败 | 检查 stAdmin 初始化、PlcDateTime 是否更新、数组是否满；PDF 未列具体原因（⚠️）|

## 5. 使用注意 / 常见坑

- **必须配合 `FB_PMLAdminTime` 周期调用**——否则 DateTime 全是初值。
- **只在故障上升沿调一次**——每周期调会覆盖数组；正确做法用 R_TRIG 包裹。（工程经验补充）
- `stAlarm.Id` 建议用项目级枚举管理（如 `eAlarmId_TempHigh := 1001`），便于 HMI/MES 反查。（工程经验补充）
- `stAlarm.Message` 是 `STRING`，默认 80 字符——超长会被截断。
- `stAlarm.Category` 用于 HMI 按严重度分类显示，建议 1=Critical / 2=Major / 3=Minor 之类（ISA-18.2 惯例）。（工程经验补充）

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_M_SetAlarm.TcPOU`](../examples/P_Demo_M_SetAlarm.TcPOU)（TwinCAT 3 原生 .TcPOU，可直接拖入 XAE 的 PLC POUs 文件夹）

```iecst
// 详见 examples 目录下的 .TcPOU 文件
```

## 7. 业务场景与实际价值

- **场景**：灌装机检测到出料温度超过 85°C 触发高温报警。检测代码用 R_TRIG 包裹一次性调用 `fbAdminAlarm.M_SetAlarm(stAdmin := PackTags.Admin, stAlarm := stHighTempAlarm)`。HMI 立即显示报警条目，MES 通过 OPC UA 订阅 `PackTags.Admin.Alarm[*]` 收到事件。
- **价值**：标准化的 alarm 上报接口——HMI/MES 端按 PackML 标准消费，跨厂家可互通。本方法把"找空位 + 写时间戳 + 拷贝字段"的细节隐藏，应用代码只关心填 Id/Message/Category。
- **替代方案对比**：自己写"遍历数组找空位+赋值+置 Trigger"代码——容易越界、时间戳逻辑不一致、不符合 PackML 标准。本方法是 OMAC 推荐写法。

## 8. 参考资料

- **PDF**：[`TwinCAT_3_PLC_Lib_Tc3_PackML_V3_EN.pdf`](https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc3_PackML_V3_EN.pdf) §4.2.1.1.7
- **InfoSys 参考 topic（同区段 FB）**：https://infosys.beckhoff.com/content/1033/tcplclib_tc3_packml_v3/16004004235.html （FB_PMLAdminTime topic；本 METHOD 自身 InfoSys topic 页面未公网检索到，已标 ⚠️ not-on-infosys）
- **相关**：`FB_PMLAdminAlarm`、`M_AcknowledgeAlarm`（确认）、`M_ClearAlarm`（清除）、`FB_PMLAdminTime`（提供时间戳）、`ST_PMLEvent`（事件结构）、`ST_PMLa`（管理 PackTag）

## 9. 待确认项 (⚠️)

- 数组满时具体覆盖策略与 FALSE 返回原因 PDF 均未列。
- V3 InfoSys 本 METHOD 自身 topic URL 未在公网检索结果中找到，已标 `⚠️ not-on-infosys`。
