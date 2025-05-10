# YouTube视频简易解释器 (Explain Like I'm 5)

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![PocketFlow](https://img.shields.io/badge/powered%20by-PocketFlow-ff69b4.svg)](https://github.com/the-pocket/PocketFlow)

这个项目使用AI技术，将YouTube视频内容转化为简化的"像我只有5岁"(ELI5)风格解释。它提取视频字幕，识别关键主题，生成相关问题和儿童友好的解答，并以美观的HTML格式呈现结果。

## 🌟 主要特点

- **自动提取视频信息**：仅需提供YouTube链接，自动获取标题、字幕和缩略图
- **智能主题分析**：从视频内容中识别5个最有价值的主题
- **深入问答生成**：为每个主题创建3个有见地的问题和答案
- **儿童友好的解释**：将复杂概念以适合5岁儿童理解的方式呈现
- **美观报告**：生成一个视觉吸引人的HTML报告，包含所有解释内容

## 📋 运行要求

- Python 3.8+
- 安装以下Python库:
  - pyyaml
  - requests
  - youtube_transcript_api
  - google-generativeai (若使用Gemini模型)
  - 其他依赖库见`requirements.txt`
- Gemini API密钥 (或其他支持的LLM API密钥)

## 🚀 快速开始

1. 克隆此仓库
2. 安装依赖：
   ```bash
   pip install -r requirements.txt
   ```
3. 设置API密钥环境变量：
   ```bash
   # 如果使用Gemini
   export GOOGLE_API_KEY='你的API密钥'
   ```
4. 运行主程序:
   ```bash
   python main.py
   ```
5. 在提示时输入YouTube视频URL
6. 查看`examples`目录下生成的HTML报告

## 🛠️ 技术架构

本项目使用PocketFlow框架实现，这是一个轻量级的有向图工作流框架，专为LLM应用设计。

### 核心组件

1. **视频处理** (`ProcessYouTubeURLNode`)
   - 从YouTube URL提取视频ID、标题、缩略图和字幕
   - 使用`youtube_transcript_api`库获取字幕内容

2. **主题和问题提取** (`ExtractTopicsAndQuestionsNode`) 
   - 使用LLM从字幕中识别最多5个关键主题
   - 为每个主题生成最多3个深思熟虑的问题
   - 返回YAML格式的结构化数据

3. **内容简化处理** (`ProcessTopicNode`)
   - 重新表述每个主题标题，使其更简洁、吸引人
   - 重新表述每个问题，使其对5岁儿童更易理解
   - 生成儿童友好的ELI5解答，使用HTML格式化
   - 批量处理所有主题

4. **HTML生成** (`GenerateHTMLNode`)
   - 创建一个美观的HTML页面展示所有处理后的内容
   - 包含视频标题、缩略图、主题和问答部分
   - 输出文件保存在`examples`目录下，使用视频标题作为文件名

### 数据流

```
YouTube URL → 视频处理 → 主题和问题提取 → 内容简化处理 → HTML生成 → 最终报告
```

## 📊 示例输出

处理后的HTML报告包含：

- 视频标题和缩略图
- 每个主题的简化标题
- 每个主题的问题列表，使用儿童友好的语言重新表述
- 为每个问题提供的ELI5解答，使用HTML格式化以突出关键概念

## 🔧 自定义和扩展

你可以通过修改以下内容来自定义输出：

- `utils/html_generator.py`中的CSS样式
- `nodes.py`中各节点的LLM提示词
- 更改`call_llm.py`中使用的LLM模型

## 📝 备注

- 此项目需要互联网连接以访问YouTube和LLM API
- 某些YouTube视频可能没有可用字幕
- LLM响应质量取决于所使用的模型和字幕内容质量

---

使用AI技术让复杂内容变得简单易懂！
