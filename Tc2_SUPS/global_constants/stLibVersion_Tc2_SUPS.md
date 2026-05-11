# stLibVersion_Tc2_SUPS

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc2_SUPS` |
| Library Version | `1.5.2` |
| Type | `VAR_GLOBAL CONSTANT` |
| Category | `Library version` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_SUPS_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tcplclib_tc2_sups/30510347.html |
| Verified | 2026-05-11 ✅ |
| InfoSys-checked | ✅ 2026-05-11 |
| Status | `verified` |
| Example | [`examples/P_Demo_stLibVersion_Tc2_SUPS.xml`](../examples/P_Demo_stLibVersion_Tc2_SUPS.xml) |

---

## 1. 功能简述

`stLibVersion_Tc2_SUPS` 是 Tc2_SUPS 库提供的**版本号全局常量**，类型为 `ST_LibVersion`（定义在 Tc2_System 中）。它的作用是给业务代码一个标准化的途径来回答"我引用的这个 Tc2_SUPS 是哪个版本"，配合 `F_CmpLibVersion`（也在 Tc2_System）做版本兼容性检查。

PDF §6.1 明确指出：所有 TwinCAT 2 时代的「`LibVersion_*.QueryLibraryVersion()` 方法 / `QueryLibraryVersion` 全局函数」等版本查询途径**全部废弃**。新工程一律使用本 `stLibVersion_Tc2_SUPS` 常量 + `F_CmpLibVersion`。

实际使用场景：某段业务代码要求 Tc2_SUPS ≥ 1.5.2（例如用到了 BAPI 版的某个特性），就在 PLC 启动初始化阶段调一次 `F_CmpLibVersion`，不满足条件就抛 PLC 报警 / 拒绝运行——避免在错误版本上跑出隐蔽 bug。

## 2. 接口定义

### VAR_GLOBAL CONSTANT

```iecst
VAR_GLOBAL CONSTANT
    stLibVersion_Tc2_SUPS : ST_LibVersion;
END_VAR
```

| 名称 | 类型 | 默认值 | 说明 |
|---|---|---|---|
| `stLibVersion_Tc2_SUPS` | `ST_LibVersion` | — | Tc2_SUPS 库的版本信息结构体。**字段由 Beckhoff 在编译库时固化**，结构体内 `iMajor` / `iMinor` / `iBuild` / `iRevision` / `nFlags` / `sVersion` / `sNote` 分量都对应 PDF 上写的版本号 `1.5.2` |

### VAR_OUTPUT

不适用（这是常量声明而非 FB）。

### VAR_IN_OUT

不适用。

## 3. 行为说明

`stLibVersion_Tc2_SUPS` 是一个**只读全局常量**——业务代码任何地方都可以读，但 IEC 61131-3 的 `CONSTANT` 关键字保证它**不能被赋值**。它的值在库被编译时由 Beckhoff 写死，是 ROM 数据，PLC 启动时直接拿到。

**典型使用模式**：
1. 在 PLC 启动 init 阶段调一次 `F_CmpLibVersion(stLibVersion := stLibVersion_Tc2_SUPS, iMajor := 1, iMinor := 5, iBuild := 2, iRevision := 0, nCmpType := E_CmpLibVersion.GreaterOrEqual)`
2. 若返回 `FALSE` → 库版本低于业务要求 → 抛 PLC 错误 / 设置 HMI 告警 / 拒绝进入正常状态机
3. 后续每个 PLC 周期不需要再查（常量值不变）

**版本比较的标准方法**：使用 `F_CmpLibVersion`（Tc2_System），通过 `nCmpType : E_CmpLibVersion` 选择比较语义：`Equal` / `NotEqual` / `Greater` / `GreaterOrEqual` / `Less` / `LessOrEqual`。

**为什么不能用 `IF stLibVersion_Tc2_SUPS.iMajor = 1 AND iMinor >= 5 THEN`**：表面看可以，但 `ST_LibVersion` 内字段的具体含义（特别是 `nFlags`、`iRevision` 与 build 号的关系）随 TwinCAT 版本演化；用 `F_CmpLibVersion` 是 Beckhoff 保证向前兼容的唯一途径。

## 4. 错误码 / 返回值

不适用——本身是常量声明，无运行时行为，无错误码。

`F_CmpLibVersion` 的返回值是 `BOOL`：`TRUE` 表示比较条件成立、`FALSE` 表示不成立（包括「比较类型 `nCmpType` 非法」这种异常也只是简单返回 `FALSE`，不抛错）。

## 5. 使用注意 / 常见坑

- **必须先引用 Tc2_System**：`ST_LibVersion` 类型和 `F_CmpLibVersion` 函数都在 Tc2_System 里。新工程往往已经依赖 Tc2_System（几乎所有 Beckhoff 库都依赖它），但要在 PLC 项目的 References 里确认。
- **`F_CmpLibVersion` 在 init 阶段调一次就够**：常量值不变，每周期重复调用浪费 PLC 时间。
- **不要用 `=` 直接比 `stLibVersion_Tc2_SUPS.iMajor`**（工程经验补充）：用 `F_CmpLibVersion`，理由见 §3。
- **PDF 文本里写的版本号是 `1.5.2`**：与本仓库元信息表的 `Library Version` 一致。如果 Beckhoff 发新版（例如 `1.5.3` / `1.6.0`），本常量的值会随之更新，但常量的**名字**（`stLibVersion_Tc2_SUPS`）和**类型**（`ST_LibVersion`）不变——这正是版本检查能稳定工作的原因。
- **`stLibVersion_Tc2_SUPS` 是这一个库的版本**：每个库都有自己的 `stLibVersion_<LibName>` 常量；要查 Tc2_System 自己的版本就用 `stLibVersion_Tc2_System`。

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_stLibVersion_Tc2_SUPS.xml`](../examples/P_Demo_stLibVersion_Tc2_SUPS.xml)（PLCopenXML，可直接导入 TwinCAT 3 XAE）
>
> 导入步骤：右键 PLC 项目 → Import PLCopenXML → 选该文件 → OK
> 详见 [`examples/README.md`](../examples/README.md)

