# DeepExplore 架构设计文档

## 1. 项目概述

### 1.1 问题描述

当前方案的目标是通过自动化手段解决以下问题：

- 不同配置的资源在执行某些功能组合后出现的隐蔽性问题
- 这些问题难以通过常规测试分析与设计覆盖
- 手动投入大量测试资源，但成本效益偏低
- 云平台功能测试在复杂状态转换场景下的验证需求

### 1.2 解决方案

DeepExplore 利用**自动化功能探索测试**替代低效的人工测试，采用以下核心设计思想：

- **FSM（有限状态机）**：跟踪实例状态变化
- **MBT（模型驱动测试）**：多样化的测试执行模型
- **SC（停止条件）**：灵活的测试终止策略
- **Action管理**：封装动作执行的前置检查、执行和后置验证

通过工厂模式实现配置驱动的测试定义，无需修改代码即可灵活配置测试场景。

## 2. 核心架构

### 2.1 架构图

```
┌─────────────────────────────────────────────────────────────────┐
│                      DeepExplore Framework                         │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌─────────────────────┐    ┌─────────────────────┐            │
│  │  DeepExploreLoader  │───▶│  Configuration      │            │
│  └─────────────────────┘    │  (YAML/JSON)        │            │
│           │                  └─────────────────────┘            │
│           ▼                                                    │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │                    DeepExploreMode                       │   │
│  │  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  │   │
│  │  │ Random       │  │ Sequence     │  │ Custom       │  │   │
│  │  │ Scenario     │  │ Scenario     │  │ Mode         │  │   │
│  │  └──────────────┘  └──────────────┘  └──────────────┘  │   │
│  │  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  │   │
│  │  │ Random       │  │ Sequence     │  │ Custom       │  │   │
│  │  │ Action       │  │ Action       │  │ Mode         │  │   │
│  │  └──────────────┘  └──────────────┘  └──────────────┘  │   │
│  └─────────────────────────────────────────────────────────┘   │
│           │                                                    │
│           ▼                                                    │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │                      Scenarios / Actions                 │   │
│  │  ┌────────────────────────────────────────────────────┐ │   │
│  │  │ DeepExploreScenario (场景：多个Action的组合)        │ │   │
│  │  │  ├── Preconditions (前置条件)                       │ │   │
│  │  │  └── Action List (动作列表)                         │ │   │
│  │  │      └── DeepExploreAction                         │ │   │
│  │  └────────────────────────────────────────────────────┘ │   │
│  │  ┌────────────────────────────────────────────────────┐ │   │
│  │  │ DeepExploreAction (单个动作)                       │ │   │
│  │  │  ├── Preconditions                                │ │   │
│  │  │  ├── Pre-checks (前置检查)                         │ │   │
│  │  │  ├── ActionExecutor (动作执行器)                   │ │   │
│  │  │  └── Post-checks (后置验证)                        │ │   │
│  │  └────────────────────────────────────────────────────┘ │   │
│  └─────────────────────────────────────────────────────────┘   │
│           │                                                    │
│           ▼                                                    │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │                 DeepExploreObject                       │   │
│  │  ├── eris_instance_dict (ERIS实例管理)                  │   │
│  │  ├── data (实例状态数据)                                │   │
│  │  ├── arg_resolver() (动态参数解析)                      │   │
│  │  ├── update_state() (状态更新+重试机制)                  │   │
│  │  └── get_status() / _do_update_state() (抽象方法)       │   │
│  └─────────────────────────────────────────────────────────┘   │
│                                                                  │
├─────────────────────────┬──────────────────────────────────────┤
│  停止条件                │  前置条件模块                         │
│  DeepExploreStopping    │  DeepExplorePrecondition              │
│  Criteria               │                                      │
│  ├─ Step                │  ├─ Status (状态匹配)                 │
│  ├─ Time                │  ├─ Data (数据匹配)                   │
│  └─ EndTime             │  └─ Function (函数检查)               │
├─────────────────────────┴──────────────────────────────────────┤
│  工具类                                                         │
│  DeepExploreUtil                                                │
│  ├─ resolve_args() (占位符解析)                                │
│  ├─ dynamic_import() (动态导入)                                │
│  └─ validate() (配置验证)                                      │
├─────────────────────────────────────────────────────────────────┤
│  公共客户端管理                                                  │
│  DeepExplorePublicManager                                       │
│  └─ create_public_client() (动态创建客户端)                     │
└─────────────────────────────────────────────────────────────────┘
```

