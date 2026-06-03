# Global_Version

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc2_ModbusRTU` |
| Library Version | `1.4.3` |
| Type | `VAR_GLOBAL CONSTANT` |
| Category | `Global Constants` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TF6255_TC3_Modbus_RTU_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tf6255_tc3_modbus_rtu/186549771.html |
| Verified | 2026-06-02 ✅ |
| InfoSys-checked | ✅ 2026-06-02 |
| Status | `verified` |
| Example | [`examples/P_Demo_Global_Version.TcPOU`](../examples/P_Demo_Global_Version.TcPOU) |

---

## 1. 功能简述

Tc2_ModbusRTU 库的版本号常量所在的全局变量列表（GVL）。所有 PLC 库都带一个版本号（在 PLC 库仓库等处可见），本库用一个全局常量 `stLibVersion_Tc2_Modbus_RTU`（类型 `ST_LibVersion`，结构体，来自 `Tc2_System`，含 `iMajor` / `iMinor` / `iBuild` / `iRevision` / `sVersion` 等字段）暴露该版本。要检查手头版本是否满足需求，用 `Tc2_System` 库里定义的 `F_CmpLibVersion` 函数。这是 Beckhoff 所有 PLC 库的统一版本暴露机制——业务代码引用本常量即可知运行时实际加载的 Tc2_ModbusRTU 版本。

## 2. 接口定义

### 全局常量声明

```iecst
VAR_GLOBAL CONSTANT
    stLibVersion_Tc2_Modbus_RTU : ST_LibVersion;
END_VAR
```

| 名称 | 类型 | 默认值 | 说明 |
|---|---|---|---|
| `stLibVersion_Tc2_Modbus_RTU` | `ST_LibVersion` | 编译时由库内嵌 | Tc2_ModbusRTU 库版本结构。读取后可比较 / 显示 |

### `ST_LibVersion` 结构（来自 `Tc2_System`）

| 字段 | 类型 | 说明 |
|---|---|---|
| `iMajor` | `INT` | 主版本号（本库为 `1`） |
| `iMinor` | `INT` | 副版本号（本库为 `4`） |
| `iBuild` | `INT` | 构建号（本库为 `3`） |
| `iRevision` | `INT` | 修订号（典型 `0`） |
| `nFlags` | `BYTE` | 内部标志 |
| `sVersion` | `STRING(23)` | 完整版本字串（如 `'1.4.3.0'`） |

### 返回值

不适用——本条目是常量声明，非函数 / 方法。

## 3. 行为说明

**何时读取**：典型在 PLC 初始化阶段调一次 `F_CmpLibVersion`，比对版本是否 ≥ 业务要求的最低版本；不达标则报警或拒绝继续启动。例如要求 Tc2_ModbusRTU ≥ 1.4.0：

```iecst
IF F_CmpLibVersion(
       cmpFlags  := LIBVERCMP_EQ OR LIBVERCMP_HI,
       refVer    := (iMajor := 1, iMinor := 4, iBuild := 0, iRevision := 0,
                     nFlags := 0, sVersion := '1.4.0.0'),
       checkVer  := stLibVersion_Tc2_Modbus_RTU) THEN
    bLibOk := TRUE;
ELSE
    bLibOk := FALSE;
    // 触发报警，禁止继续
