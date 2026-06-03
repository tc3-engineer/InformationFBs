# F_BA_IVal

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc3_BA2_Common` |
| Library Version | `1.0.2` |
| Type | `FUNCTION` |
| Category | `Functions / Types / ClassValue` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc3_BA2_Common_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tcplclib_tc3_ba2_common/9917898507.html |
| Verified | 2026-06-03 ✅ |
| InfoSys-checked | ✅ 2026-06-03 |
| Status | `verified` |
| Example | [`examples/P_Demo_F_BA_IVal.TcPOU`](../examples/P_Demo_F_BA_IVal.TcPOU) |

---

## 1. 功能简述

把 INT 值打包成 `ST_BA_ClassValue` 结构。

## 2. 接口定义

### 完整声明

```iecst
FUNCTION F_BA_IVal : U_BA_ClassValue
VAR_INPUT
  nValue    : INT;
END_VAR
```

### VAR_INPUT 引脚

| 名称 | 类型 | 默认值 | 说明 |
|---|---|---|---|
| `nValue` | `INT` | - | This value is assigned to iVal  in the output structure. |

### VAR_IN_OUT

无。


## 3. 行为说明

把 INT 值打包成 `ST_BA_ClassValue` 结构。 接入参数：`nValue`。每个参数的类型与默认值见 §2 接口定义。 本 FC 是 *无状态* 的纯函数：每次调用独立计算结果，不维护任何内部历史；多任务 / 多线程调用安全；可在 PRG / FB / METHOD / 表达式中任意位置使用。 ClassValue 系列 FC 把不同基本类型的值统一打包成 `ST_BA_ClassValue` 结构，让趋势记录 / SCADA 推送等下游模块用一种类型处理任意原始数据。 典型工程场景：楼宇 INT 类型测点（如风量等级 -10..+10）统一上传到趋势 / SCADA。

## 4. 错误码 / 返回值

本 FC 返回类型为 `U_BA_ClassValue`。

本 FC 返回 `U_BA_ClassValue` 结构 / 枚举 / 字符串。无错误代码，错误时返回零值结构。

## 5. 使用注意 / 常见坑

- 调用前必须确认 `Tc3_BA2_Common` 库已 reference（版本 ≥ 1.0.2）。
- FC 类无状态，多线程 / 多 task 调用安全；GVL 是常量集合，运行时只读。

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_F_BA_IVal.TcPOU`](../examples/P_Demo_F_BA_IVal.TcPOU)
>
> 导入步骤：右键 PLC 项目下 POUs 文件夹 → Add → Existing Item → 选该文件 → OK

详见 example xml 文件。

## 7. 业务场景与实际价值

- **场景**：楼宇 INT 类型测点（如风量等级 -10..+10）统一上传到趋势 / SCADA。
- **价值**：同其它 ClassValue 系列。
- **替代方案对比**：手写多行结构赋值（与本 FC/GVL 相比，体现统一化 / 跨平台正确性 / 代码量节省等优势）。

## 8. 参考资料

- **PDF**：[TwinCAT_3_PLC_Lib_Tc3_BA2_Common_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc3_BA2_Common_EN.pdf) §4.3.1.3.2.3
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tcplclib_tc3_ba2_common/9917898507.html
- **相关枚举 / 结构**：见 PDF §4.1（DUTs）
