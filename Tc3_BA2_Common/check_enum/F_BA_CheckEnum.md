# F_BA_CheckEnum

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc3_BA2_Common` |
| Library Version | `1.0.2` |
| Type | `FUNCTION` |
| Category | `Functions / Universal` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc3_BA2_Common_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tcplclib_tc3_ba2_common/10785586571.html |
| Verified | 2026-06-03 ✅ |
| InfoSys-checked | ✅ 2026-06-03 |
| Status | `verified` |
| Example | [`examples/P_Demo_F_BA_CheckEnum.TcPOU`](../examples/P_Demo_F_BA_CheckEnum.TcPOU) |

---

## 1. 功能简述

检查一个枚举值 `nIndex` 是否在指定的枚举信息表 `aInfo : ARRAY[*] OF ST_BA_EnumInfo` 中。返回 BOOL：TRUE = 存在。`ARRAY[*]` 语法允许传入任意上下界的数组（编译器自动推断尺寸）。

## 2. 接口定义

### 完整声明

```iecst
FUNCTION F_BA_CheckEnum : BOOL
VAR_INPUT
  nIndex      : INT;
END_VAR
VAR_IN_OUT
  aInfo       : ARRAY [*] OF ST_BA_EnumInfo;
END_VAR
```

### VAR_INPUT 引脚

| 名称 | 类型 | 默认值 | 说明 |
|---|---|---|---|
| `nIndex` | `INT` | - | 被校验的枚举值（按数组下标使用）。 |

### VAR_IN_OUT 引脚

| 名称 | 类型 | 说明 |
|---|---|---|
| `aInfo` | `ARRAY [*] OF ST_BA_EnumInfo` | 枚举元数据数组（`ARRAY[*] OF ST_BA_EnumInfo`），通常传 `BAComn_EnumDE.aUnits` 等。 |


## 3. 行为说明

检查一个枚举值 `nIndex` 是否在指定的枚举信息表 `aInfo : ARRAY[*] OF ST_BA_EnumInfo` 中。返回 BOOL：TRUE = 存在。`ARRAY[*]` 语法允许传入任意上下界的数组（编译器自动推断尺寸）。 接入参数：`nIndex`。每个参数的类型与默认值见 §2 接口定义。 双向（IN_OUT）引脚：`aInfo`，必须在调用方持有变量地址（不能传字面量）。 本 FC 是 *无状态* 的纯函数：每次调用独立计算结果，不维护任何内部历史；多任务 / 多线程调用安全；可在 PRG / FB / METHOD / 表达式中任意位置使用。 典型工程场景：运行时检查 HMI 传入的枚举值合法性："用户选择的传感器类型代码是否在我支持的列表里"。

## 4. 错误码 / 返回值

本 FC 返回类型为 `BOOL`。

本 FC 返回 BOOL：`TRUE` = 判定成功 / 条件满足；`FALSE` = 判定失败 / 条件不满足。

## 5. 使用注意 / 常见坑

- 调用前必须确认 `Tc3_BA2_Common` 库已 reference（版本 ≥ 1.0.2）。
- FC 类无状态，多线程 / 多 task 调用安全；GVL 是常量集合，运行时只读。

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_F_BA_CheckEnum.TcPOU`](../examples/P_Demo_F_BA_CheckEnum.TcPOU)
>
> 导入步骤：右键 PLC 项目下 POUs 文件夹 → Add → Existing Item → 选该文件 → OK

详见 example xml 文件。

## 7. 业务场景与实际价值

- **场景**：运行时检查 HMI 传入的枚举值合法性："用户选择的传感器类型代码是否在我支持的列表里"。
- **价值**：一行 FC 替代手写 FOR 循环遍历查找。
- **替代方案对比**：`FOR i := L TO U DO IF aInfo[i].id = nIndex THEN ... EXIT; END_IF; END_FOR;`（与本 FC/GVL 相比，体现统一化 / 跨平台正确性 / 代码量节省等优势）。

## 8. 参考资料

- **PDF**：[TwinCAT_3_PLC_Lib_Tc3_BA2_Common_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc3_BA2_Common_EN.pdf) §4.3.1.4.2
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tcplclib_tc3_ba2_common/10785586571.html
- **相关枚举 / 结构**：见 PDF §4.1（DUTs）
