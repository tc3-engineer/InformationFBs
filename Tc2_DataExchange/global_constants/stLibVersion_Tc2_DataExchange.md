# stLibVersion_Tc2_DataExchange

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc2_DataExchange` |
| Library Version | `1.2.2` |
| Type | `VAR_GLOBAL CONSTANT` |
| Category | `Library version` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_DataExchange_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tcplclib_tc2_dataexchange/54807179.html |
| Verified | 2026-05-11 ✅ |
| InfoSys-checked | ✅ 2026-05-11 |
| Status | `verified` |
| Example | [`examples/P_Demo_stLibVersion_Tc2_DataExchange.xml`](../examples/P_Demo_stLibVersion_Tc2_DataExchange.xml) |

---

## 1. 功能简述

`Tc2_DataExchange` 库的版本号全局常量。每个 Beckhoff PLC 库都会暴露一个 `stLibVersion_<LibraryName>` 常量，类型为 `ST_LibVersion`（定义于 `Tc2_System`），里面包含 `iMajor / iMinor / iBuild / iRevision` 四个数字字段加一个 `sVersion : STRING(23)` 字符串表示。

主要用途：运行时检查"用户工程引用的库版本"是否满足代码所需的最低版本，由 `F_CmpLibVersion`（也在 `Tc2_System`）做比较；不匹配时可在启动阶段报错停机，避免因新旧版 FB 行为差异引发故障。

## 2. 接口定义

### VAR_GLOBAL CONSTANT

```iecst
VAR_GLOBAL CONSTANT
    stLibVersion_Tc2_DataExchange : ST_LibVersion;
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `stLibVersion_Tc2_DataExchange` | `ST_LibVersion` | 本库版本结构体。当前版本 1.2.2 对应 `iMajor=1`、`iMinor=2`、`iBuild=2`、`iRevision=0` |

### VAR_OUTPUT

不适用（GVL 不是 FB）。

### VAR_IN_OUT

不适用（GVL 不是 FB）。

## 3. 行为说明

本常量是编译期固定值。库被加载到 PLC 工程时由 Beckhoff PLC 工具链填入数值，**用户代码不可写**（编译器会报错"不能赋值给常量"）。

典型用法是在 PLC 工程启动阶段调用 `F_CmpLibVersion` 比较版本：

1. 把 `stLibVersion_Tc2_DataExchange` 与硬编码的"代码所需的最低版本（如 1.2.2）"输入 `F_CmpLibVersion`
2. 函数返回 `BOOL`：`TRUE` 表示满足比较条件（如"大于等于 1.2.2"），`FALSE` 表示不满足
3. 不满足时用户代码进入"版本不兼容"错误分支，把 PLC 留在安全停机状态

`ST_LibVersion` 结构体内部字段（来自 `Tc2_System`）：

```iecst
TYPE ST_LibVersion :
STRUCT
    iMajor    : UINT;
    iMinor    : UINT;
    iBuild    : UINT;
    iRevision : UINT;
    sVersion  : STRING(23);   // 例：'1.2.2.0'
END_STRUCT
END_TYPE
```

InfoSys 明确说明：TwinCAT 2 时代的其他版本对比方法**已过时**，统一改用 `F_CmpLibVersion`。

## 4. 错误码 / 返回值

不适用（常量本身没有返回值或错误码）。`F_CmpLibVersion` 自己返回 `BOOL`，不通过本常量传递错误。

## 5. 使用注意 / 常见坑

