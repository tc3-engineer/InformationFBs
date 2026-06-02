# stLibVersion_Tc2_System

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc2_System` |
| Library Version | `1.17.3` |
| Type | `VAR_GLOBAL CONSTANT` |
| Category | `Library version` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_System_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tcplclib_tc2_system/31086731.html |
| Verified | 2026-05-20 ✅ |
| InfoSys-checked | ✅ 2026-05-20 |
| Status | `verified` |
| Example | [`examples/P_Demo_stLibVersion_Tc2_System.TcPOU`](../examples/P_Demo_stLibVersion_Tc2_System.TcPOU) |

---

## 1. 功能简述

`stLibVersion_Tc2_System` 是 Tc2_System 库的版本全局常量（`ST_LibVersion` 类型）。每个 Beckhoff PLC 库都按统一命名规则提供同名常量 `stLibVersion_<library>`。结合 `F_CmpLibVersion` 函数可在启动期做库版本守门，避免依赖错版本的库导致接口不兼容。

## 2. 接口定义

```iecst
VAR_GLOBAL CONSTANT
    stLibVersion_Tc2_System : ST_LibVersion;
END_VAR
```

### VAR_INPUT

无。

### VAR_OUTPUT

无。

### VAR_IN_OUT

无。

## 3. 行为说明

**类型结构 `ST_LibVersion`**：包含 4 个字段——

- `iMajor : UINT` 主版本号
- `iMinor : UINT` 次版本号
- `iBuild : UINT` 构建号
- `iRevision : UINT` 修订号

另外还有 `sVersion : STRING` 字符串形式版本和 `sLibName : STRING` 库名等字段（具体见 `ST_LibVersion` topic）。

**编译期常量**：由 Beckhoff 在发布库时写死；引用本库后该常量自动可用，无需自己赋值。

**使用模式**：

1. **直读字段**：`nMyMajor := stLibVersion_Tc2_System.iMajor;`
2. **比对版本**：`nCmp := F_CmpLibVersion(stLibVersion_Tc2_System, 3, 3, 8, 0); IF nCmp < 0 THEN ... END_IF;`
3. **HMI 显示**：直接读 `sVersion` 字符串字段。

**统一规则**：所有 Beckhoff 库都遵循 `stLibVersion_<libname>` 命名，跨库守门只需把库名换掉。

## 4. 错误码 / 返回值

本节是 `VAR_GLOBAL CONSTANT`，无返回值。访问方式：直接 `stLibVersion_Tc2_System.iMajor` 等。

## 5. 使用注意 / 常见坑

- **不要写 `stLibVersion_Tc2_System := ...`**：常量赋值编译报错。（工程经验补充）
- **字段名 `iMajor` 而不是 `nMajor`**：早期版本可能不同；以 PDF 当前版本为准。（工程经验补充）
- **库未引用时编译错误**：常量编译期就需要存在，库未加进项目会直接编译失败。（工程经验补充）
- **与运行时实际加载的库版本**：通常一致，但热更新场景下可能不同步；正常工程不会遇到。（工程经验补充）

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_stLibVersion_Tc2_System.TcPOU`](../examples/P_Demo_stLibVersion_Tc2_System.TcPOU)（TwinCAT 3 原生 .TcPOU，可直接拖入 XAE 的 PLC POUs 文件夹）。
>
> 导入步骤：右键 PLC 项目下 POUs 文件夹 → Add → Existing Item → 选该文件 → OK

详见 example xml 文件。

## 7. 业务场景与实际价值

- **场景**：集成商交付前的版本守门：MAIN 启动时读 `stLibVersion_Tc2_System.iMajor / iMinor / iBuild / iRevision` 写入诊断日志，便于事后追溯；同时用 `F_CmpLibVersion` 拒绝低版本启动。
- **价值**：替代 `F_GetVersionTcSystem` 的多次调用；一次拿到完整结构。
- **替代方案对比**：
  - `F_GetVersionTcSystem`：废弃，多次调用且只能拿 3 个字段。
  - 手工记录在文档：易过期、不可信。

## 8. 参考资料

- **PDF**：[TwinCAT_3_PLC_Lib_Tc2_System_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_System_EN.pdf) §6.2
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tcplclib_tc2_system/31086731.html
- **相关 FB / FC**：`F_CmpLibVersion`, `F_GetVersionTcSystem`, `Constants`
