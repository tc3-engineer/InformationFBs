# stLibVersion_Tc3_DriveMotionControl

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc3_DriveMotionControl` |
| Library Version | `1.5.5` |
| Type | `VAR_GLOBAL CONSTANT` |
| Category | `Library version` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc3_DriveMotionControl_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tcplclib_tc3_drivemotioncontrol/8281686539.html |
| Verified | 2026-06-02 ✅ |
| InfoSys-checked | ✅ 2026-06-02 |
| Status | `verified` |
| Example | [`examples/P_Demo_stLibVersion_Tc3_DriveMotionControl.TcPOU`](../examples/P_Demo_stLibVersion_Tc3_DriveMotionControl.TcPOU) |

---

## 1. 功能简述

`stLibVersion_Tc3_DriveMotionControl` 是 `Tc3_DriveMotionControl` 库的**版本信息全局常量**，类型为 `ST_LibVersion`（定义在 `Tc2_System` 库）。在 PLC 项目里引用该常量可在运行时读取自己实际链接的 `Tc3_DriveMotionControl` 版本。

配合 `F_CmpLibVersion`（同样来自 `Tc2_System`）可做"必须 ≥ x.y.z 才允许运行"这类版本守卫。库版本也可在 PLC 库仓库（Library Repository）里查看——本常量是工程文件之外的"运行时自描述"机制。

## 2. 接口定义

### VAR_INPUT

无（GVL 没有输入参数）。

### VAR_OUTPUT

无（GVL 没有输出参数）。

### VAR_IN_OUT

无。

### VAR_GLOBAL CONSTANT

```iecst
VAR_GLOBAL CONSTANT
    stLibVersion_Tc3_DriveMotionControl : ST_LibVersion;
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `stLibVersion_Tc3_DriveMotionControl` | `ST_LibVersion` | `Tc3_DriveMotionControl` 库的版本信息常量（含 major / minor / build / revision 等字段，结构体定义在 `Tc2_System`） |

## 3. 行为说明

该常量在编译期由 TwinCAT 把当前链接版本写入，运行时只读。典型用法是"读出来 + 与期望版本比对"：

```iecst
IF NOT F_CmpLibVersion(stLibVersion_Tc3_DriveMotionControl, 1, 5, 5, '>=') THEN
    // 实际 Tc3_DriveMotionControl 版本低于 1.5.5，禁止启动机器
    bMachineEnable := FALSE;
END_IF;
```

`F_CmpLibVersion` 第二个起的 3 个数参数即 major、minor、build。第 5 个参数支持 `'='` `'<'` `'>'` `'<='` `'>='` `'<>'` 六种比较符。

**典型用法**：项目入口程序开机第一步做一次"我用到的所有库都必须 ≥ 某版本"校验；不满足直接禁止运动使能。这避免了"开发机上用某版本编译 OK，部署到现场结果库版本不同、行为不一致"的隐患。

**典型陷阱**：从 TwinCAT 2 移植过来的旧代码习惯用 `LibVersion_*` / `GetLibVersion_*` 函数，**这些方式在 TwinCAT 3 已过时**——TwinCAT 3 只用 `stLibVersion_<LibName>` 全局常量配 `F_CmpLibVersion`。PDF 在本节明确指出"从 TwinCAT 2 你可能知道的所有其它版本比对方式都已过时"。

## 4. 错误码 / 返回值

GVL 无错误码。`F_CmpLibVersion` 比较失败仅返回 `FALSE`，不抛错。

| 返回值 / 错误码 | 含义 | 处理建议 |
|---|---|---|
| `F_CmpLibVersion` = `TRUE` | 版本满足比较条件 | 允许后续逻辑运行 |
| `F_CmpLibVersion` = `FALSE` | 版本不满足 | 禁止启动 / 给出版本不符提示 |

## 5. 使用注意 / 常见坑

- **该常量编译期决定**，不会因运行时切换库版本而变化。改版本必须重新编译 PLC 项目。
- **跨库版本对比要逐库写**：项目用了 N 个库就要 N 次 `F_CmpLibVersion` 调用，每个库都有自己的 `stLibVersion_<Lib>`。
- **不要把 `ST_LibVersion` 当字符串比对**：它是结构体，直接 `=` 比对会比所有字段（含 `sVersion : STRING` 字面量），实际工程只关心 major / minor / build 就够。（工程经验补充）
- **TwinCAT 2 旧式版本函数已过时**：只用 `stLibVersion_<Lib>` + `F_CmpLibVersion`，这是 PDF 明确要求的方式。

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_stLibVersion_Tc3_DriveMotionControl.TcPOU`](../examples/P_Demo_stLibVersion_Tc3_DriveMotionControl.TcPOU)
>
> 导入步骤：右键 PLC 项目下 POUs 文件夹 → Add → Existing Item → 选该文件 → OK

```iecst
PROGRAM P_Demo_stLibVersion_Tc3_DriveMotionControl
VAR
    bDmcVersionOK   : BOOL;
    sCurrentVersion : STRING(20);
END_VAR

// 要求 Tc3_DriveMotionControl 至少为 1.5.5；低版本则禁止启动机器
bDmcVersionOK   := F_CmpLibVersion(stLibVersion_Tc3_DriveMotionControl, 1, 5, 5, '>=');
sCurrentVersion := stLibVersion_Tc3_DriveMotionControl.sVersion;
```

## 7. 业务场景与实际价值

- **场景**：现场调试人员替换了库版本但忘记更新机器程序；测试机和量产机库版本不一致；OEM 把同一 PLC 程序部署给多家集成商但要求某些 FB 必须新版本才支持。开机自检读 `stLibVersion_Tc3_DriveMotionControl` 并比对预期版本是"防呆"的关键。
- **价值**：一行代码做版本检查 vs 写一段 ADS 调用查询 Library Repository。前者编译期注入、运行时几乎零开销；后者要 ADS RPC、开机时序复杂。
- **替代方案对比**：
  - 写死字符串比对：脆弱，版本号格式 Beckhoff 改一次就坏
  - 直接读 Library Repository：要走 ADS，开机时序复杂
  - **本常量 + `F_CmpLibVersion`**：TwinCAT 3 标准做法，PLCopen 项目通用

## 8. 参考资料

- **PDF**：[TwinCAT_3_PLC_Lib_Tc3_DriveMotionControl_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc3_DriveMotionControl_EN.pdf) §8.1
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tcplclib_tc3_drivemotioncontrol/8281686539.html
- **相关 FB / 类型**：`F_CmpLibVersion`（`Tc2_System`，做版本比较）、`ST_LibVersion`（`Tc2_System`，结构体定义）