### 2.2 设计模式

| 设计模式 | 应用位置 | 说明 |
|---------|---------|------|
| 工厂模式 | `DeepExploreModeFactory`<br>`DeepExplorePreconditionFactory`<br>`DeepExploreStoppingCriteriaFactory` | 通过配置创建对象，支持扩展 |
| 策略模式 | `DeepExploreMode` 及其子类 | 不同的测试执行策略 |
| 模板方法 | `DeepExploreObject` | 定义状态更新流程，子类实现具体逻辑 |
| 建造者模式 | `DeepExploreLoader` | 分步构建复杂的测试对象 |

## 3. 核心组件详解

### 3.1 有限状态机 (FSM)

#### 3.1.1 DeepExploreObject

**作用**：测试探索对象基类，提供状态管理和 ERIS 实例管理

**核心功能**：

1. **状态跟踪**
   - `data` 字段：统一存储实例的所有信息（不限于云主机状态，而是完整实例数据）
   - 自动缓存机制 + 3次重试更新

2. **ERIS 集成**
   - `eris_instance_dict`: 字典存储，key 为 action_id，value 为 ERIS 实例
   - 天然支持 ERIS 异常注入和恢复框架

3. **动态参数解析**
   - `arg_resolver()`: 将配置文件中的占位符解析为运行时具体值
   - 支持格式：
     - `_resolver_method_name()` - 无参数调用
     - `_resolver_method_args_arg1_arg2()` - 带参数调用
     - `_resolver_key=value` - 命名参数

**抽象方法（需子类实现）**：
```
@abstractmethod
def _do_update_state(self):  # 执行实际状态更新
    pass

@abstractmethod
def get_status(self):  # 获取当前状态返回 (action_id, object)
    pass
```

### 3.2 模型驱动测试 (MBT)

#### 3.2.1 DeepExploreMode

**基类**： 提供场景/动作执行统计功能

**内置模式**：

1. **RandomScenarioMode** - 随机场景模式
   - 从可用场景中随机选择执行
   - 每次执行检查前置条件

2. **SequenceScenarioMode** - 顺序场景模式
   - 按顺序执行所有场景
   - 支持 reverse 参数逆序执行

3. **RandomActionMode** - 随机动作模式
   - 直接随机执行单个动作
   - 更细粒度的测试控制

4. **SequenceActionMode** - 顺序动作模式
   - 按顺序执行所有动作
   - 支持 reverse 参数逆序执行

**扩展方式**：
```
class CustomMode(DeepExploreMode):
    def exec_test(self):
        # 自定义测试逻辑
        pass
```

#### 3.2.2 测试统计

每次测试执行后自动记录：
- 已执行场景/动作的顺序
- 各场景/动作的执行频次
- 便于测试覆盖度分析

### 3.3 停止条件 (SC)

#### 3.3.1 DeepExploreStoppingCriteria

**支持的停止条件**：

| 类型 | 类名 | 参数 | 说明 |
|-----|------|-----|------|
| 步数 | `DeepExploreStepStoppingCriteria` | `max_steps` | 执行指定次数后停止 |
| 时间 | `DeepExploreTimeStoppingCriteria` | `duration` (秒) | 运行指定时长后停止 |
| 截止时间 | `DeepExploreEndTimeStoppingCriteria` | `end_time_str` | 到达指定时间停止 (YYYY-MM-DD HH:MM:SS) |

