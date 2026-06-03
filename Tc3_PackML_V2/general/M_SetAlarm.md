# M_SetAlarm

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc3_PackML_V2` |
| Library Version | `1.2.4` |
| Type | `METHOD` |
| Category | `PML_AdminAlarm` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc3_PackML_V2_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tcplclib_tc3_packml_v2/6298536971.html |
| Verified | 2026-06-03 ✅ |
| InfoSys-checked | ✅ 2026-06-03 |
| Status | `verified` |
| Example | [`examples/P_Demo_M_SetAlarm.TcPOU`](../examples/P_Demo_M_SetAlarm.TcPOU) |

---

## 1. 功能简述

`PML_AdminAlarm.M_SetAlarm()` 把一条 alarm 写入 PackML Admin-Tag 的 `Alarm[]` 数组：把 `Alarm[].Trigger` 置 TRUE、从 `Admin.PlcDateTime` 读取并写入 `Alarm[].DateTime`，其余字段（Id / Value / Message / Category）从入参 `stAlarm` 拷贝。返回 TRUE 表示写入成功。

为了让时间戳有效，主程序必须周期调用 `PML_AdminTime`。

## 2. 接口定义

### VAR_INPUT

```iecst
METHOD M_SetAlarm : BOOL
VAR_INPUT
  stAlarm          : ST_Alarm;
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `stAlarm` | `ST_Alarm` | 输入 alarm 结构：调用方填好 `Id`（编号）、`Value`（关联数值如温度阈值）、`Message`（文本）、`Category`（分类）。`Trigger / DateTime / AckDateTime` 由方法内部填 |

### VAR_OUTPUT

无（返回值 BOOL 通过 METHOD 返回类型给出）。

### VAR_IN_OUT

```iecst
VAR_IN_OUT
  stAdmin          : ST_PMLa;
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `stAdmin` | `ST_PMLa` | PackML 管理 PackTag 结构。方法读取它的 `PlcDateTime` 作时间戳、把 alarm 写入它的 `Alarm[]` 数组 |

## 3. 行为说明

`M_SetAlarm` 实现 alarm "上报"的标准流程：

1. 在 `stAdmin.Alarm[]` 数组里找第一个 `Trigger = FALSE` 的空槽位（未触发的位置）；
2. 把 `stAlarm.Id / Value / Message / Category` 拷贝过去；
3. `stAdmin.Alarm[i].Trigger := TRUE`；
4. `stAdmin.Alarm[i].DateTime := stAdmin.PlcDateTime`（7 元素 DINT 数组：年/月/日/时/分/秒/毫秒）；
5. 返回 TRUE。

**数组满时行为**（PDF 未明确）：根据 PackML 标准的环形数组约定，最老一项被覆盖；具体覆盖策略 PDF 没说，⚠️ 建议测试观察。

**调用语义**：调用即执行——不是上升沿触发。每次想加一条 alarm 就调一次本方法。如果在每周期都调（不带门控），会立刻把数组填满并不停顶替。**正确做法是只在故障检测的上升沿调一次**。

**时间戳依赖**：`stAdmin.PlcDateTime` 由 `PML_AdminTime` 周期填充。如果 `PML_AdminTime` 没在主任务里调用，时间戳全部为 0 或上电初值。

**返回值含义**：PDF 说返回 TRUE = 写入成功。FALSE 的可能原因（PDF 未列）⚠️：数组满+覆盖策略禁止覆盖；输入参数无效（Id = 0）等。

## 4. 错误码 / 返回值

| 返回值 | 含义 | 处理建议 |
|---|---|---|
| `TRUE` | 写入成功 | 继续业务 |
| `FALSE` | 写入失败 | 检查 stAdmin 初始化、PML_AdminTime 是否调用、数组是否满；PDF 未列具体原因（⚠️ 待人工确认）|

## 5. 使用注意 / 常见坑

- **必须配合 `PML_AdminTime` 周期调用**——否则 DateTime 全是初值。
- **只在故障上升沿调一次**——每周期调会覆盖数组；正确做法用 R_TRIG 包裹。（工程经验补充）
- `stAlarm.Id` 建议用项目级枚举管理（如 `eAlarmId_TempHigh = 1001`），便于 HMI/MES 反查。（工程经验补充）
- `stAlarm.Message` 是 `STRING`，默认 80 字符——超长会被截断。
- `stAlarm.Category` 用于 HMI 按严重度分类显示，建议 1=Critical / 2=Major / 3=Minor 之类。（工程经验补充）

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_M_SetAlarm.TcPOU`](../examples/P_Demo_M_SetAlarm.TcPOU)（TwinCAT 3 原生 .TcPOU，可直接拖入 XAE 的 PLC POUs 文件夹）
>
> 导入步骤：右键 PLC 项目下 POUs 文件夹 → Add → Existing Item → 选该文件 → OK

```iecst
// 详见 examples 目录下的 .TcPOU 文件
```

## 7. 业务场景与实际价值

- **场景**：灌装机检测到出料温度超过 85°C 触发高温报警。检测代码用 R_TRIG 包裹一次性调用 `fbAdminAlarm.M_SetAlarm(stAdmin := PackTags.Admin, stAlarm := stHighTempAlarm)`，把 `stHighTempAlarm.Id := 1001; .Message := 'Outlet temperature exceeded 85C'; .Category := 1;` 写入。HMI 立即显示报警条目，MES 通过 OPC UA 订阅 PackTags.Admin.Alarm[*] 收到事件。
- **价值**：标准化的 alarm 上报接口——HMI/MES 端按 PackML 标准消费，跨厂家可互通。本方法把"找空位 + 写时间戳 + 拷贝字段"的细节隐藏，应用代码只关心填 Id/Message/Category。
- **替代方案对比**：自己写"遍历数组找空位+赋值+置 Trigger"代码——容易越界、时间戳逻辑不一致、不符合 PackML 标准。本方法是 OMAC 推荐写法。

## 8. 参考资料

- **PDF**：[`TwinCAT_3_PLC_Lib_Tc3_PackML_V2_EN.pdf`](https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc3_PackML_V2_EN.pdf) §2.3.2.1.1
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tcplclib_tc3_packml_v2/6298536971.html
- **相关**：`PML_AdminAlarm.M_AcknowledgeAlarm`（确认）、`PML_AdminAlarm.M_ClearAlarm`（清除）、`PML_AdminTime`（提供时间戳）、`ST_Alarm`（事件结构）、`ST_PMLa`（管理 PackTag）

## 9. 待确认项 (⚠️)

- 数组满时具体覆盖策略与 FALSE 返回原因 PDF + InfoSys 均未列。
