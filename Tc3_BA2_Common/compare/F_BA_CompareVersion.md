# F_BA_CompareVersion

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc3_BA2_Common` |
| Library Version | `1.0.2` |
| Type | `FUNCTION` |
| Category | `Functions / Compare` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc3_BA2_Common_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tcplclib_tc3_ba2_common/14593038731.html |
| Verified | 2026-06-03 ✅ |
| InfoSys-checked | ✅ 2026-06-03 |
| Status | `verified` |
| Example | [`examples/P_Demo_F_BA_CompareVersion.TcPOU`](../examples/P_Demo_F_BA_CompareVersion.TcPOU) |

---

## 1. 功能简述

比较两个 `ST_BA_Version` 版本号，按指定的比较运算符（等于 / 大于 / 小于等）返回 BOOL。可指定参与比较的分量数 `nLimit`（1=只比较 Major，4=比较全部 Major / Minor / Build / Revision）。常用于检查依赖库版本是否满足要求。

## 2. 接口定义

### 完整声明

```iecst
FUNCTION F_BA_CompareVersion : BOOL
VAR_INPUT
  stVersion1  : ST_BA_Version;
  stVersion2  : ST_BA_Version;
  eCompare    : E_BA_CompareMode  := E_BA_CompareMode.eEqual;
  nLimit      : UINT(1 .. 4)      := 4;
END_VAR
```

### VAR_INPUT 引脚

| 名称 | 类型 | 默认值 | 说明 |
|---|---|---|---|
| `stVersion1` | `ST_BA_Version` | - | 被比较的版本号 1（基准版本）。 |
| `stVersion2` | `ST_BA_Version` | - | 被比较的版本号 2（参照版本）。 |
| `eCompare` | `E_BA_CompareMode` | `E_BA_CompareMode.eEqual` | 比较运算符：`eEqual` / `eLower` / `eLowerOrEqual` / `eHigher` / `eHigherOrEqual` / `eNotEqual`。 |
| `nLimit` | `UINT(1 .. 4)` | `4` | 比较深度（1=只比 Major，2=Major+Minor，3=+Build，4=全部 4 段都比）。 |

### VAR_IN_OUT

无。


## 3. 行为说明

比较两个 `ST_BA_Version` 版本号，按指定的比较运算符（等于 / 大于 / 小于等）返回 BOOL。可指定参与比较的分量数 `nLimit`（1=只比较 Major，4=比较全部 Major / Minor / Build / Revision）。常用于检查依赖库版本是否满足要求。 接入参数：`stVersion1`, `stVersion2`, `eCompare`, `nLimit`。每个参数的类型与默认值见 §2 接口定义。 本 FC 是 *无状态* 的纯函数：每次调用独立计算结果，不维护任何内部历史；多任务 / 多线程调用安全；可在 PRG / FB / METHOD / 表达式中任意位置使用。 典型工程场景：楼宇控制器启动时检查 Tc3_BA2_Common 库版本：若 < V2.1.20.0 则报警阻止启动（避免运行时调用不存在的 FB）。

## 4. 错误码 / 返回值

本 FC 返回类型为 `BOOL`。

本 FC 返回 BOOL：`TRUE` = 判定成功 / 条件满足；`FALSE` = 判定失败 / 条件不满足。

## 5. 使用注意 / 常见坑

- 调用前必须确认 `Tc3_BA2_Common` 库已 reference（版本 ≥ 1.0.2）。
- FC 类无状态，多线程 / 多 task 调用安全；GVL 是常量集合，运行时只读。

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_F_BA_CompareVersion.TcPOU`](../examples/P_Demo_F_BA_CompareVersion.TcPOU)
>
> 导入步骤：右键 PLC 项目下 POUs 文件夹 → Add → Existing Item → 选该文件 → OK

详见 example xml 文件。

## 7. 业务场景与实际价值

- **场景**：楼宇控制器启动时检查 Tc3_BA2_Common 库版本：若 < V2.1.20.0 则报警阻止启动（避免运行时调用不存在的 FB）。
- **价值**：一行 FC 调用替代手写 `IF v.major < 2 OR (v.major = 2 AND v.minor < 1) THEN ...` 这种繁琐多级 IF；`nLimit` 让你按需控制比较精度。
- **替代方案对比**：手写多级 IF 比较 Major/Minor/Build/Revision 字段（约 10 行 + 易写错优先级）（与本 FC/GVL 相比，体现统一化 / 跨平台正确性 / 代码量节省等优势）。

## 8. 参考资料

- **PDF**：[TwinCAT_3_PLC_Lib_Tc3_BA2_Common_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc3_BA2_Common_EN.pdf) §4.3.1.1.1
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tcplclib_tc3_ba2_common/14593038731.html
- **相关枚举 / 结构**：见 PDF §4.1（DUTs）
