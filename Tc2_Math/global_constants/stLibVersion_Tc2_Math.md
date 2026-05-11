# stLibVersion_Tc2_Math

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc2_Math` |
| Library Version | `1.3.3` |
| Type | `VAR_GLOBAL CONSTANT` |
| Category | `Library version` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_Math_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tcplclib_tc2_math/68455307.html |
| Verified | 2026-05-11 ✅ |
| InfoSys-checked | ✅ 2026-05-11 |
| Status | `verified` |
| Example | [`examples/P_Demo_stLibVersion_Tc2_Math.xml`](../examples/P_Demo_stLibVersion_Tc2_Math.xml) |

---

## 1. 功能简述

`Tc2_Math` 库的版本号全局常量。每个 Beckhoff PLC 库都会暴露一个 `stLibVersion_<LibraryName>` 常量，类型为 `ST_LibVersion`（定义于 `Tc2_System`），里面包含 `iMajor / iMinor / iBuild / iRevision` 四个 `UINT` 数字字段 + 一个 `sVersion : STRING(23)` 字符串表示。

主要用途：运行时检查"用户工程引用的库版本"是否满足代码所需的最低版本。由 `F_CmpLibVersion`（也在 `Tc2_System`）做比较；不匹配时可在启动阶段报错停机，避免因新旧版 FB 行为差异（如 PDF §4 标出的 `F_GetVersionTcMath` 等弃用 API）引发现场难定位的故障。

PDF 明确指出：TwinCAT 2 时代的其他版本对比方法（包括本库的 `F_GetVersionTcMath`）**已弃用**，统一改用本常量 + `F_CmpLibVersion`。

## 2. 接口定义

### VAR_GLOBAL CONSTANT

```iecst
VAR_GLOBAL CONSTANT
    stLibVersion_Tc2_Math : ST_LibVersion;
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `stLibVersion_Tc2_Math` | `ST_LibVersion` | 本库版本结构体。当前版本 `1.3.3` 对应 `iMajor=1`、`iMinor=3`、`iBuild=3`、`iRevision=0`，`sVersion='1.3.3.0'` |

### VAR_OUTPUT

不适用（GVL 不是 FB）。

### VAR_IN_OUT

不适用（GVL 不是 FB）。

## 3. 行为说明

本常量是编译期固定值。库被加载到 PLC 工程时由 Beckhoff PLC 工具链填入数值，**用户代码不可写**（编译器会报错"不能赋值给常量"）。

`ST_LibVersion` 结构体内部字段（来自 `Tc2_System`）：

```iecst
TYPE ST_LibVersion :
STRUCT
    iMajor    : UINT;
    iMinor    : UINT;
    iBuild    : UINT;
    iRevision : UINT;
    sVersion  : STRING(23);   // 例：'1.3.3.0'
END_STRUCT
END_TYPE
```

**典型用法**（PLC 工程启动阶段调用 `F_CmpLibVersion` 比较版本）：

1. 把 `stLibVersion_Tc2_Math` 与硬编码的"代码所需的最低版本（如 `1.3.0`）"输入 `F_CmpLibVersion`
2. 函数返回 `BOOL`：`TRUE` 表示满足比较条件（如"大于等于 `1.3.0`"），`FALSE` 表示不满足
3. 不满足时用户代码进入"版本不兼容"错误分支，把 PLC 留在安全停机状态

**版本号语义**（按 Beckhoff 通用规则）：

- `iMajor`：主版本号；变更意味着不向后兼容（API 或行为变化）
- `iMinor`：次版本号；新功能 / 内部优化，向后兼容
- `iBuild`：构建号；纯内部 bug 修复
- `iRevision`：修订号；通常 `0`，特殊定制版本时非零

**InfoSys 明确说明**：TwinCAT 2 时代的旧版本对比方法（包括同库的 `F_GetVersionTcMath`）**已过时**，统一改用 `F_CmpLibVersion`。

## 4. 错误码 / 返回值

不适用（常量本身没有返回值或错误码）。`F_CmpLibVersion` 自己返回 `BOOL`，不通过本常量传递错误。

## 5. 使用注意 / 常见坑

