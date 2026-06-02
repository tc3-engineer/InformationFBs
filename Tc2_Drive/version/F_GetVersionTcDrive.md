# F_GetVersionTcDrive

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc2_Drive` |
| Library Version | `1.4.8` |
| Type | `FUNCTION` |
| Category | `Functions` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_Drive_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tcplclib_tc2_drive/2307581451.html |
| Verified | 2026-05-25 ✅ |
| InfoSys-checked | ✅ 2026-05-25 |
| Status | `verified` |
| Example | [`examples/P_Demo_F_GetVersionTcDrive.TcPOU`](../examples/P_Demo_F_GetVersionTcDrive.TcPOU) |

---

## 1. 功能简述

读取 `Tc2_Drive` PLC 库版本信息的函数。给定一个版本元素编号 `nVersionElement`，返回库版本号的对应字段（主版本 / 次版本 / 修订号），返回类型为 `UINT`。

可用于运行期检查库版本是否满足程序要求（例如在初始化阶段断言库版本不低于某个值），或在 HMI 上显示当前所用 Tc2_Drive 库版本。

## 2. 接口定义

### VAR_INPUT

```iecst
VAR_INPUT
    nVersionElement : INT;
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `nVersionElement` | `INT` | 要读取的版本元素编号。可取值：`1` = 主版本号（major）、`2` = 次版本号（minor）、`3` = 修订号（revision） |

### VAR_OUTPUT

无（本函数通过返回值给出结果）。

### VAR_IN_OUT

无。

## 3. 行为说明

本函数是无状态、同步返回的纯函数，单个 PLC 周期内即返回结果，不涉及任何异步通讯或 ADS：

1. 调用时传入 `nVersionElement`（1 / 2 / 3）。
2. 函数从库内部固化的版本信息中取出对应字段并作为 `UINT` 返回：`1` 返回主版本号、`2` 返回次版本号、`3` 返回修订号。
3. 没有 `bExecute` / `bBusy` 等异步握手，直接表达式调用即可（`F_GetVersionTcDrive(1)`）。

**取值范围之外的行为**：`nVersionElement` 取 1/2/3 以外的值时，返回值由实现定义，PDF 未明确说明，不要依赖（⚠️）。

**与本库版本对应**：本库当前版本为 `1.4.8`（PDF 头部 "Version: 1.4.8"），故 `F_GetVersionTcDrive(1)` 返回 `1`、`(2)` 返回 `4`、`(3)` 返回 `8`。

## 4. 错误码 / 返回值

本函数返回 `UINT` = 所选版本字段：

| `nVersionElement` | 返回值含义 |
|---|---|
| `1` | 主版本号（major） |
| `2` | 次版本号（minor） |
| `3` | 修订号（revision） |
| 其它 | 实现定义（PDF 未说明，⚠️ 不要依赖） |

本函数无错误输出，不会产生 ADS / Sercos 错误码。

## 5. 使用注意 / 常见坑

- **是函数不是功能块**：直接表达式调用 `F_GetVersionTcDrive(1)` 即可，不需要实例化、不需要 `bExecute` 触发。
- **`nVersionElement` 只认 1/2/3**：传其它值的返回未定义，写代码时用具名常量或注释清楚，别传变量后忘了约束范围。（工程经验补充）
- **版本断言放初始化**：典型用法是在程序启动时检查 `F_GetVersionTcDrive(1)`/`(2)`/`(3)` 是否满足最低要求，不满足就报警 / 阻止运行，避免在不兼容的库版本上跑。（工程经验补充）
- **若库提供 `stLibVersion_Tc2_Drive` 全局常量**：直接读结构体字段是编译期解析、无运行时开销的更现代做法（⚠️ 该常量是否存在以本库实际符号为准，PDF 本节未提及，待人工确认）。

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_F_GetVersionTcDrive.TcPOU`](../examples/P_Demo_F_GetVersionTcDrive.TcPOU)（TwinCAT 3 原生 .TcPOU，可直接拖入 XAE 的 PLC POUs 文件夹）
>
> 导入步骤：右键 PLC 项目下 POUs 文件夹 → Add → Existing Item → 选该文件 → OK
> 详见 [`examples/README.md`](../examples/README.md)

```iecst
PROGRAM P_Demo_F_GetVersionTcDrive
VAR
    iMajor      : UINT;                            // 在线 monitor：主版本号(应为 1)
    iMinor      : UINT;                            // 次版本号(应为 4)
    iRevision   : UINT;                            // 修订号(应为 8)
    bVersionOk  : BOOL;                            // 版本满足最低要求的断言结果
END_VAR

// 函数直接表达式调用，无需实例化、无需 bExecute
iMajor    := F_GetVersionTcDrive(1);               // 1 = major
iMinor    := F_GetVersionTcDrive(2);               // 2 = minor
iRevision := F_GetVersionTcDrive(3);               // 3 = revision

// 初始化期断言：要求 Tc2_Drive 库不低于 1.4.0
// 用 TO_INT 把 UINT 显式转为 INT 再比较，避免无符号比较歧义
bVersionOk := (TO_INT(iMajor) > 1)
           OR ((TO_INT(iMajor) = 1) AND (TO_INT(iMinor) >= 4));
```

## 7. 业务场景与实际价值

- **场景**：程序依赖 Tc2_Drive 某版本起才有的行为，需要在运行期确认实际加载的库版本满足要求；或在 HMI 诊断页显示当前库版本。
- **价值**：把库版本以 `UINT` 形式暴露给 PLC 逻辑，可做版本断言 / 显示，无需人工查工程引用。
- **替代方案对比**：
  - 读 `stLibVersion_Tc2_Drive` 全局常量（若库提供）：编译期解析、零运行时开销，是更现代的做法
  - 在工程引用里人工核对版本：不能在运行期程序里判断
  - **本函数**：运行期可调用、可做条件判断，适合做版本断言逻辑

## 8. 参考资料

- **PDF**：[TwinCAT_3_PLC_Lib_Tc2_Drive_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_Drive_EN.pdf) §4.4
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tcplclib_tc2_drive/2307581451.html
- **相关**：`stLibVersion_Tc2_Drive`（库版本全局常量，若存在；⚠️ 待确认）

## 9. 待确认项

- ⚠️ `nVersionElement` 取 1/2/3 以外值的返回行为 PDF 未定义。
- ⚠️ 是否存在 `stLibVersion_Tc2_Drive` 全局常量本节 PDF 未提及，需查库符号确认。
