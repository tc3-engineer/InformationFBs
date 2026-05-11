# stLibVersion_Tc2_Coupler

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc2_Coupler` |
| Library Version | `1.1.1` |
| Type | `VAR_GLOBAL CONSTANT` |
| Category | `Library version` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_Coupler_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tcplclib_tc2_coupler/42582795.html |
| Verified | 2026-05-11 ✅ |
| InfoSys-checked | ⚠️ not-on-infosys |
| Status | `verified` |
| Example | [`examples/P_Demo_stLibVersion_Tc2_Coupler.xml`](../examples/P_Demo_stLibVersion_Tc2_Coupler.xml) |

---

## 1. 功能简述

Tc2_Coupler 库的**版本信息全局常量**。本常量是 `ST_LibVersion` 结构体类型，库内编译时固化，包含 major / minor / build / revision 四个 `INT` 字段以及一个 `STRING` 形式的版本字符串。任意 PLC 程序都可以直接 `stLibVersion_Tc2_Coupler.iMajor` 取出主版本号，不需要调用任何函数。

**用途**：运行时检查"工程依赖的 Tc2_Coupler 库版本"是否满足业务的最低要求。配合 Tc2_System 库提供的 `F_CmpLibVersion` 函数可以一次比较"是否 ≥ x.y.z"等条件。是 TwinCAT 3 中**推荐的版本检查方式**——替代已废弃的 `F_GetVersionTcPlcCoupler`。

**与 TwinCAT 2 的关系**：PDF §6.1 明确写 "All other options for comparing library versions, which you may know from TwinCAT 2, are outdated"——TwinCAT 2 时代的版本比较 API（包括本库的 obsolete `F_GetVersionTcPlcCoupler`）都已淘汰；统一用 `stLibVersion_*` + `F_CmpLibVersion`。

## 2. 接口定义

### VAR_GLOBAL CONSTANT

```iecst
VAR_GLOBAL CONSTANT
    stLibVersion_Tc2_Coupler : ST_LibVersion;
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `stLibVersion_Tc2_Coupler` | `ST_LibVersion` | Tc2_Coupler 库的版本信息。`ST_LibVersion` 定义在 Tc2_System，含 `iMajor` / `iMinor` / `iBuild` / `iRevision`（均 `INT`）和 `sVersion`（`STRING`） |

### 当前版本

对 Tc2_Coupler 1.1.1（本次抓取的 PDF 版本，2024-09-11 发布）：
- `iMajor`    = 1
- `iMinor`    = 1
- `iBuild`    = 1
- `iRevision` = 0
- `sVersion`  ≈ `'1.1.1.0'`（字符串形式具体格式以库实际定义为准）

### VAR_OUTPUT

不适用（全局常量，非 FB / 非 FC）。

### VAR_IN_OUT

不适用。

## 3. 行为说明

**访问语义**：本常量是**编译期固化**的——库工程师在打包库时把版本号写死进 ST_LibVersion 字段，所有引用本库的 PLC 工程在编译时看到的是同一个值，**运行时不能被修改**（IEC 61131 的 `VAR_GLOBAL CONSTANT` 语义）。

**典型使用模式**：
1. **启动时一次性校验**：在 `MAIN` 或 init 程序里调用一次 `F_CmpLibVersion(stLibVersion := stLibVersion_Tc2_Coupler, iMajor:=1, iMinor:=1, ..., nCmpType:=E_CmpLibVersion.GreaterOrEqual)`；不满足就拒绝启动业务任务、点亮报警灯。
2. **HMI 显示**：把 `stLibVersion_Tc2_Coupler.sVersion` 直接打出来显示在"关于"页面，方便现场维护查看当前装的是哪个库版本。
3. **诊断归档**：把版本号写入运行日志，便于事后查"工程当时跑的是 Tc2_Coupler 哪个版本"。

