# Tc2_System

Beckhoff TwinCAT 3 PLC **Tc2_System** 库的中文技术文档与配套演示工程。

> **库版本（PDF Version）**：1.17.3
> **PDF 来源**：[TwinCAT_3_PLC_Lib_Tc2_System_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_System_EN.pdf)
> **InfoSys 总索引**：<https://infosys.beckhoff.com/content/1033/tcplclib_tc2_system/index.html>

## 库简介

Tc2_System 是 TwinCAT 3 工程中最常引用的基础库之一，封装了与运行时 / 操作系统 / 文件系统 / 内存 / 硬件低层交互的核心能力。

主要能力：

- **文件 I/O**：基于 ADS 的异步文件读 / 写 / 寻位 / 目录管理（`FB_FileOpen` 等 14 个 FB）；
- **内存操作**：高速字节级 `MEMCPY` / `MEMSET` / `MEMCMP` / `MEMMOVE`；
- **位操作**：32 位读 / 写 / 清位的纯函数（`SETBIT32` / `GETBIT32` 等）；
- **PC 硬件**：主板看门狗（`FB_PcWatchdog` / `FB_PcWatchDog_BAPI`）、I/O 端口直访（`F_IOPortRead` / `F_IOPortWrite`）；
- **任务 / 核心信息**：`F_GetTaskInfo` / `F_GetCpuCoreIndex` / `GETCURTASKINDEXEX`；
- **网络地址格式化**：IPv4 / MAC 字节数组 ↔ 字符串（`F_CreateIPv4Addr` 等）；
- **多任务同步**：原子 `TestAndSet`；
- **诊断与异常**：`F_CheckMemoryArea` / `F_GetMappingStatus` / `F_RaiseException`；
- **库版本守门**：`stLibVersion_Tc2_System` + `F_CmpLibVersion`；
- **全局常量集合**：`AMSPORT_*` / `ADSSTATE_*` / `FOPEN_MODE*` / `DEFAULT_ADS_TIMEOUT` 等。

> 此 README 收录的 47 篇文档是 **S1 范围**，覆盖 General functions / File function blocks / Memory functions / I/O port access / Watchdog function blocks / Global constants / Library version / [Obsolete] 八类。
> ADS 函数（`ADSREAD` / `ADSWRITE` 等）、IEC SFC / EventLogger / Time function blocks / Character functions 等剩余约 33 个条目属于另一个 PR 范围。

## 目录索引

### File function blocks（14）

基于 ADS 的异步文件 I/O；`bExecute` 上升沿触发，`bBusy` / `bError` / `nErrId` 状态机。

| 名称 | 类别 | 用途 |
|---|---|---|
| [FB_FileOpen](file_function_blocks/FB_FileOpen.md) | FB | 打开 / 新建文件，返回句柄 |
| [FB_FileClose](file_function_blocks/FB_FileClose.md) | FB | 关闭文件，刷盘并释放句柄 |
| [FB_FileRead](file_function_blocks/FB_FileRead.md) | FB | 按字节读 |
| [FB_FileWrite](file_function_blocks/FB_FileWrite.md) | FB | 按字节写 |
| [FB_FileGets](file_function_blocks/FB_FileGets.md) | FB | 按行读文本 |
| [FB_FilePuts](file_function_blocks/FB_FilePuts.md) | FB | 按行写文本 |
| [FB_FileLoad](file_function_blocks/FB_FileLoad.md) | FB | Open + Read + Close 一步完成 |
| [FB_FileSeek](file_function_blocks/FB_FileSeek.md) | FB | 移动文件指针 |
| [FB_FileTell](file_function_blocks/FB_FileTell.md) | FB | 查询当前文件指针位置 |
| [FB_EOF](file_function_blocks/FB_EOF.md) | FB | 检查文件结束 |
| [FB_FileDelete](file_function_blocks/FB_FileDelete.md) | FB | 删除文件 |
| [FB_FileRename](file_function_blocks/FB_FileRename.md) | FB | 重命名 / 移动文件 |
| [FB_CreateDir](file_function_blocks/FB_CreateDir.md) | FB | 新建目录（单级） |
| [FB_RemoveDir](file_function_blocks/FB_RemoveDir.md) | FB | 删除空目录 |

### General functions（20）

通用工具函数：版本对比 / 网络地址格式化 / 位操作 / 任务与核心信息 / 多任务同步。

