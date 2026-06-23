# dataclass 用于快速定义主要用来保存数据的类
from dataclasses import dataclass


# frozen=True 表示对象创建后，字段不能再被修改
# 这样可以避免模型注册信息在运行过程中被意外改变
@dataclass(frozen=True)
class ModelRegistration:
    # 网关对外公开的模型名称
    # 客户端请求模型时使用这个名字
    public_model: str

    # 负责处理该模型请求的 Provider 名称
    # 当前只有 mock，后续可能有 vllm、sglang 等
    provider_name: str

    # 下游模型服务中的真实模型名称
    # 公开模型名和真实模型名可以不同
    upstream_model: str

    # 表示当前模型是否启用
    # 默认值为 True
    enabled: bool = True


class ModelRegistry:
    """模型注册表，用于保存和查询网关中的模型信息。"""

    def __init__(self, models: list[ModelRegistration]) -> None:
        # 将模型列表转换成字典
        # 键是公开模型名，值是对应的模型注册信息
        #
        # 例如：
        # {
        #     "gateway-mock": ModelRegistration(...)
        # }
        #
        # 使用字典后，可以根据模型名快速查询模型
        self._models = {
            model.public_model: model
            for model in models
        }

    def list_models(self) -> list[ModelRegistration]:
        """返回注册表中的全部模型。"""

        # self._models.values() 得到字典中的所有模型对象
        # list() 将其转换成普通列表
        return list(self._models.values())

    def get_model(
        self,
        public_model: str,
    ) -> ModelRegistration | None:
        """根据公开模型名查询模型，不存在时返回 None。"""

        # dict.get() 查询不到时不会报错，而是返回 None
        return self._models.get(public_model)


def create_default_registry() -> ModelRegistry:
    """创建包含默认 Mock 模型的内存注册表。"""

    # 创建一个默认的模拟模型注册信息
    # 创建一个ModelRegistration类
    mock_model = ModelRegistration(
        public_model="gateway-mock",
        provider_name="mock",
        upstream_model="gateway-mock",
    )

    # 将默认模型放入注册表并返回
    return ModelRegistry([mock_model])