**与 obsolete `F_GetVersionTcPlcCoupler` 的迁移对照**：
| 老 API（obsolete） | 新 API（推荐） |
|---|---|
| `F_GetVersionTcPlcCoupler(1)` 返回 `UINT` major | `stLibVersion_Tc2_Coupler.iMajor` 返回 `INT` |
| `F_GetVersionTcPlcCoupler(2)` 返回 `UINT` minor | `stLibVersion_Tc2_Coupler.iMinor` |
| `F_GetVersionTcPlcCoupler(3)` 返回 `UINT` revision | `stLibVersion_Tc2_Coupler.iRevision` |
| 自己写 `IF` 链做范围比较 | `F_CmpLibVersion(stLibVersion := stLibVersion_Tc2_Coupler, ..., nCmpType := ...)` |

注意类型差异：老 API 返 `UINT`、新 API 字段是 `INT`；迁移时若代码里直接做无符号大小比较，要看清是否有强制转换的必要。

## 4. 错误码 / 返回值

无错误码（全局常量声明，编译期固化、运行时只读）。

如果调用 `F_CmpLibVersion` 失败（极少见，例如 `nCmpType` 传了无效枚举值），返回 `FALSE`；具体见 Tc2_System 文档。

## 5. 使用注意 / 常见坑

- **新代码必须用本常量、不要再用 `F_GetVersionTcPlcCoupler`**。后者已被 Beckhoff 官方标 obsolete，未来某版本可能被删除导致编译失败。
- **必须引用 Tc2_System 才能用 `F_CmpLibVersion` / `E_CmpLibVersion`**。`ST_LibVersion` 也定义在 Tc2_System；仅引用 Tc2_Coupler 时类型存在但找不到比较函数。在 PLC 工程的 References 节点加 Tc2_System 即可。
- **本常量是"PLC 库版本"，不是"耦合器固件版本"**。它表示工程依赖的 Tc2_Coupler 库本身打包时的版本号，与挂载的 BK / BC 硬件固件、端子固件**完全无关**。要读耦合器固件版本须调 `FB_ReadCouplerRegs` 读 terminal 0 的对应寄存器。新人最容易混淆这一点。（工程经验补充）
- **`F_CmpLibVersion` 的 `nCmpType` 默认非"GreaterOrEqual"**。`E_CmpLibVersion` 枚举里还有 `Equal` / `Less` / `LessOrEqual` / `Greater` / `NotEqual`；如果业务是"必须正好 = 1.1.0"和"≥ 1.1.0"语义差很多——前者升级库后会主动断启动，后者向后兼容更好。新代码推荐 `GreaterOrEqual`。（工程经验补充）
- **运行时常量是编译期定值，不会随 NuGet / Library Manager 升库自动反映**：升库后必须**重编工程**才能看到新版本号。在线 monitor 看不到 0 ms 内更新。
- **`sVersion` 字符串格式可能因库版本微调**：例如老版本是 `"1.1.0.0"`、新版本可能是 `"1.1.1"` 缺尾巴。HMI 显示时建议先做模糊匹配（取前 3 段数字），别假定固定 4 段格式。

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_stLibVersion_Tc2_Coupler.xml`](../examples/P_Demo_stLibVersion_Tc2_Coupler.xml)（PLCopenXML，可直接导入 TwinCAT 3 XAE）
>
> 导入步骤：右键 PLC 项目 → Import PLCopenXML → 选该文件 → OK
> 详见 [`examples/README.md`](../examples/README.md)

```iecst
// 场景：本工程依赖 Tc2_Coupler ≥ 1.1.1（因为低版本不支持某新增端子的 user
//       scaling 寄存器）。在 MAIN 启动时校验当前装的库版本是否满足要求，
//       不满足就拒绝启动业务任务、点亮报警灯，并把版本字符串送 HMI 显示。
//
// 价值：替代已废弃的 F_GetVersionTcPlcCoupler；用 ST_LibVersion 结构化访问 +
//       F_CmpLibVersion 内置比较，比手写 IF 链更清晰、向后兼容更好。
//
// 验证：登录后观察 nMajor / nMinor / nBuild / nRevision 应为 1 / 1 / 1 / 0；
//       bLibVersionOk 应为 TRUE；把 nRequiredMinor 改成 9 → bLibVersionOk
//       立刻变 FALSE，bBusinessTaskAllowed 也变 FALSE。
PROGRAM P_Demo_stLibVersion_Tc2_Coupler
VAR
    // —— 直接读取版本号字段供 HMI / 日志 ——
    nMajor              : INT;
    nMinor              : INT;
    nBuild              : INT;
    nRevision           : INT;
    sLibVersionForHmi   : STRING(40);

    // —— 业务对库版本的最低要求 ——
    nRequiredMajor      : INT := 1;
    nRequiredMinor      : INT := 1;
    nRequiredBuild      : INT := 1;
    nRequiredRevision   : INT := 0;

    // —— 校验结果 ——
    bLibVersionOk           : BOOL;
    bBusinessTaskAllowed    : BOOL;