```iecst
// 场景：业务代码要求 Tc2_SUPS ≥ 1.5.2 才能用（用到了 BAPI 版的某些输出）。
//       PLC init 阶段做一次版本检查，不满足就置 bLibVersionTooOld 让 HMI 报警。
//
// 价值：避免在「以为是 1.5.2 实际是 1.4.x」的库上跑出隐蔽 bug——例如 BAPI
//       版的某个 method 1.5.x 才有，老版本编译会过但运行行为不同。
//
// 验证：登录运行 → 观察 bLibOK 应为 TRUE（本仓库基线 1.5.2 ≥ 1.5.2）；
//       在线把 nRequiredMajor 改成 99 → bLibOK 应翻为 FALSE，bTooOld 翻
//       为 TRUE。
PROGRAM P_Demo_stLibVersion_Tc2_SUPS
VAR
    stCurrentVersion       : ST_LibVersion;       // 拿到的版本结构体
    nRequiredMajor         : USINT := 1;
    nRequiredMinor         : USINT := 5;
    nRequiredBuild         : USINT := 2;
    nRequiredRevision      : USINT := 0;
    bLibOK                 : BOOL;
    bLibVersionTooOld      : BOOL;
END_VAR
// 拷贝一份到本地变量便于在线 monitor 观察各字段
stCurrentVersion := stLibVersion_Tc2_SUPS;

// init 阶段调一次即可；用 F_CmpLibVersion 比较，标准化路径
bLibOK := F_CmpLibVersion(
    stLibVersion := stLibVersion_Tc2_SUPS,
    iMajor       := nRequiredMajor,
    iMinor       := nRequiredMinor,
    iBuild       := nRequiredBuild,
    iRevision    := nRequiredRevision,
    nCmpType     := E_CmpLibVersion.GreaterOrEqual
);
bLibVersionTooOld := NOT bLibOK;
```

## 7. 业务场景与实际价值

- **场景**：设备厂的同一份 PLC 代码部署到多家客户工厂；不同工厂的 TwinCAT 镜像里 Tc2_SUPS 版本可能不一致（有的客户长期不升级 TwinCAT，库版本卡在 1.4.x）。新加的业务功能依赖 1.5.x 的输出 → 编译时不会报错，但实际行为不一致 → 难排查的现场问题。
- **价值**：用 vs 不用 = 「上电 1 秒内立刻发现版本不够 → 停在 init 状态等运维处理」vs 「编译通过、运行隐蔽错乱、几天后被工程师反查到」。
- **替代方案对比**：
  - **手动比较 `stLibVersion_Tc2_SUPS.iMajor / iMinor`**：能做但脆弱，未来 Beckhoff 可能在结构体里加字段（例如 `nFlags` 含义变化）
  - **不检查**：上面说的隐蔽错乱
  - **本常量 + `F_CmpLibVersion`**：✅ Beckhoff 官方推荐路径，向前兼容
- **何时需要**：所有发布到外部客户的 PLC 项目都建议加版本检查；自己工厂内自用且 TwinCAT 镜像统一管理时可以省略。

## 8. 参考资料

- **PDF**：[TwinCAT_3_PLC_Lib_Tc2_SUPS_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_SUPS_EN.pdf) §6.1
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tcplclib_tc2_sups/30510347.html
- **相关类型 / 函数**：`ST_LibVersion`、`F_CmpLibVersion`、`E_CmpLibVersion`（均在 Tc2_System）
- **相关 GVL**：其它库的同名常量 `stLibVersion_<LibName>`
