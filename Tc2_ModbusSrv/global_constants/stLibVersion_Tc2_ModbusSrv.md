# stLibVersion_Tc2_ModbusSrv

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc2_ModbusSrv` |
| Library Version | `1.6.4` |
| Type | `VAR_GLOBAL CONSTANT` |
| Category | `Global constants` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TF6250_TC3_Modbus_TCP_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tf6250_tc3_modbus_tcp/192785931.html |
| Verified | 2026-06-02 ✅ |
| InfoSys-checked | ✅ 2026-06-02 |
| Status | `verified` |
| Example | [`examples/P_Demo_stLibVersion_Tc2_ModbusSrv.TcPOU`](../examples/P_Demo_stLibVersion_Tc2_ModbusSrv.TcPOU) |

---

## 1. 功能简述

Tc2_ModbusSrv 库的版本号常量。类型为 `ST_LibVersion`（结构体，来自 Tc2_System 库，含 `iMajor` / `iMinor` / `iBuild` / `iRevision` / `nFlags` / `sVersion` 等字段）。运行时用 Tc2_System 库的 `F_CmpLibVersion` 函数把本常量与“代码要求的最低版本”比对，决定是否报警或拒绝启动。这是 Beckhoff 所有 PLC 库统一的版本暴露机制——业务代码引用本常量即可得知运行时实际加载的 Tc2_ModbusSrv 版本。

## 2. 接口定义

### 全局常量声明

```iecst
VAR_GLOBAL CONSTANT
    stLibVersion_Tc2_ModbusSrv : ST_LibVersion;
END_VAR
```

| 名称 | 类型 | 默认值 | 说明（中文） |
|---|---|---|---|
| `stLibVersion_Tc2_ModbusSrv` | `ST_LibVersion` | 编译时由库内嵌 | Tc2_ModbusSrv 库版本结构；读取后可比较或显示 |

### `ST_LibVersion` 结构（来自 Tc2_System）

| 字段 | 类型 | 说明（中文） |
|---|---|---|
| `iMajor` | `INT` | 主版本号（本库为 `1`） |
| `iMinor` | `INT` | 副版本号（本库为 `6`） |
| `iBuild` | `INT` | 构建号（本库为 `4`） |
| `iRevision` | `INT` | 修订号 |
| `nFlags` | `BYTE` | 内部标志 |
| `sVersion` | `STRING(23)` | 完整版本字串（如 `'1.6.4.0'`） |

### VAR_IN_OUT

无——本条目是常量声明，非函数 / 方法。

## 3. 行为说明

**何时读取**：典型在 PLC 初始化阶段调用一次 `F_CmpLibVersion`，比对版本是否 ≥ 业务要求的最低版本；不达标则报警或拒绝继续启动。本常量是编译期由 Tc2_ModbusSrv 的 .compiled-library 内嵌的，不是运行时动态生成；若重装了不同版本的 TF6250 并重新编译工程，此常量随之更新。

**TwinCAT 2 兼容性**：PDF §6.3.1 明确指出“TwinCAT 2 库的查询方式已不再可用（Query options for TwinCAT 2 libraries are no longer available）”——TC3 工程统一使用本常量 + `F_CmpLibVersion` 做版本比对。

**典型陷阱**：把本常量当 `STRING` 直接用——它是结构体，要拿字串得读 `.sVersion` 字段；只比 `iMajor >= 1` 不够严谨，应使用 `F_CmpLibVersion` 做完整的多段比较。它是 `CONSTANT`，任何写入都是错误用法。

## 4. 错误码 / 返回值

不适用——本条目是常量声明，无返回值。

## 5. 使用注意 / 常见坑

- **永远不要写入本常量**：声明为 `CONSTANT`，写入会编译报错。
- **`F_CmpLibVersion` 的用法**：组合 `LIBVERCMP_EQ` / `LIBVERCMP_HI` / `LIBVERCMP_LO` 标志做比较；详见 Tc2_System 库的 `F_CmpLibVersion` 文档。
- **`.sVersion` 字段**：长度 `STRING(23)`，够装 `xxx.yyy.zzz.www` 格式；要做精确比较仍建议用 `iMajor`/`iMinor`/`iBuild` 整数字段。
- **跨库统一校验（工程经验补充）**：工程常把多个库的版本检查集中在初始化阶段执行，任一不达标即拒启动并向 HMI 报错。

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_stLibVersion_Tc2_ModbusSrv.TcPOU`](../examples/P_Demo_stLibVersion_Tc2_ModbusSrv.TcPOU)
>
> 导入步骤：右键 PLC 项目下 POUs 文件夹 → Add → Existing Item → 选该文件 → OK

```iecst
PROGRAM P_Demo_stLibVersion_Tc2_ModbusSrv
VAR
    bInit          : BOOL := TRUE;
    bLibVersionOk  : BOOL;
    sActualVersion : STRING(23);
END_VAR

IF bInit THEN
    bInit := FALSE;
    sActualVersion := stLibVersion_Tc2_ModbusSrv.sVersion;       // HMI 显示用
    bLibVersionOk  := stLibVersion_Tc2_ModbusSrv.iMajor > 1
        OR (stLibVersion_Tc2_ModbusSrv.iMajor = 1
            AND stLibVersion_Tc2_ModbusSrv.iMinor >= 6);
END_IF
```

## 7. 业务场景与实际价值

- **场景**：工程要求 Tc2_ModbusSrv ≥ 某版本（确保某些 FB 行为一致）；初始化时校验，不达标即在 HMI 提示“请升级 TF6250”。
- **价值**：把运行时实际加载的库版本暴露成可读常量，使业务代码能写版本敏感的兼容逻辑，避免升级后行为变化导致的隐性故障。
- **替代方案对比**：不查版本——升级后某 FB 行为变化、运行时故障且无诊断；查 TwinCAT 系统版本——粒度太粗，无法精确到具体库。

## 8. 参考资料

- **PDF**：[TF6250_TC3_Modbus_TCP_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TF6250_TC3_Modbus_TCP_EN.pdf) §6.3.1
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tf6250_tc3_modbus_tcp/192785931.html
- **相关**：`F_CmpLibVersion`（Tc2_System，比较函数）、`ST_LibVersion`（Tc2_System，结构体定义）
