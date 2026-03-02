"""
测试需求分析节点的工作流
"""
from langgraph.graph import StateGraph, END
from graphs.state import (
    GlobalState,
    GraphInput,
    GraphOutput
)
from graphs.nodes.requirement_analysis_node import requirement_analysis_node

# 创建状态图，指定图的入参和出参
builder = StateGraph(GlobalState, input_schema=GraphInput, output_schema=GraphOutput)

# 添加节点
builder.add_node("requirement_analysis", requirement_analysis_node)

# 设置入口点
builder.set_entry_point("requirement_analysis")

# 添加边：从 requirement_analysis 到 END
builder.add_edge("requirement_analysis", END)

# 编译图
main_graph = builder.compile()

if __name__ == "__main__":
    # 测试运行
    print("开始测试需求分析节点...")
    
    # 创建测试输入 - 使用一个公开的 GitHub Issue
    test_input = {
        "github_issue_url": "https://github.com/facebook/react/issues/25016"
    }
    
    # 运行工作流
    result = main_graph.invoke(test_input)
    
    # 打印结果
    print("\n" + "="*50)
    print("工作流执行结果:")
    print("="*50)
    print(f"功能列表: {result.get('feature_list', [])}")
    print(f"API 定义: {result.get('api_definitions', [])}")
    print(f"需求摘要:\n{result.get('summary', '')}")
    print("="*50)
