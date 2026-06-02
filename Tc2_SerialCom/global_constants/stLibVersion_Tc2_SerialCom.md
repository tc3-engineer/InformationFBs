# stLibVersion_Tc2_SerialCom

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc2_SerialCom` |
| Library Version | `1.8.1` |
| Type | `VAR_GLOBAL CONSTANT` |
| Category | `Global constants` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TF6340_TC3_Serial_Communication_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tf6340_tc3_serial_communication/85938699.html |
| Verified | 2026-06-02 ✅ |
| InfoSys-checked | ✅ 2026-06-02 |
| Status | `verified` |
| Example | [`examples/P_Demo_stLibVersion_Tc2_SerialCom.TcPOU`](../examples/P_Demo_stLibVersion_Tc2_SerialCom.TcPOU) |

---

## 1. 功能简述

Tc2_SerialCom 库的版本号常量，类型为 `ST_LibVersion`（结构体，来自 Tc2_System，含 `iMajor` / `iMinor` / `iBuild` / `iRevision` / `sVersion` 等字段）。库版本号会显示在 PLC 库的仓库里，并存放在这个全局常量中。运行时用 Tc2_System 库的 `F_CmpLibVersion` 函数把本常量与"代码要求的最低版本"做比对。这是 Beckhoff 所有 PLC 库统一的版本暴露机制。

## 2. 接口定义

### 全局常量声明

```iecst
VAR_GLOBAL CONSTANT
    stLibVersion_Tc2_SerialCom : ST_LibVersion;
END_VAR
```

| 名称 | 类型 | 默认值 | 说明 |
|---|---|---|---|
| `stLibVersion_Tc2_SerialCom` | `ST_LibVersion` | 编译时由库内嵌 | Tc2_SerialCom 库的版本号结构体 |

### `ST_LibVersion` 结构（来自 Tc2_System）

| 字段 | 类型 | 说明 |
|---|---|---|
| `iMajor` | `INT` | 主版本号（本库为 `1`） |
| `iMinor` | `INT` | 副版本号（本库为 `8`） |
| `iBuild` | `INT` | 构建号（本库为 `1`） |
| `iRevision` | `INT` | 修订号 |
| `sVersion` | `STRING` | 完整版本字串（如 `'1.8.1'`） |

### 返回值

不适用——本条目是常量声明，非函数 / 方法。

## 3. 行为说明

这是一个编译期内嵌的只读全局常量，不是运行时动态生成：值在编译时由 Tc2_SerialCom 库的 .compiled-library 文件内嵌；重装不同版本的 TF6340 后 PLC 重新编译，此常量自动更新为新版本。典型用法是在 PLC 初始化阶段调一次 Tc2_System 的 `F_CmpLibVersion`，把本常量与业务要求的最低版本比对，不达标则报警或拒绝启动。PDF 第 5.4.1 节明确："与 TwinCAT 2 的兼容——TwinCAT 2 库的查询选项不再可用"，即 TC3 工程统一用本常量 + `F_CmpLibVersion`，不再支持旧 TC2 的查询方式。读取版本时既可读 `sVersion`（字串，便于 HMI 显示），也可读 `iMajor` / `iMinor` / `iBuild`（整型，便于精确比较），但严谨的版本判断应交给 `F_CmpLibVersion` 做完整比对，而非手工比单个字段。

## 4. 错误码 / 返回值

不适用——常量声明，无错误码 / 返回值。

## 5. 使用注意 / 常见坑

- **永远不要写入本常量**：它是 `CONSTANT`，写入会编译报错。
- **它是结构体不是字符串**：要拿版本字串读 `.sVersion` 字段；直接当 `STRING` 用会类型错误。
- **严谨比较用 `F_CmpLibVersion`**：手工比 `iMajor >= 1` 不够严谨，应组合 `LIBVERCMP_EQ` / `LIBVERCMP_HI` 等标志用 `F_CmpLibVersion` 做完整 4 段比对（见 Tc2_System）。
- **版本检查放初始化**：通常在 PLC 启动阶段统一校验各库版本，任一不达标就拒启动并向 HMI 报错（工程经验补充）。

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_stLibVersion_Tc2_SerialCom.TcPOU`](../examples/P_Demo_stLibVersion_Tc2_SerialCom.TcPOU)

```iecst
// 场景：PLC 初始化时检查 Tc2_SerialCom 版本，HMI 显示版本字串。
PROGRAM P_Demo_stLibVersion_Tc2_SerialCom
VAR
    bInit          : BOOL := TRUE;
    sActualVersion : STRING;
    iActualMajor   : INT;
END_VAR

IF bInit THEN
    bInit := FALSE;
    sActualVersion := stLibVersion_Tc2_SerialCom.sVersion;   // 如 '1.8.1'
    iActualMajor   := stLibVersion_Tc2_SerialCom.iMajor;     // 1
END_IF
```

## 7. 业务场景与实际价值

- **场景**：工程要求 Tc2_SerialCom ≥ 某版本（才有某些功能块或修复），初始化时校验，不达标在 HMI 提示"请升级 TF6340"。
- **价值**：把运行时实际加载的库版本暴露成可读常量，使业务代码能写版本敏感的兼容逻辑、避免在旧库上调用新符号导致运行时故障。
- **替代方案对比**：不查版本——升级后某功能块行为变化会在运行时出问题且无诊断；查 TwinCAT 系统版本——粒度太粗，无法精确到具体库。

## 8. 参考资料

- **PDF**：[TF6340_TC3_Serial_Communication_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TF6340_TC3_Serial_Communication_EN.pdf) §5.4.1
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tf6340_tc3_serial_communication/85938699.html
- **相关**：`F_CmpLibVersion`（Tc2_System，版本比较函数）、`ST_LibVersion`（Tc2_System，结构体定义）
