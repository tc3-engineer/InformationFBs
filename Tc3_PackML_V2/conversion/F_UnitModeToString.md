# F_UnitModeToString

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc3_PackML_V2` |
| Library Version | `1.2.4` |
| Type | `FUNCTION` |
| Category | `Conversion` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc3_PackML_V2_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tcplclib_tc3_packml_v2/6302851083.html |
| Verified | 2026-06-03 ✅ |
| InfoSys-checked | ✅ 2026-06-03 |
| Status | `verified` |
| Example | [`examples/P_Demo_F_UnitModeToString.TcPOU`](../examples/P_Demo_F_UnitModeToString.TcPOU) |

---

## 1. 功能简述

`F_UnitModeToString` 把 PackML UnitMode 编号（DINT，范围 1-31）转换为可读字符串名称。返回 STRING——基础模式 1/2/3 映射到 `'Production'` / `'Maintenance'` / `'Manual'`；自定义模式 4-31 返回通过 `PML_UnitModeConfig` 注册时填入的 `sName` 字符串。

主要用于 HMI 显示当前模式名、写日志、报警标签等场景。

## 2. 接口定义

### 函数签名

```iecst
FUNCTION F_UnitModeToString : STRING;
```

### VAR_INPUT

```iecst
VAR_INPUT
    eMode              : DINT;
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `eMode` | `DINT` | 要查询的 UnitMode 编号（0=Invalid / 1=Production / 2=Maintenance / 3=Manual / 4-31=自定义）|

### VAR_OUTPUT

无（结果通过 FUNCTION 返回值给出）。

### VAR_IN_OUT

无。

## 3. 行为说明

`F_UnitModeToString` 根据输入的 UnitMode 编号查表返回对应的字符串名。

**基础模式（编号 1-3）**：返回值是 PackML 标准定义的硬编码字符串：
- `1` → `'Production'`
- `2` → `'Maintenance'`
- `3` → `'Manual'`

**自定义模式（编号 4-31）**：返回值是通过 `PML_UnitModeConfig` 注册时填入的 `sName` 字符串。如果模式编号未被注册过、`F_UnitModeToString` 返回值 PDF 未明确（⚠️ 可能是空字符串或 'Invalid'）。

**Invalid 模式（编号 0）**：返回 `'Invalid'` 或空字符串（⚠️ 待确认）。

**与 `F_StateCommandToString` 的关系**：前者把模式编号 (DINT) 转字符串、后者把命令枚举 (E_PMLCommand) 转字符串。配合 `PML_UnitModeManager.eModeStatus`（DINT 输出）使用很自然。

**调用语义**：纯函数（除非读取了已注册模式表，这部分是不变查询）。

**典型用法**：HMI 文本框显示"Current Mode: <name>" 时调本函数：`sMode := F_UnitModeToString(PackTags.Status.UnitModeCurrent);`，把返回字符串绑定到 HMI 控件。

## 4. 错误码 / 返回值

返回 `STRING`：对应 UnitMode 编号的名称字符串。

未注册的自定义模式或越界值返回 PDF + InfoSys 未明确，⚠️ 建议测试。

## 5. 使用注意 / 常见坑

- 自定义模式必须先调 `PML_UnitModeConfig` 注册 + 填 `sName`，本函数才能返回有意义的字符串。
- 默认 `STRING` 80 字符长度容纳模式名足够；`PML_UnitModeConfig.sName` 也是 STRING（默认 80）。
- 用于 HMI 显示；数据库存编号更紧凑、显示用本函数。
- 输入越界（编号 32+）的返回 PDF 未明确。（工程经验补充）

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_F_UnitModeToString.TcPOU`](../examples/P_Demo_F_UnitModeToString.TcPOU)（TwinCAT 3 原生 .TcPOU，可直接拖入 XAE 的 PLC POUs 文件夹）
>
> 导入步骤：右键 PLC 项目下 POUs 文件夹 → Add → Existing Item → 选该文件 → OK

```iecst
// 详见 examples 目录下的 .TcPOU 文件
```

## 7. 业务场景与实际价值

- **场景**：HMI 主界面要显示"当前模式：Production"——直接显示数字 1 操作员看不懂。调 `sName := F_UnitModeToString(PackTags.Status.UnitModeCurrent);` 把数字转字符串绑定 HMI 文本控件。同样用于把 PackTags 里的 UnitMode 数值译成文本写入历史归档/MES 报表。
- **价值**：UnitMode↔字符串的标准映射封装，自定义模式自动用注册时的 sName。HMI 上的文本绑定一行搞定。
- **替代方案对比**：HMI 端自己写 case "1→'Production'..."——硬编码新增模式要改两处；本函数读 PML_UnitModeConfig 注册表，新增模式只改一处。

## 8. 参考资料

- **PDF**：[`TwinCAT_3_PLC_Lib_Tc3_PackML_V2_EN.pdf`](https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc3_PackML_V2_EN.pdf) §2.3.3.4
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tcplclib_tc3_packml_v2/6302851083.html
- **相关**：`F_StateCommandToString`（命令枚举转字符串）、`PML_UnitModeConfig`（注册自定义模式 sName）、`PML_UnitModeManager.sModeStatus`（直接输出当前模式名）、`E_PMLProtectedUnitMode`（基础模式枚举）

## 9. 待确认项 (⚠️)

- 未注册自定义模式编号 / 越界编号（32+）的返回值 PDF + InfoSys 均未列。
