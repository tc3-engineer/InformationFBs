# FB_BACnet_File

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc2_BACnet` |
| Library Version | `1.1.2` |
| Type | `FUNCTION_BLOCK` |
| Category | `Object · File` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TF8020_TC3_BACnet_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tf8020_bacnetrev14/12319319179.html |
| Verified | 2026-06-03 ✅ |
| InfoSys-checked | ⚠️ chapter-overview-only |
| Status | `⚠️ infer-from-naming-convention` |
| Example | [`examples/P_Demo_FB_BACnet_File.TcPOU`](../examples/P_Demo_FB_BACnet_File.TcPOU) |

---

## 1. 功能简述

代表 BACnet 标准里的「File」对象类型(BACnet Object_Type = 10 / File),用于把 PLC 文件系统中的文件(典型:配置文件、persistent 数据导出、EDE 文件)暴露给 BMS,BMS 可通过 BACnet 标准的 AtomicReadFile / AtomicWriteFile 服务下载或上传。本对象类型本库仅基础类,无后缀变体。Status: ⚠️ PDF 仅在 §6.1.1 表中列出 File 一行,未给独立示例;本文档基于 BACnet 标准 File 对象语义 + 本库命名规则推导成员列表。

## 2. 接口定义

> PDF §6.1.1 / §6.1.2 把所有对象 FB 统一用对象类型表 + 后缀规则描述,**未**针对单个 FB 列 `VAR_INPUT` / `VAR_OUTPUT` 区;以下表把 PDF/InfoSys 在 §6.1.1 / §6.1.2 / §9.x 提及的成员按 BACnet 标准属性分类整理。

### VAR_INPUT

```iecst
VAR_INPUT
END_VAR
```

> ⚠️ PDF/InfoSys 均未给出独立 `VAR_INPUT` 区;成员见下表。

### VAR_OUTPUT

```iecst
VAR_OUTPUT
END_VAR
```

> ⚠️ PDF/InfoSys 均未给出独立 `VAR_OUTPUT` 区;运行状态以 FB 成员形式暴露,见下表。

### VAR_IN_OUT

无。

### 关键属性 / 成员(分组)

| 类别 | FB 成员 | 类型 | 含义 |
|---|---|---|---|
| 基本信息 | `iParent` / `sObjectName` / `sDescription` | `I_BACnet_View` / `STRING(*)` | DPAD + 名称 |
| 文件路径 | `sFileName` | `STRING(*)` | 本地文件系统中的实际文件路径 |
| 大小 | `nFileSize` | `UDINT` | File_Size(只读,stack 自动算) |
| 修改时间 | `dtFileModificationDate` | `DT` | Modification_Date(只读) |
| 访问方式 | `eFileAccessMethod` | `E_BACnet_FileAccessMethod` | File_Access_Method(`eStream` / `eRecord`) |
| 读保护 | `bReadOnly` | `BOOL` | Read_Only(禁止 BMS 写) |

## 3. 行为说明

FB_BACnet_File 每周期调用一次。stack 内部把 `sFileName` 指定的文件元数据(大小、修改时间)暴露为 BACnet File 对象属性,BMS 用 `AtomicReadFile(byteOffset, count)` 分块下载文件内容,用 `AtomicWriteFile(byteOffset, octetString)` 上传 / 更新文件。访问方式 `eStream` 适合顺序读写(典型:日志文件);`eRecord` 适合结构化记录读写。`bReadOnly := TRUE` 禁止 BMS 写,防误操作。文件实际驻留在 PLC 控制器本地存储(SD 卡 / 内置 flash),PLC 上电时 stack 会读 sFileName 校验文件是否存在;不存在则 stack 自动建空文件或报告 fault。PDF 未给独立示例,典型用法参照 BACnet 标准定义。

## 4. 错误码 / 返回值

无返回值。⚠️ PDF + InfoSys 未列具体 BACnet error/reject 码;本对象类型也未在 §9 给出示例。

## 5. 使用注意 / 常见坑

- **每周期调用一次,且使用同一周期任务**:`fb<Name>()` 必须每个 PLC 循环调用且只调用一次。若条件性调用(`IF bX THEN fb(); END_IF`),BACnet 客户端读这个对象时会看到值停滞;若用不同周期任务,启动期同步会失败(PDF §6.4.1 / §6.4.2)。
- **属性初值放在变量声明里,运行时改属性用上升沿触发**:`IF bChanged THEN fb.sDescription := 'New'; END_IF`,不要每周期写,否则 BACnet 端写下来的值会被覆盖(PDF §6.3.1)。
- **router memory 默认 32 MB,按"每对象 ≈ 20 KB"估算总需求**(PDF §6.5)。占用 ≥ 60% 时库拒绝再建对象,日志窗有 router-memory 错误。
- **`sFileName` 是本地文件系统的实际路径**:典型 CX 控制器是 `C:\TwinCAT\3.1\Boot\PlcLog.csv` 或 `/var/log/plc.log`;路径错文件读不到。
- **大文件读取慢**:BACnet AtomicReadFile 分块大小默认 1024 字节,几 MB 文件要几百次往返;通常只把 ≤ 1 MB 的配置 / 日志暴露。
- **`bReadOnly := TRUE` 是安全默认**:不打开时 BMS 可能误改 PLC 关键配置;打开写权限只在确认需要的场景。

## 6. 最小例程

> 配套可导入文件:[`examples/P_Demo_FB_BACnet_File.TcPOU`](../examples/P_Demo_FB_BACnet_File.TcPOU)

```iecst
PROGRAM P_Demo_FB_BACnet_File
VAR
    fbConfigFile : FB_BACnet_File := (
        sObjectName := 'ConfigFile',
        sDescription := 'Plant configuration JSON',
        sFileName := 'C:\TwinCAT\3.1\Boot\config.json',
        eFileAccessMethod := E_BACnet_FileAccessMethod.eStream,
        bReadOnly := FALSE);
END_VAR
fbConfigFile();
```

## 7. 业务场景与实际价值

- **场景**:运维想从 BMS 直接下载 PLC 上的 config.json(包含温度设定点表、报警阈值表),改完后再上传;无需远程登录 PLC。
- **价值**:BACnet File 是标准服务,跨厂商 BMS 都支持;免去 FTP / SCP / 远程桌面等额外协议。
- **替代方案对比**:用 FTP:运维要装客户端 + 走另一个端口;用 ADS:Beckhoff 自家;BACnet File 标准化、跨厂商。

## 8. 参考资料

- **PDF**:[TF8020_TC3_BACnet_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TF8020_TC3_BACnet_EN.pdf) §6.1.1(File = File)
- **InfoSys topic**:https://infosys.beckhoff.com/content/1033/tf8020_bacnetrev14/12319319179.html;命名规则:https://infosys.beckhoff.com/content/1033/tf8020_bacnetrev14/12319294987.html
- **相关 FB**:`FB_BACnet_Server.SavePersistentStackData()`(触发持久化的方法,与 File 配合可让 BMS 拉走 persistent 数据)
