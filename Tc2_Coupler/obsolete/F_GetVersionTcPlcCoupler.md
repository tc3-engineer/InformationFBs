# F_GetVersionTcPlcCoupler

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc2_Coupler` |
| Library Version | `1.1.1` |
| Type | `FUNCTION` |
| Category | `[obsolete functions]` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_Coupler_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tcplclib_tc2_coupler/42582795.html |
| Verified | 2026-05-11 ✅ |
| InfoSys-checked | ⚠️ not-on-infosys |
| Status | `verified · deprecated` |
| Example | [`examples/P_Demo_F_GetVersionTcPlcCoupler.TcPOU`](../examples/P_Demo_F_GetVersionTcPlcCoupler.TcPOU) |

---

## 1. 功能简述

⚠️ **本函数已废弃**——PDF §4.1 明确写 "This function is obsolete and should not be used any longer"。请改用全局常量 [`stLibVersion_Tc2_Coupler`](../global_constants/stLibVersion_Tc2_Coupler.md)（属于 `ST_LibVersion` 结构体），配合 Tc2_System 库的 `F_CmpLibVersion` 做运行时版本比较，这是 TwinCAT 3 当前推荐做法。

本函数的功能：传入 1 / 2 / 3 取库版本号的某一段——返回 major / minor / revision 数字（`UINT` 形式）。对应 Tc2_Coupler 1.1.1 调用 `F_GetVersionTcPlcCoupler(1)` 得 1、`F_GetVersionTcPlcCoupler(2)` 得 1、`F_GetVersionTcPlcCoupler(3)` 得 1。

仅在维护**从 TwinCAT 2 迁移过来的旧 PLC 程序**时还会遇到本函数——保持 API 兼容、暂时不重写版本检查代码可以继续用，新写代码不要再用。

## 2. 接口定义

### VAR_INPUT

```iecst
FUNCTION F_GetVersionTcPlcCoupler : UINT
VAR_INPUT
    nVersionElement : INT;
END_VAR
```

| 名称 | 类型 | 默认值 | 说明 |
|---|---|---|---|
| `nVersionElement` | `INT` | — | 要查询的版本元素号：`1` = major（主版本），`2` = minor（次版本），`3` = revision（修订号）。其它值返回 0 |

### 返回值

`UINT` —— 与 `nVersionElement` 对应的版本号数值。对 Tc2_Coupler 1.1.1：传 1 → 返回 1，传 2 → 返回 1，传 3 → 返回 1。传 4 或其它无效编号返回 0。

### VAR_IN_OUT

无。

## 3. 行为说明

**调用语义**：本函数是纯函数（无内部状态、无副作用），每次调用立即返回。可在任意 PLC 任务中调用。

**返回值规则**（PDF §4.1）：
- `nVersionElement = 1` → 返回 `major number`（主版本号）。Tc2_Coupler 1.1.1 返回 1。
- `nVersionElement = 2` → 返回 `minor number`（次版本号）。Tc2_Coupler 1.1.1 返回 1。
- `nVersionElement = 3` → 返回 `revision number`（修订号）。Tc2_Coupler 1.1.1 返回 1。
- 其它值：PDF 未明确，实测返回 0。

**与现代 API 的对比**：现代写法用 `stLibVersion_Tc2_Coupler : ST_LibVersion`，结构体里同时含 `iMajor`、`iMinor`、`iBuild`、`iRevision` 四个 `INT` 字段，无需调用函数、可一次性取到所有字段；而且配合 Tc2_System 的 `F_CmpLibVersion` 可以做"版本 ≥ x.y.z"这种范围比较，本 obsolete 函数做不到，只能逐字段取后自己写比较逻辑。

**迁移策略**：
1. 把 `F_GetVersionTcPlcCoupler(1)` 替换为 `stLibVersion_Tc2_Coupler.iMajor`；以此类推 2 → `iMinor`、3 → `iRevision`。
2. 把"自己手写大小比较"替换为 `F_CmpLibVersion(stLibVersion_Tc2_Coupler, iMajor:=1, iMinor:=1, iBuild:=1, iRevision:=0, nCmpType:=E_CmpLibVersion.GreaterOrEqual)`。
3. 移除对本函数的所有调用，避免新代码再依赖一个已废弃的接口。

## 4. 错误码 / 返回值

本函数无错误码——任何输入都返回 `UINT`。无效 `nVersionElement` 返回 0，调用方需自己识别"0 表示输入错误"还是"该字段确实是 0"（实际项目里 0.0.0 版本不存在，所以 0 等价于错误）。

## 5. 使用注意 / 常见坑

- **不要在新代码里用本函数**。Beckhoff 官方明示 obsolete，未来某个 Tc2_Coupler 版本可能整个删掉它，调用者会编译失败。新代码用 `stLibVersion_Tc2_Coupler`。
- **本函数无副作用、纯函数语义**：可在循环任务、init 段、IO 段任意位置调用。即便如此也建议只在 init / 上电诊断时调一次取值缓存，循环调没意义只会增加 PLC 任务负载（虽然代价很小）。
- **返回 `UINT` 而非 `INT`**：`UINT` 在 TwinCAT 是 16 位无符号，但 `stLibVersion_Tc2_Coupler` 字段是 `INT`（带符号）。从本函数迁移到 `stLibVersion_*` 时类型有变化，注意调用方代码里的强制类型转换。
- **`nVersionElement = 0` 与无效值都返回 0**：调用方不能用"返回 0"区分"我传错了"和"该字段就是 0"。这是本函数 API 设计上的小缺陷。
- **该函数不读 EEPROM / 硬件**：它只是把库内置的版本号常量翻译出来，与 BC / BK 耦合器硬件无关。是"PLC 库版本"而非"耦合器固件版本"——耦合器固件版本要去耦合器寄存器读（`FB_ReadCouplerRegs` 读 terminal 0 表）。（工程经验补充，避免新人混淆）
- **替换为 `stLibVersion_Tc2_Coupler` 时记得引用 Tc2_System**：因为 `ST_LibVersion`、`F_CmpLibVersion`、`E_CmpLibVersion` 都定义在 Tc2_System，工程里要把它加进 References。

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_F_GetVersionTcPlcCoupler.TcPOU`](../examples/P_Demo_F_GetVersionTcPlcCoupler.TcPOU)（TwinCAT 3 原生 .TcPOU，可直接拖入 XAE 的 PLC POUs 文件夹）
>
> 导入步骤：右键 PLC 项目下 POUs 文件夹 → Add → Existing Item → 选该文件 → OK
> 详见 [`examples/README.md`](../examples/README.md)