| 名称 | 用途 |
|---|---|
| [F_CmpLibVersion](general_functions/F_CmpLibVersion.md) | 比较库版本 |
| [F_CheckMemoryArea](general_functions/F_CheckMemoryArea.md) | 查变量所在内存区类别 |
| [F_CreateIPv4Addr](general_functions/F_CreateIPv4Addr.md) | 4 字节 → IPv4 字符串 |
| [F_CreateMacAddr](general_functions/F_CreateMacAddr.md) | 6 字节 → MAC 字符串 |
| [F_ScanIPv4AddrIds](general_functions/F_ScanIPv4AddrIds.md) | IPv4 字符串 → 4 字节 |
| [F_GetCpuCoreIndex](general_functions/F_GetCpuCoreIndex.md) | 任务 → CPU 核索引 |
| [F_GetCpuCoreInfo](general_functions/F_GetCpuCoreInfo.md) | 读 CPU 核详细信息 |
| [F_GetMappingPartner](general_functions/F_GetMappingPartner.md) | 取变量映射对端 ID |
| [F_GetMappingStatus](general_functions/F_GetMappingStatus.md) | 取变量映射状态 |
| [F_GetStructMemberAlignment](general_functions/F_GetStructMemberAlignment.md) | 结构体对齐字节数 |
| [F_GetTaskInfo](general_functions/F_GetTaskInfo.md) | 当前任务系统信息 |
| [F_RaiseException](general_functions/F_RaiseException.md) | 主动抛运行时异常 |
| [F_SplitPathName](general_functions/F_SplitPathName.md) | 拆解完整路径 |
| [SETBIT32](general_functions/SETBIT32.md) | 32 位置位 |
| [CSETBIT32](general_functions/CSETBIT32.md) | 32 位条件置位 |
| [GETBIT32](general_functions/GETBIT32.md) | 32 位读位 |
| [CLEARBIT32](general_functions/CLEARBIT32.md) | 32 位清位 |
| [GETCURTASKINDEXEX](general_functions/GETCURTASKINDEXEX.md) | 当前任务上下文索引 |
| [LPTSIGNAL](general_functions/LPTSIGNAL.md) | LPT 并口引脚控制 |
| [TestAndSet](general_functions/TestAndSet.md) | 原子 TestAndSet 锁 |

### Memory functions（4）

字节级高速内存操作。**直接操作物理内存**，使用不当可能导致系统崩溃。

| 名称 | 用途 |
|---|---|
| [MEMCPY](memory_functions/MEMCPY.md) | 复制内存（不重叠） |
| [MEMMOVE](memory_functions/MEMMOVE.md) | 复制内存（支持重叠） |
| [MEMSET](memory_functions/MEMSET.md) | 字节填充 |
| [MEMCMP](memory_functions/MEMCMP.md) | 字节比较 |

### I/O port access（2）

直接读 / 写 PC 主板 I/O 端口（x86 端口空间）。**写操作可能损坏硬件**。

| 名称 | 用途 |
|---|---|
| [F_IOPortRead](io_port_access/F_IOPortRead.md) | 读端口 |
| [F_IOPortWrite](io_port_access/F_IOPortWrite.md) | 写端口 |

### Watchdog function blocks（2）

PC 主板硬件看门狗，超时强制重启整机。

| 名称 | 用途 |
|---|---|
| [FB_PcWatchdog](watchdog_function_blocks/FB_PcWatchdog.md) | 旧版（特定主板，≤ 255 秒） |
| [FB_PcWatchDog_BAPI](watchdog_function_blocks/FB_PcWatchDog_BAPI.md) | 新版（BIOS-API，≤ 15300 秒） |

### Global constants（1）

| 名称 | 用途 |
|---|---|
| [Constants](global_constants/Constants.md) | `AMSPORT_*` / `ADSSTATE_*` / `FOPEN_MODE*` 等 |

### Library version（1）

| 名称 | 用途 |
|---|---|
| [stLibVersion_Tc2_System](library_version/stLibVersion_Tc2_System.md) | 库版本全局常量 |

### [Obsolete]（3）

| 名称 | 替代方案 |
|---|---|
| [F_GetVersionTcSystem](obsolete/F_GetVersionTcSystem.md) | `stLibVersion_Tc2_System.iMajor` 等字段 |
| [GETSYSTEMTIME](obsolete/GETSYSTEMTIME.md) | `F_GetSystemTime()` 函数 |
| [GETTASKTIME](obsolete/GETTASKTIME.md) | `F_GetTaskTime()` 函数 |

## 例程使用

每篇文档配套一个 `examples/P_Demo_<Name>.xml` PLCopenXML 文件。导入方式：

1. 在 TwinCAT XAE 中右键 PLC 项目 → **Import PLCopenXML** → 选择对应 xml 文件 → OK；
2. 引用 Tc2_System（References → Add library）；
3. 编译 → 登录 → 运行；按例程头部『验证步骤』在线观察。

## 验证基线

- 所有 47 篇文档通过 `_meta/tools/verify_doc.py`（PDF + InfoSys 双源对照、占位短语扫描、§3 中文长度 ≥ 80）；
- 所有 47 个例程通过 `_meta/tools/lint_plcopen.py`（PLCopenXML 结构校验）；
- 元信息表 `InfoSys-checked: ✅ 2026-05-20` 已对每个条目逐条交叉验证。