- **必须先引用 `Tc2_System`**。`ST_LibVersion` 类型和 `F_CmpLibVersion` 函数都定义在 Tc2_System，没引用时编译报"未声明的标识符"。
- **比较类型用枚举 `E_CmpLibVersion`**：`Equal` / `GreaterOrEqual` / `GreaterThan` / `LessOrEqual` / `LessThan`。**实际工程几乎只用 `GreaterOrEqual`**（"至少这个版本"）。
- **不要硬编码版本字符串去匹配 `sVersion`**：字符串格式 Beckhoff 没文档化保证（中间分隔符是 `.` 还是 `_` 不同版本可能有差异）。比较只看 `iMajor / iMinor / iBuild / iRevision` 四个数字字段。
- **不可改这个常量值**：尝试 `stLibVersion_Tc2_DataExchange.iMajor := 2;` 会被编译器拒绝。
- **下载新版本库后必须重启 PLC** 才能让新版本号生效。在 XAE 把库从 1.2.2 换成 1.2.3 → 重新编译 → 重新下载到目标 → 此时 `stLibVersion_Tc2_DataExchange.iBuild` 才会从 2 变成 3。（工程经验补充）
- **不要在循环中重复调 `F_CmpLibVersion`**：版本是编译期常量，启动时调一次缓存结果即可，循环调浪费 PLC 周期。

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_stLibVersion_Tc2_DataExchange.xml`](../examples/P_Demo_stLibVersion_Tc2_DataExchange.xml)（PLCopenXML，可直接导入 TwinCAT 3 XAE）
>
> 导入步骤：右键 PLC 项目 → Import PLCopenXML → 选该文件 → OK
> 详见 [`examples/README.md`](../examples/README.md)

```iecst
// 场景：工程代码依赖 Tc2_DataExchange ≥ 1.2.2 的 FB_WriteWatchdog 行为（旧版本 bSendNow
//       在 bEnable=FALSE 时无效，已知 bug 1.2.2 修复）。需要在 PLC 启动时先检查版本，
//       不达标就停机并点亮 HMI 报警，避免在不兼容的库上跑生产。
//
// 价值：不做版本检查时，现场升级机器可能把库无意换成旧版，旧 FB 行为不一致会导致看门狗
//       行为异常但又不报错——故障非常难定位。一次性的启动版本门禁可在编译/下载阶段就发现。
//
// 验证：在线 monitor stCurrentLibVer 应显示 iMajor=1 iMinor=2 iBuild=2；
//       bLibVersionOk 应为 TRUE；如果在 XAE 把库降到 1.2.1 重新下载 →
//       bLibVersionOk 变 FALSE，sLibCheckMsg 显示 "Tc2_DataExchange too old, need 1.2.2+"。
PROGRAM P_Demo_stLibVersion_Tc2_DataExchange
VAR
    stCurrentLibVer    : ST_LibVersion;          // 在线 monitor 看实际版本号
    bLibVersionOk      : BOOL;                   // 启动门禁结果
    sLibCheckMsg       : STRING(80);             // HMI 显示用消息
    bChecked           : BOOL;                   // 只检查一次的 latch
END_VAR

// 启动只跑一次（PLC 进入 Run 后第一个周期）
IF NOT bChecked THEN
    bChecked := TRUE;

    // 1. 快照当前库的版本号（仅诊断用，给 HMI 看）
    stCurrentLibVer := stLibVersion_Tc2_DataExchange;

    // 2. 调用 Tc2_System 提供的版本比较器，要求 ≥ 1.2.2.0
    bLibVersionOk := F_CmpLibVersion(
        stLibVersion := stLibVersion_Tc2_DataExchange,
        iMajor       := 1,
        iMinor       := 2,
        iBuild       := 2,
        iRevision    := 0,
        nCmpType     := E_CmpLibVersion.GreaterOrEqual
    );

    // 3. 决策：不满足就把状态消息填进去给 HMI / 报警系统
    IF bLibVersionOk THEN
        sLibCheckMsg := 'Tc2_DataExchange version OK';
    ELSE
        sLibCheckMsg := 'Tc2_DataExchange too old, need 1.2.2+';
        // 真实工程在这里应该把 PLC 切到 SAFE_STOP，而不是继续跑业务
    END_IF
END_IF
```

## 7. 业务场景与实际价值

- **场景**：机器交付现场后，多年内会经历多次 TwinCAT 升级、备机替换、PLC 程序拷贝迁移。每次操作都有把库版本搞错的风险（备机里的 Tc2_DataExchange 是 1.1.x，主机是 1.2.2）。版本不一致导致 FB 行为微妙差异，故障极难复现。
- **价值**：一行 `F_CmpLibVersion` 调用在 PLC 启动阶段把"运行时 vs 编译时所需版本"显式化，把版本不匹配从"隐蔽现场 bug"变成"启动时立刻报错"。代码与库版本绑定写在源码里，做版本管理时有据可查。
- **替代方案对比**：
  - 不检查版本：默认大家都用最新版——实际现场是混乱的，多机型多版本并存
  - 注释里写"需要 Tc2_DataExchange ≥ 1.2.2"：人靠不住，迟早有人忽略
  - 在 PLC 工程属性里"锁定库版本"：能锁但不可在运行时检测，迁移时还是会被默默改掉
  - **本常量 + `F_CmpLibVersion`**：运行时强制门禁，是行业标准做法

## 8. 参考资料

- **PDF**：[TwinCAT_3_PLC_Lib_Tc2_DataExchange_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_DataExchange_EN.pdf) §6.1
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tcplclib_tc2_dataexchange/54807179.html
- **相关类型**：[`ST_LibVersion`](https://infosys.beckhoff.com/content/1033/globaldatatypes/714823819.html)（在 `Tc2_System` / 全局类型库）
- **相关函数**：`F_CmpLibVersion`（在 `Tc2_System`，版本比较器）、`E_CmpLibVersion`（比较类型枚举）
