# Version

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc2_BACnet` |
| Library Version | `1.1.2` |
| Type | `GVL` |
| Category | `Library version` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TF8020_TC3_BACnet_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tf8020_bacnetrev14/12319275659.html |
| Verified | 2026-06-03 ✅ |
| InfoSys-checked | ✅ 2026-06-03 |
| Status | `verified` |
| Example | [`examples/P_Demo_Version.TcPOU`](../examples/P_Demo_Version.TcPOU) |

---

## 1. 功能简述

库版本声明 GVL，提供变量 `stLibVersion_Tc3_BACnetRev14`（类型 `ST_LibVersion`），运行时可读出本库的主版本号、次版本号、构建号与修订号，用于"项目里引用的 BACnet 库版本是否符合工程需求"的版本校验。BACnet 协议状态机和持久化文件格式在小版本间可能演进，HMI 启动时按版本号给出"项目要求最低版本"提示能避免现场误装旧库的问题。

## 2. 接口定义

> PDF §5.2.1 仅给出 `stLibVersion_Tc3_BACnetRev14` 类型与结构成员描述，未单独列 `VAR_GLOBAL` 块。下表整理 PDF §5.2.1 中确认的成员（来自标准 `ST_LibVersion` 结构）。

### VAR_INPUT

无（GVL，不接收输入）。

### VAR_OUTPUT

无（GVL，不暴露输出）。

### 结构体成员（`ST_LibVersion` 字段）

| 名称 | 类型 | 说明 |
|---|---|---|
| `iMajor` | `INT` | 主版本号（Major release number） |
| `iMinor` | `INT` | 次版本号（Minor release number） |
| `iBuild` | `INT` | 构建号（Build number） |
| `iRevision` | `INT` | 修订号（Revision number） |
| `sVersion` | `STRING` | 完整版本字符串（点分形式，如 `'1.1.2.0'`） |

⚠️ `ST_LibVersion` 是 TwinCAT 通用结构（多个 Beckhoff 库共用）；PDF §5.2.1 仅说明本库通过 `stLibVersion_Tc3_BACnetRev14` 暴露该结构，未自行列字段。

## 3. 行为说明

GVL 在库加载时由 TwinCAT 自动初始化为编译进库的版本元数据；PLC 程序通过 `Tc3_BACnetRev14.stLibVersion_Tc3_BACnetRev14.iMajor`（或在引用了本库的 namespace 下直接 `stLibVersion_Tc3_BACnetRev14.iMajor`）读取，**只读**。典型校验语义：在 PLC 程序冷启动时（PLC 任务首个周期）读出版本结构，与项目硬编码的"最低支持版本"比较，若版本过低则把诊断告警送到 HMI（如 `bLibVersionOk := FALSE; sLibVersionDiag := 'BACnetRev14 < 1.1.2';`）。**不要在循环里每周期都比对**，浪费 CPU；启动期比一次即可。本 GVL 不是 FB / 不能被实例化、不需要 `Adapter` 或 `Server` 绑定。

## 4. 错误码 / 返回值

GVL 不存在错误码概念。版本字段读取本身永不失败。

## 5. 使用注意 / 常见坑

- **库版本变名注意**：库实际命名 `Tc3_BACnetRev14`（PDF 头页所示），本仓库 `Tc2_BACnet` 是任务别名，**实际工程项目里引用是 `Tc3_BACnetRev14`**；GVL 全名是 `stLibVersion_Tc3_BACnetRev14`。
- **旧版本 `Tc2_BACnetRev12` 不可共存**：PDF §5 第二段明确"Using both libraries Tc3_BACnetRev14 and Tc2_BACnetRev12 within one project is not supported"，工程升级时需先卸 V12 再装 V14。
- **版本字符串 `sVersion` 仅供日志使用**：作为唯一 string 来源比较时需用 `EQ` / `FIND`；数值字段才适合做"≥ X"判断。
- **不能用版本号判断"BACnet supplement 已 ready"**：本 GVL 仅说明库代码版本，BACnet 协议栈是否真启动需要查 `BACnet_Globals.DefaultAdapter.eDevState = eComplete` 或 `BACnet_Globals.DefaultServer` 内部状态。

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_Version.TcPOU`](../examples/P_Demo_Version.TcPOU)

```iecst
PROGRAM P_Demo_Version
VAR
    bChecked        : BOOL;
    bVersionOk      : BOOL;
    sLibVersion     : STRING;
END_VAR

IF NOT bChecked THEN
    bChecked := TRUE;
    sLibVersion := stLibVersion_Tc3_BACnetRev14.sVersion;
    bVersionOk := (stLibVersion_Tc3_BACnetRev14.iMajor >= 1)
              AND (stLibVersion_Tc3_BACnetRev14.iMinor >= 1)
              AND (stLibVersion_Tc3_BACnetRev14.iBuild >= 2);
END_IF
```

## 7. 业务场景与实际价值

- **场景**：分包工程交付后维护人员升级 TwinCAT 装了不同版本的 Tc3_BACnetRev14，控制器开机时通过 HMI 显示"BACnet 库版本是否满足项目要求"，避免运维误装旧库导致 BACnet 协议帧格式回退。
- **价值**：把"库版本检查"从手工排查降级到"PLC 自检"，减少现场故障定位时间。
- **替代方案对比**：
  - 用文档约定"必须装 1.1.2 以上"：能做但无法在程序里自检
  - 用 PLC 启动时调一次未知方法看是否 NPE：脆弱、跨版本兼容差
  - **本 GVL**：官方提供，跨小版本兼容、可靠

## 8. 参考资料

- **PDF**：[TF8020_TC3_BACnet_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TF8020_TC3_BACnet_EN.pdf) §5.2.1
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tf8020_bacnetrev14/12319275659.html；库根 https://infosys.beckhoff.com/content/1033/tf8020_bacnetrev14/index.html
- **相关 GVL**：`BACnet_Globals`、`BACnet_Param`
