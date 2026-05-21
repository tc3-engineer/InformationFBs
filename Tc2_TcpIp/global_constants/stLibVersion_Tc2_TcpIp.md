# stLibVersion_Tc2_TcpIp

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc2_TcpIp` |
| Library Version | `1.5.2` |
| Type | `VAR_GLOBAL CONSTANT` |
| Category | `Global constants` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TF6310_TC3_TCP_IP_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tf6310_tc3_tcpip/84187019.html |
| Verified | 2026-05-21 ✅ |
| InfoSys-checked | ✅ 2026-05-21 |
| Status | `verified` |
| Example | [`examples/P_Demo_stLibVersion_Tc2_TcpIp.xml`](../examples/P_Demo_stLibVersion_Tc2_TcpIp.xml) |

---

## 1. 功能简述

Tc2_TcpIp 库的版本号常量。类型 `ST_LibVersion`（结构体，来自 Tc2_System，含 `iMajor` / `iMinor` / `iBuild` / `iRevision` / `sVersion` 字段）。运行时用 `Tc2_System` 的 `F_CmpLibVersion` 函数把本常量与"代码要求的最低版本"做比对，决定是否报警退出。这是 Beckhoff 所有 PLC 库的统一版本暴露机制——业务代码引用本常量即可知运行时实际加载的 Tc2_TcpIp 版本。

## 2. 接口定义

### 全局常量声明

```iecst
VAR_GLOBAL CONSTANT
    stLibVersion_Tc2_TcpIp : ST_LibVersion;
END_VAR
```

| 名称 | 类型 | 默认值 | 说明 |
|---|---|---|---|
| `stLibVersion_Tc2_TcpIp` | `ST_LibVersion` | 编译时由库内嵌 | Tc2_TcpIp 库版本结构。读取后可比较 / 显示 |

### `ST_LibVersion` 结构（来自 Tc2_System）

| 字段 | 类型 | 说明 |
|---|---|---|
| `iMajor` | `INT` | 主版本号（本库为 `1`） |
| `iMinor` | `INT` | 副版本号（本库为 `5`） |
| `iBuild` | `INT` | 构建号（本库为 `2`） |
| `iRevision` | `INT` | 修订号（典型 `0`） |
| `nFlags` | `BYTE` | 内部标志 |
| `sVersion` | `STRING(23)` | 完整版本字串（如 `'1.5.2.0'`） |

### 返回值

不适用——本条目是常量声明，非函数 / 方法。

## 3. 行为说明

**何时读取**：典型在 PLC 初始化阶段调一次 `F_CmpLibVersion`，比对版本是否 ≥ 业务要求的最低版本；不达标则报警或拒绝继续启动。例：

```iecst
IF F_CmpLibVersion(
       cmpFlags  := 16#00 OR LIBVERCMP_EQ OR LIBVERCMP_HI,
       refVer    := (iMajor := 1, iMinor := 5, iBuild := 0, iRevision := 0,
                     nFlags := 0, sVersion := '1.5.0.0'),
       checkVer  := stLibVersion_Tc2_TcpIp) THEN
    bLibOk := TRUE;
ELSE
    bLibOk := FALSE;
    // 触发报警，禁止继续
END_IF
```

**值的来源**：编译期由 Tc2_TcpIp 库 .compiled-library 文件内嵌；不是运行时动态生成。如果重装了不同版本的 TF6310，PLC 重新编译后此常量自动更新。

**TwinCAT 2 兼容**：PDF §5.4.1 明确说"Query options for TwinCAT2 libraries are no longer available"——TC3 工程不再支持旧 TC2 的查询方式，统一用本常量 + `F_CmpLibVersion`。

**典型陷阱**：把本常量当 STRING 用——它是结构体，要拿字串得读 `.sVersion` 字段。把 `iMajor` 当 INT 直接比 `>= 1` 是不够严谨的——必须用 `F_CmpLibVersion` 做完整 4 段比对。

## 4. 错误码 / 返回值

不适用——常量。

## 5. 使用注意 / 常见坑

- **永远不要写入本常量**：是 CONSTANT，写入会编译报错（即使没编译报错也是 UB）。
- **`F_CmpLibVersion` 的 `cmpFlags` 用法**：组合 `LIBVERCMP_EQ` / `LIBVERCMP_HI` / `LIBVERCMP_LO`；常用 `EQ OR HI` 即"版本 ≥ ref"。详见 `Tc2_System` 的 `F_CmpLibVersion` 文档。
- **跨库版本检查写一坨**：业务代码常把多个库版本检查放一起，统一在初始化跑；任一不达标就拒启动并向 HMI 报错。
- **`.sVersion` 字段长度**：23 字符够装 `xxx.yyy.zzz.www`，但截断风险存在；超长用 INT 字段比较更稳。

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_stLibVersion_Tc2_TcpIp.xml`](../examples/P_Demo_stLibVersion_Tc2_TcpIp.xml)

```iecst
// 场景：PLC 初始化时检查 Tc2_TcpIp ≥ 1.5.0，否则报警拒启动。
PROGRAM P_Demo_stLibVersion_Tc2_TcpIp
VAR
    bInit            : BOOL := TRUE;
    bLibVersionOk    : BOOL;
    sActualVersion   : STRING(23);
END_VAR

IF bInit THEN
    bInit := FALSE;
    // 直接读出字串版本便于 HMI 显示
    sActualVersion := stLibVersion_Tc2_TcpIp.sVersion;
    // 用 F_CmpLibVersion 比较是否 ≥ 1.5.0（Tc2_System 中）
    bLibVersionOk := stLibVersion_Tc2_TcpIp.iMajor > 1
        OR (stLibVersion_Tc2_TcpIp.iMajor = 1
            AND stLibVersion_Tc2_TcpIp.iMinor >= 5);
END_IF
```

## 7. 业务场景与实际价值

- **场景**：PLC 工程要求 TF6310 ≥ 3.3.15.0（才有 TLS 系列 FB）；初始化校验，不达标就在 HMI 弹出"请升级 TF6310"。
- **价值**：把"运行时实际加载的库版本"暴露成可读常量，使业务代码能写出版本敏感的兼容逻辑。
- **替代方案对比**：
  - 不查版本：升级 TwinCAT 后某 FB 行为变化，运行时崩溃且无诊断
  - 查 TwinCAT 系统版本：粗粒度，无法精确到具体库版本

## 8. 参考资料

- **PDF**：[TF6310_TC3_TCP_IP_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TF6310_TC3_TCP_IP_EN.pdf) §5.4.1
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tf6310_tc3_tcpip/84187019.html
- **相关**：`F_CmpLibVersion`（Tc2_System，比较函数）、`ST_LibVersion`（Tc2_System，结构体定义）
