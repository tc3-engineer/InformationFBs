# F_GetVersionTcMath

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc2_Math` |
| Library Version | `1.3.3` |
| Type | `FUNCTION` |
| Category | `[obsolete functions]` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_Math_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tcplclib_tc2_math/68452363.html |
| Verified | 2026-05-11 ✅ |
| InfoSys-checked | ✅ 2026-05-11 |
| Status | `verified · deprecated` |
| Example | [`examples/P_Demo_F_GetVersionTcMath.xml`](../examples/P_Demo_F_GetVersionTcMath.xml) |

---

## 1. 功能简述

**已过时（obsolete）** 的版本号读取函数，由 TwinCAT 2 时代的 API 兼容性遗留。通过传入一个"版本字段编号"（major / minor / revision = 1 / 2 / 3），按 `UINT` 返回该字段的数值。

**新代码不应再使用本函数**：Beckhoff 在 TwinCAT 3 中统一改用全局常量 `stLibVersion_Tc2_Math` + 函数 `F_CmpLibVersion`（在 `Tc2_System`），既能拿到完整 4 字段（major / minor / build / revision）也能直接做版本比较。本函数仅保留以避免老工程编译失败，新工程引用本函数会被代码审查标红。

PDF 第 4 章把它归为 `[obsolete functions]`，明示弃用状态。

## 2. 接口定义

### VAR_INPUT

```iecst
FUNCTION F_GetVersionTcMath : UINT
VAR_INPUT
    nVersionElement : INT;
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `nVersionElement` | `INT` | 要读取的版本字段编号：`1` = major（主版本号）、`2` = minor（次版本号）、`3` = revision（修订号）。其他值的行为 PDF 未明说，⚠️ 不可依赖 |

### 返回值

| 类型 | 说明 |
|---|---|
| `UINT` | 指定字段的版本数值。例：库版本 `1.3.3` 时 `F_GetVersionTcMath(1) = 1`，`F_GetVersionTcMath(2) = 3`，`F_GetVersionTcMath(3) = 3`。`nVersionElement` 取值 `1..3` 之外时返回值 PDF 未规定，⚠️ 不可依赖 |

### VAR_OUTPUT

无（本符号是 `FUNCTION`）。

### VAR_IN_OUT

无。

## 3. 行为说明

**算法语义**：函数内部以编译期固化的方式把库版本号的 major / minor / revision 三个字段存入查表，按入参 `nVersionElement` 取对应的字段。这与一般用户编写的 PLC 代码"读取常量"语义相同，只是封装成 FC 形式。

**取值表**（基于库当前版本 `1.3.3`）：

| `nVersionElement` | 返回值 | 字段含义 |
|---|---|---|
| `1` | `1` | major |
| `2` | `3` | minor |
| `3` | `3` | revision |
| 其他 | ⚠️ 未定义 | PDF 未规定 |

**为什么弃用**：

- **只能拿 3 个字段**：现代 Beckhoff 库版本是 4 字段 `major.minor.build.revision`，本函数缺 `build`
- **每次调用要传魔法数 `1`/`2`/`3`**：可读性差、易写错
- **不能直接比较**：要判断"版本 ≥ 1.3.0" 还得自己写 3 段 `IF` 拼接，配合 `F_CmpLibVersion` 一行就完成
- **不能拿字符串表示**：现代 `stLibVersion_Tc2_Math.sVersion` 给 `'1.3.3.0'` 字符串方便 HMI 显示

**替代路径（强烈推荐）**：

```iecst
// 旧（弃用）
nMajor := F_GetVersionTcMath(1);
nMinor := F_GetVersionTcMath(2);
nRev   := F_GetVersionTcMath(3);

// 新（首选）
nMajor := stLibVersion_Tc2_Math.iMajor;
nMinor := stLibVersion_Tc2_Math.iMinor;
nBuild := stLibVersion_Tc2_Math.iBuild;    // 旧 API 拿不到
nRev   := stLibVersion_Tc2_Math.iRevision;

// 版本比较（旧 API 完全做不到，需自己写）
bOk := F_CmpLibVersion(
    stLibVersion := stLibVersion_Tc2_Math,
    iMajor := 1, iMinor := 3, iBuild := 0, iRevision := 0,
    nCmpType := E_CmpLibVersion.GreaterOrEqual
);
```

## 4. 错误码 / 返回值

本函数返回类型为 `UINT`，无错误码、无 `bError` 输出、无 `HRESULT`。返回值语义见 §2「返回值」表。

`nVersionElement` 越界（小于 1 或大于 3）时返回值 PDF / InfoSys 均未规定，⚠️ 实测可能返回 `0` 或其他未定义值，**不可依赖**。

## 5. 使用注意 / 常见坑

