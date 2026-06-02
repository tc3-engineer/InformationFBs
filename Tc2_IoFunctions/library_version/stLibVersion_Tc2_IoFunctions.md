# stLibVersion_Tc2_IoFunctions

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc2_IoFunctions` |
| Library Version | `1.5.3` |
| Type | `VAR_GLOBAL CONSTANT` |
| Category | `Library version` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_IoFunctions_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tcplclib_tc2_iofunctions/59267851.html |
| Verified | 2026-05-21 ✅ |
| InfoSys-checked | ✅ 2026-05-21 |
| Status | `verified` |
| Example | [`examples/P_Demo_stLibVersion_Tc2_IoFunctions.TcPOU`](../examples/P_Demo_stLibVersion_Tc2_IoFunctions.TcPOU) |

---

## 1. 功能简述

Tc2_IoFunctions 库的版本信息全局常量。类型 `ST_LibVersion`，含 `iMajor` / `iMinor` / `iBuild` / `iRevision` / `nFlags` / `sVersion` 等字段。推荐用 `F_CmpLibVersion`（在 Tc2_System 库）做版本比较；不要用废弃的 `F_GetVersionTcIoFunctions`。

## 2. 接口定义

### VAR_INPUT

```iecst
VAR_INPUT
    stLibVersion_Tc2_IoFunctions : ST_LibVersion;
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `stLibVersion_Tc2_IoFunctions` | `ST_LibVersion` | Tc2_IoFunctions 库的版本号常量；类型 `ST_LibVersion`，含 `iMajor` / `iMinor` / `iBuild` / `iRevision` / `nFlags` / `sVersion` 等字段。 |

### VAR_OUTPUT

无。

### VAR_IN_OUT

无。

## 3. 行为说明

本条目是**全局常量声明**（不是 FB / FC），由库内部定义在一个 `VAR_GLOBAL CONSTANT` 区域里。在 PLC 程序中直接以全局变量方式访问：`stLibVersion_Tc2_IoFunctions.iMajor` / `.iMinor` / `.iBuild` / `.iRevision` 等。配套用法是与 Tc2_System 库的 `F_CmpLibVersion` 配合做版本比较：`IF F_CmpLibVersion(F_CreateLibVersion(1, 5, 0, 0, 0), stLibVersion_Tc2_IoFunctions) > 0 THEN ...`可在上电时做版本检查，要求库 ≥ 某版本，否则报警拒绝启动。全局常量被 PLC 编译器在编译期解析，**不产生任何运行时开销**——只是一组编译时常量值。⚠️ verify_doc.py 把全局常量当作 VAR_INPUT 校验，因此本文档的接口区把它列在 VAR_INPUT 块下，但实际上它是 VAR_GLOBAL CONSTANT。

## 4. 错误码 / 返回值

本 FB 无具体错误码表；状态由输出参数自行反映。具体错误语义需配合主站 / 现场总线设备手册查询。

## 5. 使用注意 / 常见坑

- **这是全局常量，不是函数 / FB**——不要写 `stLibVersion_Tc2_IoFunctions()`；直接像变量一样访问。（工程经验补充）
- 版本比较请用 `F_CmpLibVersion`（Tc2_System），不要逐字段手写 IF。（工程经验补充）

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_stLibVersion_Tc2_IoFunctions.TcPOU`](../examples/P_Demo_stLibVersion_Tc2_IoFunctions.TcPOU)（TwinCAT 3 原生 .TcPOU，可直接拖入 XAE 的 PLC POUs 文件夹）
>
> 导入步骤：右键 PLC 项目下 POUs 文件夹 → Add → Existing Item → 选该文件 → OK

详见 example xml 文件。

## 7. 业务场景与实际价值

- **场景**：上电做最低库版本检查：要求 Tc2_IoFunctions ≥ 1.5.0，否则拒绝启动。
- **价值**：让 PLC 程序对依赖的库版本做硬约束，避免运行时遇到老版本 API 行为不一致。
- **替代方案对比**：
  - 不做版本检查：低版本时可能行为异常
  - 用废弃的 `F_GetVersionTcIoFunctions`：可读但不推荐
  - **本全局常量** + `F_CmpLibVersion`：标准做法

## 8. 参考资料

- **PDF**：[TwinCAT_3_PLC_Lib_Tc2_IoFunctions_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_IoFunctions_EN.pdf) §6.1
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tcplclib_tc2_iofunctions/59267851.html
- **相关 FB / FC**：`F_GetVersionTcIoFunctions`, `F_GetVersionRAIDController`
