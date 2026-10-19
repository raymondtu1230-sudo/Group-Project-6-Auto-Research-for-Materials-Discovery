# RTX 4070 独立试跑准备（未执行）

目的：测量这台机器的 Chemeleon GPU 耗时和显存，不是启动正式基线。无需搬走旧电脑的个人数据；不复制旧 `.venv`，不把 CPU 中断缓存接到 GPU。当前操作系统、显存容量、驱动和远程访问方式尚未知，醒来后再按实际系统确定安装步骤。这里没有启动或远程连接你的机器。

## 1. 在 4070 机器独立准备

安装 Git、uv 和兼容的 NVIDIA 驱动；先查看已有版本，不擅自升级。选一个新目录：

```bash
git clone https://github.com/raymondtu1230-sudo/Group-Project-6-Auto-Research-for-Materials-Discovery.git
cd Group-Project-6-Auto-Research-for-Materials-Discovery
git rev-parse HEAD
cd M1/MADE
uv sync --locked
nvidia-smi
uv run python -c "import torch; print('torch', torch.__version__); print('built CUDA', torch.version.cuda); print('available', torch.cuda.is_available()); print('GPU', torch.cuda.get_device_name(0) if torch.cuda.is_available() else 'NONE'); print('memory bytes', torch.cuda.get_device_properties(0).total_memory if torch.cuda.is_available() else 0)"
```

保存 Git revision、uv.lock、Python/Torch/CUDA 版本、驱动版本、GPU 型号和实际显存。若 locked 环境不能识别 GPU，停在环境诊断；不要直接升级 Torch、改 uv.lock 或把这一结果算模型测试成功。模型权重可在这台机器正常重新下载；下载时间与计算时间分开记录。以后需要 Materials Project key 时只用本机忽略的 `.env`，不复制或公开密钥。

## 2. 环境通过后，单独做小型 GPU 计时

由用户确认具体系统后再运行，不在本轮深夜执行：

- 新建带时间戳的 `M2/results/gpu_pilot/` 子目录；明确写 `benchmark_score=false`、`split=pilot`，不要放进正式 `protocol_v1` 或复用清单。
- 使用项目当前 ChemeleonGenerator 的 `device="cuda"`，加载后核对模型实际设备。先以 Li2O、seed 17、batch=2、候选数=2做独立环境试跑，保留默认256扩散步；这只是诊断配置，绝不替代正式 batch256 / pool1024 / B20。
- 模型加载、一次预热、正式计时分开。计时前后做 CUDA synchronize，清零后记录 peak allocated/reserved memory、wall seconds、生成数量和完整错误日志。
- 显存充足且小试跑成功后，再单独评估正式 batch256 能否容纳；OOM 时保存错误并停止该配置，不把缩小 batch 后的结果冒充正式协议结果。小样本速度不能直接推算全部18个正式单元。

## 3. 正式迁移前的界限

CPU 与 GPU 的数值及随机执行结果不保证逐位相同，不能续接本次 CPU cache。正式GPU实验需先与 M1/M6 统一设备、环境、方法间比较和成本口径，记录版本化协议；既有 CPU 原始结果保留。GPU pilot 不计入36个 CPU dev baseline 单元，也不授权启动 check/hidden 或付费云资源。

目前未测出 4070 的真实加速倍数，也未证明其显存能容纳正式批次。先独立 clone 和检测即可，不必迁移整台电脑。
