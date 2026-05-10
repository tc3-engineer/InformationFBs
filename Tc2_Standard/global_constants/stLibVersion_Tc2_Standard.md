# stLibVersion_Tc2_Standard

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc2_Standard` |
| Library Version | `1.3.4` |
| Type | `VAR_GLOBAL CONSTANT` |
| Category | `Global constants` |
| Source | https://infosys.beckhoff.com/content/1033/tcplclib_tc2_standard/ |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_Standard_EN.pdf |
| Verified | 2026-04-08 ✅ |
| Status | `verified` |
| Example | [`examples/P_Demo_stLibVersion_Tc2_Standard.xml`](../examples/P_Demo_stLibVersion_Tc2_Standard.xml) |

---

## 1. 功能简述

每个 PLC 库都带有一个版本号，存储在 `Tc2_Standard` 库的全局常量 `stLibVersion_Tc2_Standard` 中。在 PLC repository 中也能看到该版本。

类型 `ST_LibVersion` 来自 `Tc2_System`（结构体含 iMajor/iMinor/iBuild/iRevision/sVersion 等字段——以 `Tc2_System` 文档为准）。

## 2. 接口定义

### VAR_GLOBAL CONSTANT

```iecst
VAR_GLOBAL CONSTANT
    stLibVersion_Tc2_Standard : ST_LibVersion;
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `stLibVersion_Tc2_Standard` | `ST_LibVersion` | Tc2_Standard 库的版本号 |

### VAR_OUTPUT

不适用（全局常量，无 IO 接口）。

### VAR_IN_OUT

不适用。

## 3. 行为说明

- 由编译器在加载库时自动填值
- **只读**——尝试写入会编译报错
- 用 `F_CmpLibVersion`（在 `Tc2_System` 中）做版本比较
- TwinCAT 2 的 `LibVersion_*.QueryLibraryVersion()` 风格已不再支持

## 4. 错误码 / 返回值

无（常量声明）。

## 5. 使用注意 / 常见坑

- `ST_LibVersion` 类型定义在 `Tc2_System`，不在 `Tc2_Standard`——使用前需引用 `Tc2_System`。
- **运行时检查**用法：
  ```iecst
  IF NOT F_CmpLibVersion(
      stLibVersion := stLibVersion_Tc2_Standard,
      iMajor := 1, iMinor := 3, iBuild := 4, iRevision := 0,
      nCmpType := E_CmpLibVersion.GreaterOrEqual
  ) THEN
      // 库版本太低，处理异常
  END_IF;
  ```
  这能在工程切换 TwinCAT 版本时及时发现 lib 不匹配。（工程经验补充）
- 在 PLC project 的 References → `Tc2_Standard` 上右键 "Properties" 也能看到同一版本。

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_stLibVersion_Tc2_Standard.xml`](../examples/P_Demo_stLibVersion_Tc2_Standard.xml)（PLCopenXML，可直接导入 TwinCAT 3 XAE）
>
> 导入步骤：右键 PLC 项目 → Import PLCopenXML → 选该文件 → OK
> 详见 [`examples/README.md`](../examples/README.md)

```iecst
PROGRAM P_Demo_stLibVersion_Tc2_Standard
VAR
    stMyVer  : ST_LibVersion;     // 监视库版本
    bOk      : BOOL;              // 版本是否 >= 1.3.4
END_VAR

// 把全局常量复制到本地变量便于在线监视
stMyVer := stLibVersion_Tc2_Standard;

// 运行时检查最低版本
bOk := F_CmpLibVersion(
    stLibVersion := stLibVersion_Tc2_Standard,
    iMajor       := 1,
    iMinor       := 3,
    iBuild       := 4,
    iRevision    := 0,
    nCmpType     := E_CmpLibVersion.GreaterOrEqual
);

// 1. 登录 PLC
// 2. 在线监视 stMyVer（应显示 1.3.4 或更高）
// 3. 在线监视 bOk（应为 TRUE）
```

## 7. 相关

- `Tc2_System.ST_LibVersion`（结构体定义）
- `Tc2_System.F_CmpLibVersion`（版本比较函数）
- 任意其他 lib 的 `stLibVersion_<libname>`（同样模式）

## 8. 待确认项

- `ST_LibVersion` 字段细节以 `Tc2_System` 文档为准（本库未自描述）
