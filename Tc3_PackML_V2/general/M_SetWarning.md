# M_SetWarning

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc3_PackML_V2` |
| Library Version | `1.2.4` |
| Type | `METHOD` |
| Category | `PML_AdminAlarm` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc3_PackML_V2_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tcplclib_tc3_packml_v2/6299606539.html |
| Verified | 2026-06-03 ✅ |
| InfoSys-checked | ✅ 2026-06-03 |
| Status | `verified` |
| Example | [`examples/P_Demo_M_SetWarning.TcPOU`](../examples/P_Demo_M_SetWarning.TcPOU) |

---

## 1. 功能简述

`PML_AdminAlarm.M_SetWarning()` 把一条 warning 写入 PackML Admin-Tag 的 `Warning[]` 数组：`Warning[].Trigger := TRUE` + 时间戳 + 拷贝结构字段。返回 TRUE 表示写入成功。

Warning 与 Alarm 用同一个 `ST_Alarm` 结构表示，但语义不同：Warning 是"提醒"（不停机，但需记录），Alarm 是"故障"（要求处理）。Warning **没有 History 数组**——新 warning 会顶掉最老一条。

## 2. 接口定义

### VAR_INPUT

```iecst
METHOD M_SetWarning : BOOL
VAR_INPUT
  stWarning        : ST_Alarm;
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `stWarning` | `ST_Alarm` | Warning 结构（与 Alarm 同型，调用方填 Id / Value / Message / Category）|

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
| `stAdmin` | `ST_PMLa` | PackML 管理 PackTag 结构 |

## 3. 行为说明

`M_SetWarning` 的实现与 `M_SetAlarm` 几乎一致，只是目标数组改成 `stAdmin.Warning[]`：

1. 在 `stAdmin.Warning[]` 找第一个 `Trigger=FALSE` 的空槽位；
2. 拷贝 `stWarning.Id / Value / Message / Category`；
3. `Warning[i].Trigger := TRUE`；
4. `Warning[i].DateTime := stAdmin.PlcDateTime`；
5. 返回 TRUE。

**与 Alarm 的关键区别**：Warning 数组**没有伴生的 History 数组**。PDF 直译："If the Warning array is already full of entries, the oldest entry is deleted as a result." —— 数组满时**直接顶掉最老 warning**，无历史归档。这意味着 Warning 仅用于"短期提醒"，长期统计需要应用层另存。

**调用语义**：调用即执行；用故障检测的上升沿包裹一次性触发。

**时间戳依赖**：与所有 PML_AdminAlarm 方法一样，必须保证 `PML_AdminTime` 周期调用。

**典型用例**：温度接近上限但还未触发 alarm（譬如温度 78°C、alarm 阈值 85°C）时上报 warning 给操作员提示"该检查冷却系统了"，不停机不报警。

## 4. 错误码 / 返回值

| 返回值 | 含义 | 处理建议 |
|---|---|---|
| `TRUE` | 写入成功 | 继续业务 |
| `FALSE` | 写入失败 | 检查 stAdmin 初始化；PDF 未列细分原因（⚠️ 待人工确认）|

## 5. 使用注意 / 常见坑

- **Warning 无 History**——重要 warning 想要长期保留必须应用层自存，否则一被顶掉就找不到了。（工程经验补充）
- 用 R_TRIG 包裹避免周期重复写入。
- 配合 `PML_AdminTime` 周期调用确保时间戳有效。
- `stWarning.Category` 推荐用与 alarm 不重叠的编号段（如 Warning 用 100-199、Alarm 用 1-99）便于 HMI 分类。（工程经验补充）

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_M_SetWarning.TcPOU`](../examples/P_Demo_M_SetWarning.TcPOU)（TwinCAT 3 原生 .TcPOU，可直接拖入 XAE 的 PLC POUs 文件夹）
>
> 导入步骤：右键 PLC 项目下 POUs 文件夹 → Add → Existing Item → 选该文件 → OK

```iecst
// 详见 examples 目录下的 .TcPOU 文件
```

## 7. 业务场景与实际价值

- **场景**：灌装机检测到原料桶液位低于 30%（未到 alarm 阈值 10%），上报 warning "Material level approaching minimum"。HMI 黄色提示但不停机，操作员可以安排补料。补料后下一次 alarm 检测时不再触发。
- **价值**：把"提醒"和"故障"分开数组管理，HMI 上 Warning 黄色 + Alarm 红色清晰区分。运营调度看 Warning 知道哪里要预防性维护，看 Alarm 知道哪里出了事。
- **替代方案对比**：把 warning 也写到 Alarm[]——HMI 红黄不分、操作员疲劳；用独立 BOOL 变量——没有时间戳和分类。本方法是 PackML 标准路径。

## 8. 参考资料

- **PDF**：[`TwinCAT_3_PLC_Lib_Tc3_PackML_V2_EN.pdf`](https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc3_PackML_V2_EN.pdf) §2.3.2.1.4
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tcplclib_tc3_packml_v2/6299606539.html
- **相关**：`PML_AdminAlarm.M_AcknowledgeWarning`、`PML_AdminAlarm.M_ClearWarning`、`PML_AdminTime`、`ST_Alarm`

## 9. 待确认项 (⚠️)

- 数组满时具体覆盖策略与 FALSE 返回原因 PDF + InfoSys 均未列。