**扩展方式**：
```
class CustomStoppingCriteria(DeepExploreStoppingCriteria):
    def is_matched(self):
        # 自定义停止条件逻辑
        return True/False
```

### 3.4 前置条件

#### 3.4.1 DeepExplorePrecondition

**支持的前置条件类型**：

1. **StatusPrecondition** - 状态匹配
   - 验证对象状态是否在允许列表中

2. **MatchDataPrecondition** - 数据匹配
   - 递归验证对象数据是否包含指定结构
   - 支持字典、列表嵌套匹配

3. **FunctionPrecondition** - 函数检查
   - 执行自定义函数并验证结果

**扩展方式**：
```
class CustomPrecondition(DeepExplorePrecondition):
    def check_precondition(self, deep_explore_object):
        # 自定义前置条件逻辑
        return True/False
```

### 3.5 测试内容

#### 3.5.1 DeepExploreScenario

**作用**：将多个 Action 组合为一个固定场景

**应用场景**：
- 可靠性测试：异常注入和恢复需要成对出现
- 功能组合测试：多个步骤组成完整业务流程

**执行方式**：内部 Action 顺序执行（暂不支持并发，可扩展）

**设计建议**：当测试内容为 Scenario 时，内部的 Action 不建议有独立的 Precondition

#### 3.5.2 DeepExploreAction

**作用**：测试探索动作执行器，封装动作的完整生命周期

**执行流程**：
```
┌─────────────────────────────────────────────┐
│  1. 更新状态 (配置项：update_positions)    │
│  ┌─────────────────────────────────────┐   │
│  │  start (可选)                       │   │
│  │  before_exec_action (可选)          │   │
│  │  after_exec_action (可选)           │   │
│  │  end (默认)                         │   │
│  └─────────────────────────────────────┘   │
│                                             │
│  2. 执行 Pre-checks (前置检查)              │
│                                             │
│  3. 执行 Action (通过 ActionExecutor)       │
│                                             │
│  4. 执行 Post-checks (后置验证)             │
│                                             │
│  5. 返回结果                                │
└─────────────────────────────────────────────┘
```

#### 3.5.3 DeepExploreActionExecutor

**封装内容**：
- `action_id`: 动作唯一标识
- `action_name`: 方法名称
- `action_public_client`: 客户端对象
- `action_exec_user`: 执行用户
- `except_meet_exception`: 是否预期异常
- `action_args`: 动作参数（支持占位符解析）

### 3.6 DeepExploreActionCheck

**作用**：动态加载和执行检查逻辑

**功能**：
- 支持动态导入检查函数
- 参数解析（支持占位符）
- 结果验证

**复用框架**：复用现有的检查框架，避免重复开发

### 3.7 DeepExploreLoader

**作用**：配置加载器，从配置文件创建完整的测试对象

**加载流程**：
```
配置文件 (YAML/JSON)
    │
    ▼
DeepExploreLoader.load_deep_explore_mode()
    │
    ├──> stopping_criteria_list ──▶ DeepExploreStoppingCriteriaFactory
    │
    ├──> scenario_list / action_list
    │       │
    │       ▼
    │   ┌─────────────────────────────────┐
    │   │ Preconditions                  │
    │   └─────────────────────────────────┘
    │       │
    │       ▼
    │   ┌─────────────────────────────────┐
    │   │ Action List                    │
    │   │   ├─ ActionExecutor            │
    │   │   ├─ Pre-checks                │
    │   │   └─ Post-checks               │
    │   └─────────────────────────────────┘
    │
    ▼
DeepExploreModeFactory.create_mode()
    │
    ▼
测试模式实例
```

### 3.8 DeepExploreUtil

**核心功能**：

1. **resolve_args()** - 占位符参数解析
   - 递归处理嵌套结构（dict、list、tuple）
   - 支持多种解析器格式

