# stLibVersion_Tc2_MC2

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc2_MC2` |
| Library Version | `2.17.0` |
| Type | `VAR_GLOBAL CONSTANT` |
| Category | `Library version` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_MC2_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tcplclib_tc2_mc2/70173195.html |
| Verified | 2026-05-21 ✅ |
| InfoSys-checked | ✅ 2026-05-21 |
| Status | `verified` |
| Example | [`examples/P_Demo_stLibVersion_Tc2_MC2.TcPOU`](../examples/P_Demo_stLibVersion_Tc2_MC2.TcPOU) |

---


## 1. 功能简述

`stLibVersion_Tc2_MC2` 是 `Tc2_MC2` 库的**版本信息全局常量**，类型为 `ST_LibVersion`（定义在 `Tc2_System` 库）。在 PLC 项目里引用该常量可在运行时读取自己实际链接的 `Tc2_MC2` 版本，配合 `F_CmpLibVersion`（同样来自 `Tc2_System`）做"必须 ≥ x.y.z 才允许运行"这类版本守卫。

PLC 库仓库（Library Repository）里能看到所有库的版本，这是工程文件外的"运行时自描述"机制。

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
    stLibVersion_Tc2_MC2 : ST_LibVersion;
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `stLibVersion_Tc2_MC2` | `ST_LibVersion` | `Tc2_MC2` 库的版本信息常量（major/minor/build/revision 等字段，定义在 `Tc2_System`） |

## 3. 行为说明

该常量在编译期由 TwinCAT 把当前链接版本写入；运行时只读。用法是"读出来 + 与期望版本比对"：

```iecst
IF NOT F_CmpLibVersion(stLibVersion_Tc2_MC2, 2, 17, 0, '>=' ) THEN
    // 实际 Tc2_MC2 版本低于 2.17.0，禁止启动机器
    bMachineEnable := FALSE;
END_IF;
```

`F_CmpLibVersion` 第二个起的 3 个数参数即 major、minor、build。第 5 个参数支持 `'='` `'<'` `'>'` `'<='` `'>='` `'<>'` 六种比较符。

**典型用法**：项目入口程序（`PRG_Init` 之类）开机第一步做一次"我用到的所有库都必须 ≥ 某版本"校验；不满足直接禁止运动控制使能。这避免了"开发机上用 2.17.0 编译 OK，部署到产线现场结果库版本 2.10 行为不一致"。

**典型陷阱**：从 TwinCAT 2 移植过来的旧代码习惯用 `LibVersion_*` / `GetLibVersion_*` 函数，**这些方式在 TwinCAT 3 已过时**——只用 `stLibVersion_<LibName>` 全局常量配 `F_CmpLibVersion`。

## 4. 错误码 / 返回值

GVL 无错误码。`F_CmpLibVersion` 比较失败仅返回 `FALSE`，不抛错。

## 5. 使用注意 / 常见坑

- **该常量编译期决定**，不会因运行时切换库版本而变化。改版本必须重新编译 PLC 项目。
- **跨库版本对比要逐库写**：项目用了 N 个库就要 N 次 `F_CmpLibVersion` 调用，每个库都有自己的 `stLibVersion_<Lib>`。
- **不要把 `ST_LibVersion` 当字符串比对**：它是结构体，直接 `=` 比对会比所有字段（含 `sVersion : STRING` 字面量），实际工程中只关心 major/minor/build 就够。（工程经验补充）
- **库版本回退要警惕**：TwinCAT 3 Library Repository 允许把一个项目"锁定"到某个旧版本（Placeholder），如果团队成员各自本地版本不同会出现"我这里跑得了你那里跑不了"，把版本检查写进开机自检可早暴露问题。（工程经验补充）

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_stLibVersion_Tc2_MC2.TcPOU`](../examples/P_Demo_stLibVersion_Tc2_MC2.TcPOU)
>
> 导入步骤：右键 PLC 项目下 POUs 文件夹 → Add → Existing Item → 选该文件 → OK

```iecst
PROGRAM P_Demo_stLibVersion_Tc2_MC2
VAR
    bMC2VersionOK : BOOL;
    sCurrentVersion : STRING(20);
END_VAR

// 要求 Tc2_MC2 至少为 2.17.0；低版本则禁止启动机器
bMC2VersionOK := F_CmpLibVersion(stLibVersion_Tc2_MC2, 2, 17, 0, '>=');
sCurrentVersion := stLibVersion_Tc2_MC2.sVersion;
```

## 7. 业务场景与实际价值

- **场景**：现场调试人员替换了 Tc2_MC2 库版本但忘记更新机器程序 / 测试机和量产机库版本不一致 / OEM 把同一 PLC 程序部署给多家集成商但要求某些 FB 必须新版本才支持。开机自检读 `stLibVersion_Tc2_MC2` 并比对预期版本是"防呆"的关键。
- **价值**：一行代码做版本检查 vs 写一段 ADS 调用查询 Library Repository。前者编译期注入、运行时几乎零开销；后者要 ADS RPC。
- **替代方案对比**：
  - 写死字符串比对：脆弱，版本号格式 Beckhoff 改一次就坏
  - 直接读 Library Repository：要走 ADS，开机时序复杂
  - **本常量 + `F_CmpLibVersion`**：标准做法，PLCopen 项目通用

## 8. 参考资料

- **PDF**：[TwinCAT_3_PLC_Lib_Tc2_MC2_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_MC2_EN.pdf) §8.1
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tcplclib_tc2_mc2/70173195.html
- **相关 FB**：`F_CmpLibVersion`（`Tc2_System`，做版本比较）、`ST_LibVersion`（`Tc2_System`，结构体定义）