END_VAR

// 直接取字段——纯只读访问，无副作用
nMajor    := stLibVersion_Tc2_Coupler.iMajor;
nMinor    := stLibVersion_Tc2_Coupler.iMinor;
nBuild    := stLibVersion_Tc2_Coupler.iBuild;
nRevision := stLibVersion_Tc2_Coupler.iRevision;
sLibVersionForHmi := stLibVersion_Tc2_Coupler.sVersion;

// 用 F_CmpLibVersion 做范围比较；需要引用 Tc2_System
bLibVersionOk := F_CmpLibVersion(
    stLibVersion := stLibVersion_Tc2_Coupler,
    iMajor       := nRequiredMajor,
    iMinor       := nRequiredMinor,
    iBuild       := nRequiredBuild,
    iRevision    := nRequiredRevision,
    nCmpType     := E_CmpLibVersion.GreaterOrEqual
);

// 不满足版本要求就拒绝启动业务任务
bBusinessTaskAllowed := bLibVersionOk;
```

## 7. 业务场景与实际价值

- **场景**：工程依赖某个 Tc2_Coupler 版本特有的功能 / bugfix，希望部署到不同现场时能在启动时自动校验当前库版本，不满足就主动报警而不是悄悄出 bug。也用于 HMI"关于"页面展示装的是哪个库版本，方便现场运维。
- **价值**：把"取版本号 + 范围比较"做成一行可读的标准化调用，替代 TwinCAT 2 时代的手写 IF 链。版本检查放在启动期做一次即可，开销忽略不计；但避免的潜在 bug 价值很大——尤其在多机部署、分布式工程中。
- **替代方案对比**：
  - obsolete `F_GetVersionTcPlcCoupler`：要 3 次函数调用、手写比较、未来可能被删除——不推荐
  - 编译期 `{attribute 'TcLibCheck'}` pragma：编译期就报错、比运行时更早；但灵活性低，且不能基于版本走分支逻辑
  - 不做版本检查：现场出 bug 后才发现库版本不对，定位耗时
  - **本常量 + F_CmpLibVersion**：**推荐**，TwinCAT 3 标准做法

## 8. 参考资料

- **PDF**：[TwinCAT_3_PLC_Lib_Tc2_Coupler_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_Coupler_EN.pdf) §6.1 "Library version"
- **InfoSys topic**：⚠️ Tc2_Coupler 的 "Library version" 章节在 InfoSys 上没有独立 topic 页（Beckhoff 的小库通常省略这页）；最相近的入口是库总览 https://infosys.beckhoff.com/content/1033/tcplclib_tc2_coupler/42582795.html。其它库（Tc2_System / Tc2_Utilities / Tc2_SUPS）的 "Library version" 章节互相结构一致，可参考。
- **相关**：`ST_LibVersion`（Tc2_System，本常量的类型定义）、`F_CmpLibVersion`（Tc2_System，比较函数）、`E_CmpLibVersion`（Tc2_System，比较类型枚举：`Equal` / `GreaterOrEqual` / `Less` 等）、`F_GetVersionTcPlcCoupler`（同库 §4.1，已 obsolete，本常量的替代品）