2. **dynamic_import()** - 动态导入
   - 支持模块、类、方法的动态加载
   - 自动处理导入路径

3. **validate()** - 配置验证
   - 验证 YAML/JSON 配置语法
   - 检查 resolver 方法的有效性
   - 验证接口方法和参数

### 3.9 DeepExplorePublicManager

**作用**：公共客户端管理器

**功能**：
- 根据客户端名称动态创建客户端实例
- 支持灵活的模块路径配置
- 统一的客户端实例化入口

## 4. 配置示例

### 4.1 场景模式配置

```yaml
mode_type: random_scenario

stopping_criteria_list:
  - criteria_type: time
    duration: 7200  # 2小时

scenario_list:
  - scenario_name: "VM创建与销毁场景"
    scenario_precondition_list:
      - precondition_type: status
        precondition_data: ["available", "stopped"]
        compare_result: true
    action_list:
      - action_id: "create_vm"
        action_name: "create_instance"
        action_public_client: "vm.VMClient"
        action_args:
          - "_resolver_vm_name"
          - flavor_id: "small"
          - image_id: "ubuntu-20.04"
        action_pre_check_list:
          - check_info:
              - "vm.check_quota"
            check_result: true
        action_post_check_list:
          - check_info:
              - "vm.check_vm_status"
              - "_resolver_vm_id"
            check_result: "running"

      - action_id: "delete_vm"
        action_name: "delete_instance"
        action_public_client: "vm.VMClient"
        action_args:
          - "_resolver_vm_id"
        update_positions: ["end"]
```

### 4.2 动作模式配置

```yaml
mode_type: sequence_action
kwargs:
  reverse: false  # 是否逆序执行

stopping_criteria_list:
  - criteria_type: step
    max_steps: 100

action_list:
  - action_name: "start_instance"
    action_public_client: "vm.VMClient"
    action_args:
      - "_resolver_vm_id"
    action_precondition_list:
      - precondition_type: status
        precondition_data: ["stopped"]
        compare_result: true
    except_meet_exception: false

  - action_name: "stop_instance"
    action_public_client: "vm.VMClient"
    action_args:
      - "_resolver_vm_id"
    action_precondition_list:
      - precondition_type: status
        precondition_data: ["running"]
        compare_result: true
```

## 5. 扩展指南

### 5.1 自定义测试模式

```
from deep_explore_mode import DeepExploreMode

class CustomMode(DeepExploreMode):
    def __init__(self, deep_explore_object, stop_criteria_list, test_objects):
        super().__init__()
        self.deep_explore_object = deep_explore_object
        self.stop_criteria_list = stop_criteria_list
        self.test_objects = test_objects

    def exec_test(self):
        # 自定义测试逻辑
        while self._should_continue():
            # 按需选择测试对象
            test_obj = self._select_object()
            test_obj.exec_action(self.deep_explore_object)

    def _select_object(self):
        # 自定义选择逻辑
        pass

    def _should_continue(self):
        # 自定义继续条件
        for criteria in self.stop_criteria_list:
            if criteria.is_matched():
                return False
        return True
```

### 5.2 自定义停止条件

```
from deep_explore_stopping_criteria import DeepExploreStoppingCriteria

class CustomStoppingCriteria(DeepExploreStoppingCriteria):
    def __init__(self, custom_param):
        self.custom_param = custom_param

    def is_matched(self):
        # 自定义判断逻辑
        return True
```

### 5.3 自定义前置条件

```
from deep_explore_precondition import DeepExplorePrecondition

class CustomPrecondition(DeepExplorePrecondition):
    def __init__(self, custom_data):
        self.custom_data = custom_data

    def check_precondition(self, deep_explore_object):
        # 自定义判断逻辑
 status = deep_explore_object.get_status()
        return status in self.custom_data
```

---

**文档版本**: 1.0.0
**最后更新**: 2025-01-24