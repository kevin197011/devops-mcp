# Copyright (c) 2025 Kk
#
# This software is released under the MIT License.
# https://opensource.org/licenses/MIT

require 'net/http'
require 'uri'
require 'json'

uri = URI('http://localhost:5678/webhook/d4221b97-6785-49cf-8936-7335b74c33c3/chat')

headers = {
  'Accept' => '*/*',
  'Accept-Language' => 'en-US,en;q=0.9,zh-CN;q=0.8,zh;q=0.7,fil;q=0.6',
  'Cache-Control' => 'no-cache',
  'Connection' => 'keep-alive',
  'Content-Type' => 'application/json',
  'Origin' => 'http://localhost:5678',
  'Pragma' => 'no-cache',
  'Referer' => 'http://localhost:5678/webhook/d4221b97-6785-49cf-8936-7335b74c33c3/chat',
  'Sec-Fetch-Dest' => 'empty',
  'Sec-Fetch-Mode' => 'cors',
  'Sec-Fetch-Site' => 'same-origin',
  'User-Agent' => 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36',
  'X-Instance-Id' => '06e4aeba10bb117147290da895174269849134421682bc73338cacb1425e5d33',
  'sec-ch-ua' => '"Google Chrome";v="135", "Not-A.Brand";v="8", "Chromium";v="135"',
  'sec-ch-ua-mobile' => '?0',
  'sec-ch-ua-platform' => '"macOS"',
  'Cookie' => 'lb:user_data=...; token=...; n8n-auth=...; [其他 cookie 略]'
}

# 注意：这里应当把 cookie 内容处理成一行字符串（如上方），建议仅保留必要的 cookie 项目

chat_input = <<~TEXT
  查询prometheus的主机 cpu mem disk
  - 查询当前1分钟以内的数据
  - 标签为 job="node"
  - 按照cpu mem disk整理为表格
  - 基于当前查询出的数据给出分析，提示可能存在的风险和建议
  - 反馈结果的风险用红色字体提示
TEXT

payload = {
  action: 'sendMessage',
  sessionId: '51aa5ab9-2185-409c-828d-95b4036fcf82',
  chatInput: chat_input
}.to_json

http = Net::HTTP.new(uri.host, uri.port)
request = Net::HTTP::Post.new(uri.request_uri, headers)
request.body = payload

response = http.request(request)

puts "Response code: #{response.code}"
puts "Response body: #{response.body}"