- **必须先引用 `Tc2_System`**：`ST_LibVersion` 类型和 `F_CmpLibVersion` 函数都定义在 `Tc2_System`，没引用会编译报"未声明的标识符"。
- **比较类型用枚举 `E_CmpLibVersion`**：`Equal` / `GreaterOrEqual` / `GreaterThan` / `LessOrEqual` / `LessThan`。**实际工程几乎只用 `GreaterOrEqual`**（"至少这个版本"）。
- **不要硬编码版本字符串去匹配 `sVersion`**：字符串格式 Beckhoff 没文档化保证（中间分隔符是 `.` 还是 `_` 不同版本可能有差异）。比较只看 `iMajor / iMinor / iBuild / iRevision` 四个数字字段。
- **不可改这个常量值**：尝试 `stLibVersion_Tc2_Math.iMajor := 2;` 会被编译器拒绝。
- **下载新版本库后必须重新下载到 PLC** 才能让新版本号生效。在 XAE 把库从 `1.3.2` 换成 `1.3.3` → 重新编译 → 重新下载到目标 → 此时 `stLibVersion_Tc2_Math.iBuild` 才会从 `2` 变成 `3`。（工程经验补充）
- **不要在循环中重复调 `F_CmpLibVersion`**：版本是编译期常量，启动时调一次缓存结果即可，循环调浪费 PLC 周期。
- **优于 `F_GetVersionTcMath`**：旧 API 只能拿 3 个字段、需传魔法数 1/2/3、不能直接比较。本常量提供 4 字段 + 字符串 + 配套比较函数，是新代码唯一推荐方式。

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_stLibVersion_Tc2_Math.xml`](../examples/P_Demo_stLibVersion_Tc2_Math.xml)（PLCopenXML，可直接导入 TwinCAT 3 XAE）
>
> 导入步骤：右键 PLC 项目 → Import PLCopenXML → 选该文件 → OK
> 详见 [`examples/README.md`](../examples/README.md)

```iecst
// 场景：工程代码依赖 Tc2_Math ≥ 1.3.0 的 MODTURNS / MODABS 行为（更早版本
//       某些边界情况返回值不同）。PLC 启动时先检查所引用的库版本是否够新，
//       不够就停机并给 HMI 报警，避免现场升级或备机替换时无意引入旧版库
//       导致 NC 角度归一化行为微妙变化。
//
// 价值：把"版本依赖"从源码注释里的口头约定变成运行时强制门禁——版本不匹配
//       在 PLC 第一个周期就被发现，而不是在 NC 跑了几天后才暴露行为差异。
//
// 验证：登录运行，在线 monitor 看 stCurrentLibVer 应显示 iMajor=1 iMinor=3
//       iBuild=3，bLibVersionOk = TRUE，sLibCheckMsg 显示 "version OK"。
//       反例：在 XAE 把 Tc2_Math 降到 1.2.x 重新下载 → bLibVersionOk 变 FALSE，
//       sLibCheckMsg 显示 "Tc2_Math too old, need 1.3.0+"。
PROGRAM P_Demo_stLibVersion_Tc2_Math
VAR
    stCurrentLibVer    : ST_LibVersion;   // 在线 monitor 看实际版本号
    bLibVersionOk      : BOOL;            // 启动门禁结果
    sLibCheckMsg       : STRING(80);      // HMI 显示用消息
    bChecked           : BOOL;            // 只检查一次的 latch
END_VAR

// 启动只跑一次（PLC 进入 Run 后第一个周期），版本是编译期常量
IF NOT bChecked THEN
    bChecked := TRUE;

    // 1. 快照当前库的版本号（仅诊断用，给 HMI 看）
    stCurrentLibVer := stLibVersion_Tc2_Math;

    // 2. 调 Tc2_System 提供的版本比较器：要求 ≥ 1.3.0.0
    bLibVersionOk := F_CmpLibVersion(
        stLibVersion := stLibVersion_Tc2_Math,
        iMajor       := 1,
        iMinor       := 3,
        iBuild       := 0,
        iRevision    := 0,
        nCmpType     := E_CmpLibVersion.GreaterOrEqual
    );

    // 3. 决策：不满足就把状态消息填进去给 HMI / 报警系统
    IF bLibVersionOk THEN
        sLibCheckMsg := 'Tc2_Math version OK';
    ELSE
        sLibCheckMsg := 'Tc2_Math too old, need 1.3.0+';
        // 真实工程在这里应该把 PLC 切到 SAFE_STOP，而不是继续跑业务
    END_IF
END_IF
```

## 7. 业务场景与实际价值

- **场景**：机器交付现场后，多年内会经历多次 TwinCAT 升级、备机替换、PLC 程序拷贝迁移。每次操作都有把库版本搞错的风险（备机里的 `Tc2_Math` 是 `1.2.x`，主机是 `1.3.3`）。版本不一致导致取整 / 模运算行为微妙差异，故障极难复现（伺服角度归一化错半圈、CRC 校验偶尔失败……）。
- **价值**：一行 `F_CmpLibVersion` 调用在 PLC 启动阶段把"运行时 vs 编译时所需版本"显式化，把版本不匹配从"隐蔽现场 bug"变成"启动时立刻报错"。代码与库版本绑定写在源码里，做版本管理时有据可查。
- **替代方案对比**：
  - 不检查版本：默认大家都用最新版——实际现场是混乱的，多机型多版本并存
  - 注释里写"需要 Tc2_Math ≥ 1.3.0"：人靠不住，迟早有人忽略
  - 在 PLC 工程属性里"锁定库版本"：能锁但不可在运行时检测，迁移时还是会被默默改掉
  - 用 `F_GetVersionTcMath`：旧 API，缺 build 字段、缺字符串、要传魔法数；新代码勿用
  - **本常量 + `F_CmpLibVersion`**：运行时强制门禁，是行业标准做法

## 8. 参考资料

- **PDF**：[TwinCAT_3_PLC_Lib_Tc2_Math_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_Math_EN.pdf) §5.1
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tcplclib_tc2_math/68455307.html
- **相关类型**：[`ST_LibVersion`](https://infosys.beckhoff.com/content/1033/globaldatatypes/714823819.html)（在 `Tc2_System` / 全局类型库）
- **相关函数**：`F_CmpLibVersion`（在 `Tc2_System`，版本比较器）、`E_CmpLibVersion`（比较类型枚举）、`F_GetVersionTcMath`（**已弃用**的旧 API，仅迁移期保留）
