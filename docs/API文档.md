# 当前压缩 API

这些模块是 Windows 桌面程序的内部实现，不承诺独立 SDK 的兼容性。界面入口为 `src/compress_gui.py`，压缩任务入口为 `ImageCompressor.compress_images()`。

## 模块职责

| 模块 | 职责 |
| --- | --- |
| `modules/config.py` | 工具路径、格式列表、启动提示设置 |
| `modules/compressor.py` | 文件扫描、处理进度、统计与停止控制 |
| `modules/strategies/` | 常规和极致压缩的工具编排及独立参数 |
| `modules/tools_manager.py` | 原生工具、图像量化库的具体调用 |
| `modules/tool_invoker.py` | 极致策略使用的参数封装和调用入口 |
| `modules/parameter.py` | 参数定义、类型转换、范围校验 |
| `modules/logger.py` | 控制台、轮转文件与结构化日志 |
| `modules/ui/` | 窗口、配置、参数对话框和进度展示 |

常规策略直接调用工具，极致策略通过 `ToolInvoker` 调用。两者都使用 `ToolParameterSet` 校验原生工具参数。

## 压缩任务

```python
from src.modules.compressor import ImageCompressor

# 默认使用常规压缩；另一个有效策略标识为 compression。
compressor = ImageCompressor(strategy_name='speed')
# 路径必须由使用者明确选择，先复制资源再压缩。
compressor.compress_images('资源副本', compress_audio=False)
# 获取本轮统计信息。
statistics = compressor.get_statistics()
```

`compress_images(path, progress_callback=None, compress_audio=False)` 支持单文件或目录，返回是否完成任务调度；**返回 True 不表示每个文件都成功压缩**，应结合统计和日志判断。回调收到进度值，处理文件期间还可能收到第二个文件路径参数。

`stop_compression()` 会停止继续调度后续文件；已在执行的外部工具不会因此立即终止。

`get_statistics()` 包含 `total_files`、`processed_files`、`success_count`、`failed_count`、`png_count`、`jpg_count`、`audio_count`、`other_count`、`total_original_size` 和 `total_saved_bytes`。未节省空间的文件也计入失败数量，小于 512 字节的文件会直接跳过；统计不代表内容质量检测结果。

## 策略和参数

- `speed`：常规压缩，默认参数在 `strategies/config_speed.py`。
- `compression`：极致压缩，默认参数在 `strategies/config_compression.py`。
- `set_strategy(name)` 切换策略；未知策略会抛出明确错误。
- `set_strategy_parameters(name, parameters)` 更新对应策略参数，界面参数入口为 `ParameterDialog`。
- 不再提供历史多工具策略配置、WebP 转换分支和依赖旧配置的包装方法。

`ToolParameter` 记录名称、值、类型、必填约束、范围、默认值及说明。`validate()` 检查必填值，必要时尝试类型转换，再检查数值范围，失败抛出 `ParameterValidationError`。

`ToolParameterSet.from_dict(tool_name, param_dict, param_definitions)` 根据工具参数定义构造集合。未知参数不应作为可用的命令行扩展点；增加参数需要同时更新定义与具体工具实现。

`ToolInvoker.invoke_tool(tool_type, tool_name, file_path, params_dict=None)` 返回处理后的字节大小，参数错误在调用工具前抛出。具体工具通常会记录运行错误并返回原文件大小，因此调用方仍需检查体积变化和日志。

## 文件与日志边界

- 只在文件变小时原位置覆盖；压缩可能有损，不保证元数据保留。
- 工具参数使用列表直接传给 `subprocess`，不经过命令解释器。
- 日志可能包含资源名称、完整路径和原生工具输出，不应直接公开。
- 启动设置写入 `startup_warning_config.json`，日志和设置均由 `.gitignore` 排除。
- 原生工具配置与目录要求见 [压缩工具准备](../tools/modes/README.md)。