```iecst
// 场景：现有一个 TwinCAT 2 老程序里用 F_GetVersionTcPlcCoupler 校验 Tc2_Coupler
//       至少是 1.1.0 才允许 PLC 启动业务任务；现在迁到 TwinCAT 3 暂时不重写
//       这段逻辑，先让老代码继续跑通，并在旁边并行展示推荐的新写法对比。
//
// 价值：用 obsolete 函数对照"现代 ST_LibVersion + F_CmpLibVersion"的差别，
//       便于迁移老代码时一眼看出替换关系。新代码不要再用 obsolete 函数。
//
// 验证：登录后观察 nMajorOld / nMinorOld / nRevisionOld 应为 1 / 1 / 1（Tc2_Coupler
//       1.1.1）；bVersionOkLegacy 与 bVersionOkModern 应同时为 TRUE。把
//       nRequiredMajor 改成 2 → 两者同时变 FALSE，说明两条路径语义一致。
PROGRAM P_Demo_F_GetVersionTcPlcCoupler
VAR
    nMajorOld         : UINT;        // 老 API 读 major
    nMinorOld         : UINT;        // 老 API 读 minor
    nRevisionOld      : UINT;        // 老 API 读 revision
    bVersionOkLegacy  : BOOL;        // 老 API 手写比较结果

    bVersionOkModern  : BOOL;        // 推荐做法的结果（用 F_CmpLibVersion）

    // —— 业务策略 ——
    nRequiredMajor    : UINT := 1;
    nRequiredMinor    : UINT := 1;
    nRequiredRevision : UINT := 0;
END_VAR

// ========== Legacy 写法（迁移期保留，新代码不要写）==========
nMajorOld    := F_GetVersionTcPlcCoupler(1);
nMinorOld    := F_GetVersionTcPlcCoupler(2);
nRevisionOld := F_GetVersionTcPlcCoupler(3);

// 手写"≥ Required"比较逻辑，逐字段判断
bVersionOkLegacy := (nMajorOld > nRequiredMajor)
                  OR (nMajorOld = nRequiredMajor AND nMinorOld > nRequiredMinor)
                  OR (nMajorOld = nRequiredMajor AND nMinorOld = nRequiredMinor
                      AND nRevisionOld >= nRequiredRevision);

// ========== Modern 写法（推荐；需要引用 Tc2_System）==========
// 用 stLibVersion_Tc2_Coupler 一次取全部字段；F_CmpLibVersion 内置比较
bVersionOkModern := F_CmpLibVersion(
    stLibVersion := stLibVersion_Tc2_Coupler,
    iMajor       := INT#(nRequiredMajor),
    iMinor       := INT#(nRequiredMinor),
    iBuild       := 0,
    iRevision    := INT#(nRequiredRevision),
    nCmpType     := E_CmpLibVersion.GreaterOrEqual
);
```

## 7. 业务场景与实际价值

- **场景**：把 TwinCAT 2 时代用 `F_GetVersionTcPlcCoupler` 写的旧 PLC 程序迁到 TwinCAT 3 时，临时保留对本函数的调用以减少改动面；或在某个老库依赖必须 Tc2_Coupler ≥ x.y.z 时做兼容检查。新写代码**不该用**本函数。
- **价值**：迁移期的过渡 API，让 TwinCAT 2 代码无需立即重构即可在 TwinCAT 3 上编译运行。本函数本身没有"积极价值"——它只是历史遗留，价值在于"不立即破坏旧代码"。
- **替代方案对比**：
  - 本 obsolete 函数：每次返回单字段、要自己写比较、未来可能被库整个删除
  - `stLibVersion_Tc2_Coupler` + `F_CmpLibVersion`：**推荐**，结构化访问 + 内置 ≥ / ≤ / = 比较；TwinCAT 3 标准做法
  - 编译期 conditional pragma（`{attribute 'TcLibCheck' := ...}`）：编译期检查，比运行时更早发现版本问题，但灵活性低
  - **结论**：新代码直接用 `stLibVersion_Tc2_Coupler`；只有维护 TwinCAT 2 迁移过来的老代码才接触本函数

## 8. 参考资料

- **PDF**：[TwinCAT_3_PLC_Lib_Tc2_Coupler_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_Coupler_EN.pdf) §4.1（标记为 obsolete）
- **InfoSys topic**：⚠️ Beckhoff InfoSys 未为本 obsolete 函数单独建 topic 页；最相近的入口是 Tc2_Coupler 库总览 https://infosys.beckhoff.com/content/1033/tcplclib_tc2_coupler/42582795.html
- **替代品**：[`stLibVersion_Tc2_Coupler`](../global_constants/stLibVersion_Tc2_Coupler.md)（同库 §6.1）、`ST_LibVersion`（Tc2_System）、`F_CmpLibVersion`（Tc2_System）、`E_CmpLibVersion`（Tc2_System，比较枚举：`Equal` / `GreaterOrEqual` / ...）
