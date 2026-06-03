# F_PMLUnitModeToString

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc3_PackML_V3` |
| Library Version | `1.0.0` |
| Type | `FUNCTION` |
| Category | `Conversion` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc3_PackML_V3_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tcplclib_tc3_packml_v3/16003571595.html |
| Verified | 2026-06-03 ✅ |
| InfoSys-checked | ⚠️ not-on-infosys |
| Status | `verified` |
| Example | [`examples/P_Demo_F_PMLUnitModeToString.TcPOU`](../examples/P_Demo_F_PMLUnitModeToString.TcPOU) |

---

## 1. 功能简述

`F_PMLUnitModeToString` 把 PackML UnitMode 编号（`DINT`）转换为可读字符串名称。返回 `STRING`——把 `1` 转成 `'Production'`、`2` 转成 `'Maintenance'`、`3` 转成 `'Manual'`、`4..31` 转成用户通过 `FB_PMLUnitModeConfig` 配置的 `sName` 字符串。

**V3 与 V2 的关键差异**：V2 函数名是 `F_UnitModeToString`（无 `PML` 前缀）；V3 改为 `F_PMLUnitModeToString`，与同库 `F_PMLStateCommandToString` 保持命名风格一致。

主要用于 HMI 显示和事件日志——OPC UA 拉到 `PackTags.Status.UnitModeCurrent` 是数字，HMI 需要用文本展示当前模式。

## 2. 接口定义

### 函数签名

```iecst
FUNCTION F_PMLUnitModeToString : STRING;
```

### VAR_INPUT

```iecst
VAR_INPUT
    eMode              : DINT;
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `eMode` | `DINT` | 要转换的 UnitMode 编号（0=Invalid / 1=Production / 2=Maintenance / 3=Manual / 4..31=用户自定义模式）|

### VAR_OUTPUT

无（结果通过 `FUNCTION` 返回值给出）。

### VAR_IN_OUT

无。

## 3. 行为说明

`F_PMLUnitModeToString` 是查表函数：

**基础模式映射（PackML V3 预定义）**：
- `0` → `'Invalid'`
- `1` → `'Production'`
- `2` → `'Maintenance'`
- `3` → `'Manual'`

**用户自定义模式映射（4-31）**：从全局 `stPMLUnitModeConfiguration` 数组取对应索引项的 `sName` 字段。这个全局数组由 `FB_PMLUnitModeConfig` 注册时填充——如果应用层从未注册某个模式编号，调本函数返回值未定义（PDF 未明确，可能是空字符串）。

**调用语义**：纯函数——同一输入永远返回同一输出（前提是 `stPMLUnitModeConfiguration` 状态稳定）。

**典型用例**：HMI 顶端"当前模式"标签——`sCurrentModeName := F_PMLUnitModeToString(eMode := PackTags.Status.UnitModeCurrent);`，文本显示给操作员。

## 4. 错误码 / 返回值

返回 `STRING`：对应模式编号的字符串名。具体字面值（如基础模式是否含前缀）PDF 未列样本，⚠️ 建议测试确认。

未注册的自定义模式（如 4-31 中某个 eMode 没注册过）返回行为 PDF 未列：可能返回空字符串，可能返回 `'Invalid'`，可能返回内存里的随机内容。⚠️ 建议先调用 `FB_PMLUnitModeConfig` 注册后再用本函数查询。

## 5. 使用注意 / 常见坑

- 必须先用 `FB_PMLUnitModeConfig` 注册自定义模式（4-31）才能反查到 `sName`；否则返回值不可预期。（工程经验补充）
- 默认 `STRING` 类型 80 字符长度，本函数返回的字符串都很短不会溢出。
- 与 `F_PMLStateCommandToString` 互补——前者转模式编号、后者转命令枚举。
- 与 V2 (`F_UnitModeToString`) 函数名不同：V3 多了 `PML` 前缀。

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_F_PMLUnitModeToString.TcPOU`](../examples/P_Demo_F_PMLUnitModeToString.TcPOU)（TwinCAT 3 原生 .TcPOU，可直接拖入 XAE 的 PLC POUs 文件夹）
>
> 导入步骤：右键 PLC 项目下 POUs 文件夹 → Add → Existing Item → 选该文件 → OK

```iecst
// 详见 examples 目录下的 .TcPOU 文件
```

## 7. 业务场景与实际价值

- **场景**：HMI 顶端有一个"当前模式"标签实时显示——`PackTags.Status.UnitModeCurrent` 是数字 1，操作员看不出是 Production 还是 Cleaning。本函数把数字翻译成中文/英文模式名（如 'Production' / 'Cleaning'）显示。MES 同样用本函数把数字事件翻译成文本写入日志。
- **价值**：基础模式 + 自定义模式统一映射，应用层不必维护自己的 case 表。新增模式只需注册一次 Config，反查自动生效。
- **替代方案对比**：手写 `IF eMode = 1 THEN sName := 'Production'; ...` ——代码量大、新增模式忘记更新；本函数自动跟随 `FB_PMLUnitModeConfig` 注册同步。

## 8. 参考资料

- **PDF**：[`TwinCAT_3_PLC_Lib_Tc3_PackML_V3_EN.pdf`](https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc3_PackML_V3_EN.pdf) §4.1.4
- **InfoSys 参考 topic（基础模式枚举）**：https://infosys.beckhoff.com/content/1033/tcplclib_tc3_packml_v3/16003571595.html （E_PMLProtectedUnitMode 枚举 topic；本函数前 4 个模式（0-3）即此枚举；V3 本 FUNCTION 自身 InfoSys topic 页面公网未检索到，故 InfoSys-checked 标 ⚠️ not-on-infosys）
- **相关**：`F_PMLStateCommandToString`（命令枚举转字符串）、`FB_PMLUnitModeConfig`（注册自定义模式的 sName）、`E_PMLProtectedUnitMode`（基础模式枚举）、`ST_PMLUnitModeConfiguration`（全局配置数组）

## 9. 待确认项 (⚠️)

- 未注册的自定义模式编号查询行为 PDF 未列。
- 基础模式（0-3）字符串字面值具体形式 PDF 未列样本，建议运行测试确认。
- V3 InfoSys 本 FUNCTION 自身 topic URL 未在公网检索结果中找到，已标 `⚠️ not-on-infosys`。