END_IF
```

**值的来源**：编译期由 Tc2_ModbusRTU 库的 .compiled-library 文件内嵌，不是运行时动态生成。重装了不同版本的 TF6255 后，PLC 重新编译，此常量自动更新。

**TwinCAT 2 兼容**：PDF §5.3.1 明确指出——你在 TwinCAT 2 里熟悉的其他版本比较方式都已过时（"All other options for comparing library versions, which you may know from TwinCAT 2, are outdated"），TC3 工程统一用本常量 + `F_CmpLibVersion`。

**典型陷阱**：把本常量当 STRING 用——它是结构体，要拿字串得读 `.sVersion` 字段；只比 `iMajor >= 1` 不够严谨，应用 `F_CmpLibVersion` 做完整多段比对；常量名是 `stLibVersion_Tc2_Modbus_RTU`（注意库名部分带下划线 `Tc2_Modbus_RTU`），别误写成 `Tc2_ModbusRTU`。

## 4. 错误码 / 返回值

不适用——常量声明，无返回值/错误码。版本比较的结果由 `Tc2_System` 的 `F_CmpLibVersion` 以 `BOOL` 返回（详见该函数文档）。

## 5. 使用注意 / 常见坑

- **永远不要写入本常量**：是 `CONSTANT`，写入会编译报错。
- **`F_CmpLibVersion` 的 `cmpFlags` 用法**：组合 `LIBVERCMP_EQ` / `LIBVERCMP_HI` / `LIBVERCMP_LO`；常用 `EQ OR HI` 即「版本 ≥ ref」。详见 `Tc2_System` 的 `F_CmpLibVersion` 文档。
- **跨库版本检查写一坨**：业务代码常把多个库的版本检查放一起，统一在初始化跑；任一不达标就拒启动并向 HMI 报错。
- **`.sVersion` 字段长度**：`STRING(23)` 够装 `x.y.z.w`；要稳妥比较还是用 INT 字段。
- **常量名带下划线**：`stLibVersion_Tc2_Modbus_RTU`，与库名标识 `Tc2_ModbusRTU` 写法不同（库名部分是 `Tc2_Modbus_RTU`），跨库统一检查时容易写错。（工程经验补充）

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_Global_Version.TcPOU`](../examples/P_Demo_Global_Version.TcPOU)
>
> 导入步骤：右键 PLC 项目下 POUs 文件夹 → Add → Existing Item → 选该文件 → OK

```iecst
// 场景：PLC 初始化时检查 Tc2_ModbusRTU ≥ 1.4.0，否则报警拒启动。
PROGRAM P_Demo_Global_Version
VAR
    bInit            : BOOL := TRUE;
    bLibVersionOk    : BOOL;
    sActualVersion   : STRING(23);
END_VAR

IF bInit THEN
    bInit := FALSE;
    // 读出字串版本便于 HMI 显示
    sActualVersion := stLibVersion_Tc2_Modbus_RTU.sVersion;
    // 简化的就地判断（生产代码建议改用 Tc2_System 的 F_CmpLibVersion 做完整比对）
    bLibVersionOk := stLibVersion_Tc2_Modbus_RTU.iMajor > 1
        OR (stLibVersion_Tc2_Modbus_RTU.iMajor = 1
            AND stLibVersion_Tc2_Modbus_RTU.iMinor >= 4);
END_IF
```

## 7. 业务场景与实际价值

- **场景**：PLC 工程依赖 Tc2_ModbusRTU 某个最低版本的特性（例如 Generic 系列要求库 ≥ v3.5.6.0）；初始化校验，不达标就在 HMI 弹出「请升级 TF6255」。
- **价值**：把「运行时实际加载的库版本」暴露成可读常量，使业务代码能写出版本敏感的兼容逻辑，避免升级 TwinCAT 后某 FB 行为变化导致运行时静默故障。
- **替代方案对比**：
  - 不查版本：升级后某 FB 行为变化，运行时崩溃且无诊断。
  - 查 TwinCAT 系统版本：粒度太粗，无法精确到具体库。
  - **本常量 + `F_CmpLibVersion`**：精确到库的 4 段版本比对，Beckhoff 全库统一做法。

## 8. 参考资料

- **PDF**：[TF6255_TC3_Modbus_RTU_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TF6255_TC3_Modbus_RTU_EN.pdf) §5.3.1
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tf6255_tc3_modbus_rtu/186549771.html
- **相关**：`F_CmpLibVersion`（`Tc2_System`，比较函数）、`ST_LibVersion`（`Tc2_System`，结构体定义）
