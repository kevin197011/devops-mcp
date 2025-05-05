require 'fast_mcp'

# 创建 MCP 服务器实例
server = FastMcp::Server.new(name: 'my-ai-server', version: '1.0.0')

# 定义一个工具类
class SummarizeTool < FastMcp::Tool
  description "Summarize a given text"

  arguments do
    required(:text).filled(:string).description("Text to summarize")
    optional(:max_length).filled(:integer).description("Maximum length of summary")
  end

  def call(text:, max_length: 100)
    # 实现摘要逻辑
    text.split('.').first(3).join('.') + '...'
  end
end

# 注册工具到服务器
server.register_tool(SummarizeTool)

# 启动服务器
server.start