- **新代码勿用**：改用 `stLibVersion_Tc2_Math.iMajor` 等字段访问 + `F_CmpLibVersion` 比较。本函数仅为兼容 TwinCAT 2 老工程而保留。
- **没有 `build` 字段**：本函数无法读出 4 字段版本号的第三段。如果代码逻辑依赖区分 `1.3.2` 与 `1.3.3.5` 不同 build，本函数无能为力——必须改用 `stLibVersion_Tc2_Math.iBuild`。
- **魔法数易写错**：`F_GetVersionTcMath(2)` 比 `stLibVersion_Tc2_Math.iMinor` 可读性差太多，团队应在代码审查时一律打回。
- **不要在循环里反复调用**：版本是编译期常量，启动时取一次缓存即可，反复调用浪费 PLC 周期。
- **混用风险**：同一份代码若一部分用 `F_GetVersionTcMath`、一部分用 `stLibVersion_Tc2_Math`，库版本更新时容易遗漏其中一边导致行为不一致。（工程经验补充）
- **代码审查规则**：建议在团队规范里把 `F_GetVersionTcMath` 加入禁用 API 列表，提交时静态检查标红。（工程经验补充）

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_F_GetVersionTcMath.xml`](../examples/P_Demo_F_GetVersionTcMath.xml)（PLCopenXML，可直接导入 TwinCAT 3 XAE）
>
> 导入步骤：右键 PLC 项目 → Import PLCopenXML → 选该文件 → OK
> 详见 [`examples/README.md`](../examples/README.md)

```iecst
// 场景：老工程从 TwinCAT 2 迁移到 TwinCAT 3，原本代码用 F_GetVersionTcMath
//       做版本号取数。本程序保留这段旧代码以演示行为，同时**并行**用现代
//       stLibVersion_Tc2_Math 取相同数据，方便对比 / 迁移验证。
//
// 价值：本程序的"反面教材"作用：展示旧 API 与新 API 的等价对比，说服团队
//       完成迁移；通过观察 nBuild_NewWay 字段证明旧 API 缺 build 信息。
//
// 验证：登录运行，在线 monitor 看：
//       - nMajor_OldWay 与 nMajor_NewWay 相同
//       - nMinor / nRevision 同理
//       - nBuild_NewWay 单独有值，旧 API 拿不到
//       证明：旧 API 是新 API 的真子集，没有任何理由继续使用旧 API。
PROGRAM P_Demo_F_GetVersionTcMath
VAR
    // ─── 旧 API（弃用，仅演示）──────────────────────────
    nMajor_OldWay     : UINT;
    nMinor_OldWay     : UINT;
    nRevision_OldWay  : UINT;

    // ─── 新 API（推荐）─────────────────────────────────
    nMajor_NewWay     : UINT;
    nMinor_NewWay     : UINT;
    nBuild_NewWay     : UINT;    // 旧 API 完全拿不到这个字段
    nRevision_NewWay  : UINT;
    sVersion_NewWay   : STRING(23);

    bChecked          : BOOL;     // 只跑一次的 latch
END_VAR

IF NOT bChecked THEN
    bChecked := TRUE;

    // 旧 API：每个字段要单独传魔法数 1/2/3，可读性差
    nMajor_OldWay    := F_GetVersionTcMath(nVersionElement := 1);
    nMinor_OldWay    := F_GetVersionTcMath(nVersionElement := 2);
    nRevision_OldWay := F_GetVersionTcMath(nVersionElement := 3);

    // 新 API：直接成员访问，自描述、还能拿到 build 与字符串
    nMajor_NewWay    := stLibVersion_Tc2_Math.iMajor;
    nMinor_NewWay    := stLibVersion_Tc2_Math.iMinor;
    nBuild_NewWay    := stLibVersion_Tc2_Math.iBuild;
    nRevision_NewWay := stLibVersion_Tc2_Math.iRevision;
    sVersion_NewWay  := stLibVersion_Tc2_Math.sVersion;
END_IF
```

## 7. 业务场景与实际价值

- **场景**：维护从 TwinCAT 2 迁移过来的老代码、临时回滚到旧版库做兼容测试。这两个场景之外**不要**再调用本函数。
- **价值**：仅作为"反面教材 / 迁移参考"——通过对比新旧 API 看出差距，推动团队完成代码现代化。
- **替代方案对比**：
  - **首选**：`stLibVersion_Tc2_Math.iMajor` 直接成员访问 + `F_CmpLibVersion` 做比较
  - **过渡期**：保留 `F_GetVersionTcMath` 调用但加 `// TODO: migrate to stLibVersion_Tc2_Math` 注释，团队规范限期迁移
  - **本函数继续使用**：无任何技术理由

## 8. 参考资料

- **PDF**：[TwinCAT_3_PLC_Lib_Tc2_Math_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_Math_EN.pdf) §4.1（`[obsolete functions]`）
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tcplclib_tc2_math/68452363.html
- **替代用法**：`stLibVersion_Tc2_Math`（本库版本常量）、`F_CmpLibVersion`（`Tc2_System` 的版本比较器）、`ST_LibVersion`（`Tc2_System` 的版本结构体类型）
