# FB_KL3208Config

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc2_IoFunctions` |
| Library Version | `1.5.3` |
| Type | `FUNCTION_BLOCK` |
| Category | `Bus Terminal configuration` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_IoFunctions_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tcplclib_tc2_iofunctions/2084384779.html |
| Verified | 2026-05-21 ✅ |
| InfoSys-checked | ✅ 2026-05-21 |
| Status | `verified` |
| Example | [`examples/P_Demo_FB_KL3208Config.TcPOU`](../examples/P_Demo_FB_KL3208Config.TcPOU) |

---

## 1. 功能简述

配置 KL3208-0010（8 通道电阻传感器输入端子）单个通道的传感器类型。8 个通道每个都用一个本 FB 实例（混合配置允许）。

## 2. 接口定义

### VAR_INPUT

```iecst
VAR_INPUT
    bConfigurate : BOOL;
    bReadConfig : BOOL;
    iSetSensorType : INT;
    tTimeout : TIME;
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `bConfigurate` | `BOOL` | 布尔标志 `bConfigurate`。 |
| `bReadConfig` | `BOOL` | 布尔标志 `bReadConfig`。 |
| `iSetSensorType` | `INT` | 传感器类型编码（PT100 / PT1000 / Ni100 / 直接电阻 等；具体见 PDF KL3208 手册表）。 |
| `tTimeout` | `TIME` | ADS 命令执行允许的最大时长。默认 `DEFAULT_ADS_TIMEOUT`（约 5 秒）。若现场总线设备应答慢需要适当放大。 |

### VAR_OUTPUT

无。

### VAR_IN_OUT

无。

## 3. 行为说明

与 `FB_KL320xConfig` 用法完全相同，只是面对的端子是 8 通道版本，需要 8 个 FB 实例分别配置。`bConfigurate` 上升沿启动写配置序列（读通用信息 → 写寄存器 → 读回校验）；`bReadConfig` 上升沿启动只读序列（不写入 EEPROM）。`iSetSensorType` 选传感器类型（具体编码见 PDF KL3208 手册表，与 KL3204 可能略有差异）。执行期间 `bBusy := TRUE`，结束后通过 `bError` / `iErrorId` 反映成功 / 失败。`tTimeout` 限制单通道配置时长；K-bus 握手较慢，建议 ≥ 2 秒。8 通道一次性配完时间约 4-8 秒（每通道一次握手），可串行调用。

## 4. 错误码 / 返回值

本 FB 无具体错误码表；状态由输出参数自行反映。具体错误语义需配合主站 / 现场总线设备手册查询。

## 5. 使用注意 / 常见坑

- **写端子寄存器会改 EEPROM**，**不要循环周期调用 `bConfigurate`**——EEPROM 寿命 10 万次写入。上电时配置一次足够。
- `stInData` / `stOutData` 必须 IN_OUT 链到 System Manager 中端子的过程数据区，否则 FB 与端子之间通讯不通。（工程经验补充）
- PDF 指出"本 FB 不遵循 alternative output format"——意思是过程数据在标准 vs alternative 模式下偏移不同，FB 假定**标准模式**；若 System Manager 中端子设为 alternative 会出错。（工程经验补充）
- `tTimeout` 默认未指定时建议给 ≥ 2 秒，K-bus 端子配置握手较慢。（工程经验补充）
- 错误号 `iErrorId` 见 PDF 5.6 节的 KL Config 错误码表（如端子型号不匹配 / 寄存器写失败）；具体表 PDF 在每个 FB 后会列。（工程经验补充）
- 8 通道要 8 个 FB 实例，不要复用一个 FB 切通道访问。（工程经验补充）
- KL3208 与 KL3204 的传感器类型编码可能不完全相同；按 KL3208 手册选。（工程经验补充）

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_FB_KL3208Config.TcPOU`](../examples/P_Demo_FB_KL3208Config.TcPOU)（TwinCAT 3 原生 .TcPOU，可直接拖入 XAE 的 PLC POUs 文件夹）
>
> 导入步骤：右键 PLC 项目下 POUs 文件夹 → Add → Existing Item → 选该文件 → OK

详见 example xml 文件。

## 7. 业务场景与实际价值

- **场景**：机柜温度监控：KL3208 8 通道端子分别接 8 个 PT1000 监控不同设备温度。
- **价值**：8 通道配置代码化。
- **替代方案对比**：
  - KS2000 工具：要带工具
  - **本 FB**：8 个实例搞定

## 8. 参考资料

- **PDF**：[TwinCAT_3_PLC_Lib_Tc2_IoFunctions_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_IoFunctions_EN.pdf) §3.6.4
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tcplclib_tc2_iofunctions/2084384779.html
- **相关 FB / FC**：`FB_KL320xConfig`, `FB_KL3228Config`
