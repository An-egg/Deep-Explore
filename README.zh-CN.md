# DeepExplore

[![PyPI version](https://badge.fury.io/py/deep-explore.svg)](https://badge.fury.io/py/deep-explore)
[![Python Versions](https://img.shields.io/pypi/pyversions/deep-explore.svg)](https://pypi.org/project/deep-explore/)
[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](LICENSE)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

**DeepExplore** 是一个自动化的功能探索测试框架，结合了有限状态机（FSM）和基于模型的测试（MBT）原则。它提供了一种灵活的、配置驱动的方法，用于测试云平台和分布式系统中的复杂状态转换。

## 特性

- **状态机支持**: 通过自动缓存和重试机制跟踪实例状态
- **基于模型的测试**: 多种执行策略（随机/顺序场景和动作）
- **灵活地停止条件**: 基于时间、步数或自定义结束条件
- **前置条件验证**: 状态匹配、数据匹配和自定义函数检查
- **场景组合**: 将多个动作组合成复杂的测试场景
- **配置驱动**: 通过 YAML/JSON 定义测试，无需修改代码
- **可扩展架构**: 工厂模式便于扩展模式、条件和检查

## 安装

```bash
pip install deep-explore
```

带 YAML 支持的开发版本：

```bash
pip install deep-explore[yaml,dev]
```

## 快速开始

### 1. 定义测试对象

```python
from deep_explore import DeepExploreObject

class MyTestObject(DeepExploreObject):
    def _do_update_state(self):
        # 从系统获取当前状态
        self.data = self.client.get_instance_info()

    def get_status(self):
        # 返回当前状态
        return self.data.get('status')

    def instance_id(self):
        # 动态参数解析器
        return self.data['id']
```

### 2. 创建配置文件

```yaml
mode_type: random_scenario

stopping_criteria_list:
  - criteria_type: step
    max_steps: 100

scenario_list:
  - scenario_name: "创建和删除测试"
    scenario_precondition_list:
      - precondition_type: status
        precondition_data: ["available"]
        compare_result: true
    action_list:
      - action_name: "create_resource"
        action_public_client: "my_client.ResourceClient"
        action_args:
          - name: "test-resource"
          - "_resolver_instance_id"
        action_post_check_list:
          - check_info: ["my_checks.check_created"]
            check_result: true

      - action_name: "delete_resource"
        action_public_client: "my_client.ResourceClient"
        action_args:
          - "_resolver_instance_id"
        action_precondition_list:
          - precondition_type: status
            precondition_data: ["running"]
            compare_result: true
```

### 3. 加载并执行

```python
import yaml
from deep_explore import DeepExploreLoader

# 创建测试对象
test_obj = MyTestObject()

# 加载配置
with open('config.yaml') as f:
    config = yaml.safe_load(f)

# 创建测试模式
mode = DeepExploreLoader.load_deep_explore_mode(test_obj, config)

# 运行测试
mode.exec_test()
```

## 架构

```
┌─────────────────────────────────────────────────────────┐
│                   DeepExplore Framework                  │
├─────────────────────────────────────────────────────────┤
│  DeepExploreMode (MBT Strategies)                       │
│   • RandomScenario   • SequenceScenario                 │
│   • RandomAction     • SequenceAction                   │
├─────────────────────────────────────────────────────────┤
│  DeepExploreObject (FSM State Management)               │
│   • State Tracking   • ERIS Integration                 │
│   • Parameter Resolvers                                 │
├─────────────────────────────────────────────────────────┤
│  Scenarios & Actions                                     │
│   • Preconditions    • Pre/Post Checks                  │
│   • Action Execution                                   │
├─────────────────────────────────────────────────────────┤
│  Stopping Criteria & Validation                         │
│   • Step/Time Based  • Custom Conditions                │
└─────────────────────────────────────────────────────────┘
```

详细的架构文档请参阅 [docs/deep_explore架构设计文档.md](docs/deep_explore架构设计文档.md)。

## 支持的测试模式

| 模式 | 描述 |
|------|------|
| `random_scenario` | 随机选择并执行场景 |
| `sequence_scenario` | 按顺序执行场景（支持反向） |
| `random_action` | 随机选择并执行单个动作 |
| `sequence_action` | 按顺序执行动作（支持反向） |

## 停止条件

| 类型 | 描述 |
|------|------|
| `step` | 执行 N 步后停止 |
| `time` | T 秒后停止 |
| `end_time` | 在指定时间戳停止 |

## 前置条件类型

| 类型 | 描述 |
|------|------|
| `status` | 匹配对象状态到列表 |
| `data` | 匹配对象数据结构 |
| `function` | 执行自定义检查函数 |

## 示例

查看 [examples/](examples/) 目录获取展示 DeepExplore 所有功能的综合使用示例。

### 示例文件

| 示例 | 难度 | 描述 |
|------|------|------|
| [基础设置](examples/basic_setup.py) | 初级 | 核心概念、测试对象、参数解析器和基本执行模式 |
| [场景测试](examples/scenario_test.py) | 中级 | 包含多个动作和场景级前置条件的复杂场景 |
| [自定义模式](examples/custom_mode.py) | 高级 | 创建自定义测试模式和扩展框架 |
| [高级用法](examples/advanced_usage.py) | 高级 | 数据匹配、多重停止条件、错误处理和更新控制 |
| [YAML 配置](examples/scenario_config.yaml) | 全部 | 基于场景测试的 YAML 配置示例 |

### 公共 Mock 模块

所有示例都共享一个公共 mock 模块（`examples/common/`），提供可重用的 mock 客户端和检查函数：

**可用的 Mock 客户端：**
- `ResourceClient` - 资源管理（启动、停止、重启）
- `VMClient` - 虚拟机操作（创建、启动、停止、删除）
- `TaskClient` - 任务队列管理（处理、重试、完成）
- `DatabaseClient` - 数据库操作（创建、扩容、添加副本、删除）

**可用的检查函数：**
- `check_resource_started`, `check_resource_stopped`
- `check_vm_created`, `check_vm_running`, `check_vm_stopped`
- `check_database_created`, `check_database_scaled`
- `check_high_priority`

### 运行示例

```bash
# 运行单个示例
python examples/basic_setup.py
python examples/scenario_test.py
python examples/custom_mode.py
python examples/advanced_usage.py

# 或从 examples 目录运行
cd examples
python basic_setup.py
```

每个示例的详细文档请参阅 [examples/README.md](examples/README.md)。

## 贡献

欢迎贡献！详情请参阅 [CONTRIBUTING.md](CONTRIBUTING.md)。

1. Fork 本仓库
2. 创建您的特性分支 (`git checkout -b feature/amazing-feature`)
3. 提交您的更改 (`git commit -m 'Add amazing feature'`)
4. 推送到分支 (`git push origin feature/amazing-feature`)
5. 开启 Pull Request

## 许可证

本项目采用 Apache License 2.0 许可证 - 详见 [LICENSE](LICENSE) 文件。

## 致谢

- 为测试复杂的云平台状态转换而构建
- 灵感来源于基于模型的测试和状态机设计模式

## 联系方式

- **GitHub**: [https://github.com/leojohn/deep-explore](https://github.com/leojohn/deep-explore)
- **Issues**: [https://github.com/leojohn/deep-explore/issues](https://github.com/leojohn/deep-explore/issues)
- **Email**: liaozynb@gmail.com
