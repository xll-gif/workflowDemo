import time
from langchain_core.runnables import RunnableConfig
from langgraph.runtime import Runtime
from coze_coding_utils.runtime_ctx.context import Context
from graphs.state import HelloWorldInput, HelloWorldOutput

def hello_world_node(state: HelloWorldInput, config: RunnableConfig, runtime: Runtime[Context]) -> HelloWorldOutput:
    """
    title: Hello World
    desc: 一个简单的测试节点，接收输入消息并返回处理后的消息
    integrations: 无
    """
    # 记录开始时间
    start_time = time.time()
    
    # 获取上下文
    ctx = runtime.context
    
    # 简单的消息处理
    output_message = f"Hello World! 收到消息: {state.input_message}"
    
    # 计算处理时间
    processing_time = time.time() - start_time
    
    # 返回结果
    return HelloWorldOutput(
        output_message=output_message,
        processing_time=processing_time
    )
