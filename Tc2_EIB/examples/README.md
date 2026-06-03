# Tc2_EIB / examples

每个 FB / FC 配套的可导入演示程序，**TwinCAT 3 原生 .TcPOU 格式**（XML / TcPlcObject schema），可直接拖入 XAE 的 PLC `POUs` 文件夹。

## 命名约定

- `P_Demo_<Name>.TcPOU` — 一个 PROGRAM POU，演示该 FB / FC 的最小可运行用法

## 如何导入到 TwinCAT 3 XAE

1. 在 Solution Explorer 里**右键 PLC 项目（`<MyProject> Project` 节点）或其下任一文件夹**
2. 选 **"Add → Existing Item..."**
3. 选中本目录下的 `.TcPOU` 文件
4. 弹窗显示可导入对象（一个 PROGRAM）→ OK
5. POU 出现在树中（顶层或你选的文件夹下，取决于 TwinCAT 设置）

> ⚠️ 一定要**右键 PLC 项目层**（不是 Solution 层、不是 System 层），否则菜单不会出现 "Add → Existing Item"。

## 如何运行验证

1. **引用本库 + 依赖库**：在 PLC 项目 References 节点添加 `Tc2_EIB`，部分例程还需引用 `Tc2_Standard`（`TON` / `R_TRIG` 等）。
2. 编译 PLC 项目（无错误）。
3. 把刚导入的 PROGRAM 加到 PlcTask 调用列表（`MAIN` 或新建任务）：
   - 在 `MAIN` 里加一行 `P_Demo_<Name>();`
4. Activate Configuration → 登录 → Run。
5. 用在线写值（Write Value）切换输入变量，观察输出变量。

每个 `.TcPOU` 文件顶部的注释列出了该 demo 的**场景 / 价值 / 验证步骤**三件套，照做即可观察 FB 的真实行为。

## 关于 EIB demo 的特殊点

EIB 不像 TON / R_TRIG 那样能"纯软件跑通"——它必须有真实的 KL6301 端子 + EIB 总线 + 至少一个对端 EIB 设备（开关、传感器、调光器等）才能跑通完整链路。所以：

### 不需要硬件就能验证的部分

- 编译过 = FB 引脚名 / 类型对齐
- 登录 + 运行 → FB 实例能创建、变量内存被分配
- 在线 monitor 变量 → 能看到默认值

### 需要硬件才能验证的部分

- `bReady = TRUE`（KL6301 配置成功）
- `bDataReceive` 脉冲（必须有对端发 telegram）
- `bError = FALSE`（必须 EIB 总线通信正常）

如果只想"看 FB 编译过且实例被实例化"，把例程加到任务里、登录即可——不需要接 KL6301 也能验证这一步。

### 没有硬件时的等价测试

可以用 ETS5 软件 + 假 KL6301 + 真 EIB 设备做半实物联调。详见 Beckhoff 提供的 zip 示例（PDF §4.4.1 链接）：

> https://infosys.beckhoff.com/content/1033/tcplclib_tc2_eib/Resources/6165821835.zip

## 库依赖

例程统一依赖：

- `Tc2_EIB`（本库）：所有 EIB FB / FC、`EIB_REC` / `EIB_GROUP_ADDR` 等数据类型
- `Tc2_Standard`（部分例程）：`TON` / `R_TRIG` 等基本 FB

在 References 节点 → Add Library → 输入名字即可添加。

## 例程通用约定

为了让 48 个例程风格一致便于阅读：

1. **FB 实例命名**：`fb<FunctionalRole>` 形式（例 `fbSendTemp` / `fbReceiveAngle`）
2. **EIB_REC 变量**：所有例程都用名 `stEibRec`——实际项目中要换成你 KL6301 实例的 `str_Data_Rec` 输出
3. **组地址变量**：`stGroup<Purpose>` 形式（例 `stGroupOutdoorTemp`）
4. **业务输入变量**：贴近工业语义命名（例 `rRoomTempC` / `iBrightnessLux` 而不是 `r1` / `i2`）
5. **R_TRIG 上升沿采样**：所有接收 demo 都用 R_TRIG 转 `bDataReceive` 上升沿，避免把脉冲信号当电平用
6. **错误码变量**：`iLastErrID : EIB_ERROR_CODE` 统一名

## 链 KL6301 IO 的步骤

实际工程中本例程要工作，KL6301 端子必须在 System Manager 里链好 24 字节过程数据：

1. System Manager → 找 KL6301 端子节点
2. 右键 KL6301 input `ParameterStatus` → Change Link → 选 PLC 工程里 `arrKL6301_IN[1]`
3. 右键 KL6301 input `InputData1`..`InputData22` → 用 Shift+左键多选 → Change Link → 选 PLC `arrKL6301_IN[2]`..`arrKL6301_IN[23]`（PDF §4.4.1 详细截图）
4. 输出方向同样把 22 字节链到 `arrKL6301_OUT[]`

每个 demo 顶部的"场景 / 价值 / 验证步骤"注释会标明具体链接哪个 EIB 设备到哪个 group address，照做即可。

## 调试技巧

- **看不到 `bDataReceive` 脉冲**：90% 是 KL6301 过滤器没配你监听的 group address，检查 `KL6301.EIB_GROUP_FILTER`。
- **发送看似成功但 EIB 总线无帧**：检查 `Group_Address` 是否在过滤器内（PDF 反复警告：过滤器外的地址 KL6301 静默丢，连下发都不发）。
- **`KL6301.bError = TRUE`、`iErrorId = 14`**：固件 B0 用了 iMode = 1，要么升固件，要么改 iMode = 0。
- **`KL6301.bError = TRUE`、`iErrorId = 32`**：KL6301 端子 mapping 没链，检查 System Manager。
- **跨任务时 `EIB_REC` 不工作**：所有 EIB FB 必须放同一 PLC 任务。
