import json
import yaml # Added for YAML parsing
from pocketflow import Node, BatchNode, BatchFlow # Assuming pocketflow.py is in the same directory or PYTHONPATH
from utils.youtube_processor import get_youtube_video_info
from utils.call_llm import call_llm
from utils.html_generator import generate_html_report
import os
import re

class ProcessYouTubeURLNode(Node):
    """Process YouTube URL to extract video information."""
    def prep(self, shared):
        print(f"Node: Preparing to process YouTube URL: {shared['video_info']['url']}")
        return shared["video_info"]["url"]

    def exec(self, prep_res): # prep_res is the URL from shared_store["video_info"]["url"]
        print(f"Node: Processing YouTube URL: {prep_res}")
        return get_youtube_video_info(prep_res)

    def post(self, shared, prep_res, exec_res):
        shared["video_info"] = exec_res # exec_res is the dict from get_youtube_video_info
        print(f"Node: Stored video_info: Title '{shared['video_info']['title']}'")
        return "default"

class ExtractTopicsAndQuestionsNode(Node):
    """Extract interesting topics from transcript and generate questions for each topic."""
    def prep(self, shared):
        print("Node: Preparing to extract topics and questions.")
        transcript = shared.get("video_info", {}).get("transcript", "")
        title = shared.get("video_info", {}).get("title", "Untitled Video")
        if not transcript:
            print("Warning: Transcript is empty in ExtractTopicsAndQuestionsNode.prep")
        return transcript, title

    def exec(self, prep_res):
        transcript, title = prep_res
        print(f"Node: Extracting topics and questions for video '{title}' (transcript first 50 chars): '{transcript[:50]}...'")
        
        if not transcript:
            print("Warning: Transcript is empty in ExtractTopicsAndQuestionsNode.exec, returning empty topics.")
            return []

        # Single prompt to extract topics and questions together
        prompt = f"""
An expert content analyzer has been tasked with identifying the most engaging aspects of a YouTube video. 
Based on the video's title and full transcript, please perform the following:

1. Identify a maximum of 5 distinct and most interesting topics discussed in the video.
2. For each of these topics, generate a maximum of 3 thought-provoking questions. These questions should encourage deeper thinking about the topic and do not necessarily need to be explicitly answered in the video. Clarification questions or questions that explore implications are good.

VIDEO TITLE: {title}

TRANSCRIPT:
{transcript}

Format your entire response strictly in YAML, following this structure exactly:

```yaml
topics:
  - title: |
      First extracted topic title (should be a concise summary of the topic)
    questions:
      - |
        First question related to the first topic?
      - |
        Second question related to the first topic?
      - |
        Third question related to the first topic (if applicable).
  - title: |
      Second extracted topic title
    questions:
      - |
        First question related to the second topic?
      # ... more questions for the second topic, up to 3
  # ... more topics, up to 5 in total
```
"""
        
        llm_response_yaml_str = call_llm(prompt, system_message="You are an AI assistant that processes text and outputs structured data in YAML format.")
        
        result_topics = []
        try:
            # Clean up the response to get only the YAML part
            if "```yaml" in llm_response_yaml_str:
                yaml_content = llm_response_yaml_str.split("```yaml")[1].split("```")[0].strip()
            elif "```" in llm_response_yaml_str: # Simpler ``` block
                 yaml_content = llm_response_yaml_str.split("```")[1].strip()
            else:
                yaml_content = llm_response_yaml_str # Assume the whole response is YAML if no fences

            parsed_data = yaml.safe_load(yaml_content)
            
            if parsed_data and "topics" in parsed_data and isinstance(parsed_data["topics"], list):
                raw_topics = parsed_data["topics"]
                for i, raw_topic in enumerate(raw_topics[:5]): # Max 5 topics
                    if isinstance(raw_topic, dict) and "title" in raw_topic and "questions" in raw_topic:
                        topic_title = str(raw_topic["title"]).strip()
                        
                        formatted_questions = []
                        if isinstance(raw_topic["questions"], list):
                            for j, q_text in enumerate(raw_topic["questions"][:3]): # Max 3 questions
                                formatted_questions.append({
                                    "original": str(q_text).strip(),
                                    "rephrased": "", # To be filled later
                                    "answer": ""      # To be filled later
                                })
                        
                        if topic_title and formatted_questions: # Ensure topic has title and questions
                            result_topics.append({
                                "title": topic_title,
                                "rephrased_title": "", # To be filled later
                                "questions": formatted_questions
                            })
            else:
                print(f"Warning: LLM response YAML was not in the expected format or no topics found. Response: {llm_response_yaml_str}")

        except yaml.YAMLError as e:
            print(f"Error parsing YAML from LLM: {e}")
            print(f"LLM Raw Response was: {llm_response_yaml_str}")
        except Exception as e:
            print(f"An unexpected error occurred during YAML processing: {e}")
            print(f"LLM Raw Response was: {llm_response_yaml_str}")

        if not result_topics:
            print("Warning: No topics were successfully extracted. Populating with fallback.")
            # Fallback if parsing fails or LLM output is bad
            result_topics.append({
                "title": "Fallback Topic: Could not parse LLM response",
                "rephrased_title": "",
                "questions": [
                    {"original": "Fallback Question: What went wrong with LLM output?", "rephrased": "", "answer": ""}
                ]
            })
            
        return result_topics

    def post(self, shared, prep_res, exec_res):
        shared["topics"] = exec_res # exec_res is the list of topics with questions
        print(f"Node: Stored {len(shared['topics'])} topics with their initial questions.")
        return "default"

class ProcessTopicNode(BatchNode):
    """Batch process each topic for rephrasing titles, questions, and generating ELI5 answers."""
    def prep(self, shared):
        print(f"Node: Preparing to batch process {len(shared.get('topics', []))} topics.")
        topics = shared.get("topics", [])
        transcript = shared.get("video_info", {}).get("transcript", "")
        # Returns a list of (topic_item, transcript) tuples. Each tuple will be passed to exec().
        # We pass the full transcript for now; a more advanced version might pass relevant excerpts.
        return [(topic, transcript) for topic in topics]

    def exec(self, prep_res_item):
        topic_item, transcript = prep_res_item # Unpack the tuple
        
        original_topic_title = topic_item['title']
        original_questions_list = [q["original"] for q in topic_item["questions"]]

        print(f"Node: Batch processing topic: '{original_topic_title}'")

        # Construct the detailed prompt for a single LLM call per topic
        questions_str_for_prompt = "\n".join([f"- {q}" for q in original_questions_list])
        
        # For transcript excerpt, we can use a snippet or a more sophisticated selection. Using first N chars for simplicity.
        transcript_excerpt = transcript[:1500] # Use a portion of the transcript

        prompt = f"""You are a content simplifier and engager for children. 
Given a topic, a list of original questions related to it from a YouTube video, and an excerpt from the video's transcript, your task is to:
1. Rephrase the topic title to be catchy, interesting, and short (around 10 words).
2. For each original question, rephrase it to be clear, interesting, and suitable for a 5-year-old (around 15 words).
3. For each rephrased question, provide a simple ELI5 (Explain Like I'm 5) answer (around 100 words per answer).

GUIDELINES FOR ANSWERS:
- Format them using simple HTML: use <b> for emphasis on key terms and <i> for slight emphasis or foreign/technical terms if necessary.
- Prefer ordered lists (<ol><li>...</li></ol>) or unordered lists (<ul><li>...</li></ul>) if the answer involves steps or multiple points. For example, a list item could start with a <b>bolded key point</b> followed by its explanation.
- When you introduce an important keyword (especially if it might be new to a child), bold it and explain it in very simple terms. For example: "<b>Photosynthesis</b> is a big word for how plants make their own food using sunlight!"
- Keep the overall tone friendly, engaging, and ensure the answers are genuinely easy for a 5-year-old to understand.
- Ensure answers are concise and directly address the rephrased question.

ORIGINAL TOPIC TITLE: {original_topic_title}

ORIGINAL QUESTIONS:
{questions_str_for_prompt}

TRANSCRIPT EXCERPT (for context, not for direct quotation unless a term needs defining):
{transcript_excerpt}

Now, provide your full response strictly in YAML format as specified below:

```yaml
rephrased_title: |
    Rephrased catchy topic title (approx. 10 words)
questions:
  - original: |
      {original_questions_list[0] if len(original_questions_list) > 0 else 'Question 1 not provided'}
    rephrased: |
      Rephrased interesting question 1 (approx. 15 words)
    answer: |-
      ELI5 HTML answer for question 1 (approx. 100 words). Example: <p><b>Gravity</b> is like an invisible glue that keeps everything stuck to the Earth!</p><ol><li><b>It pulls things down:</b> That's why your toys fall!</li><li><b>It keeps us on the ground:</b> So we don't float away!</li></ol>
  - original: |
      {original_questions_list[1] if len(original_questions_list) > 1 else 'Question 2 not provided'}
    rephrased: |
      Rephrased interesting question 2 (approx. 15 words)
    answer: |-
      ELI5 HTML answer for question 2 (approx. 100 words).
  # Add more questions here if present in the input, up to the number of original questions provided.
  # Ensure the 'original' fields exactly match the questions provided above.
```
"""
        
        llm_response_yaml_str = call_llm(prompt, system_message="You are an AI assistant that processes text and outputs structured data in YAML format following specific guidelines for content and HTML formatting.")

        updated_topic_item = topic_item.copy() # Start with a copy to preserve original data if parsing fails

        try:
            if "```yaml" in llm_response_yaml_str:
                yaml_content = llm_response_yaml_str.split("```yaml")[1].split("```")[0].strip()
            elif "```" in llm_response_yaml_str:
                 yaml_content = llm_response_yaml_str.split("```")[1].strip()
            else:
                yaml_content = llm_response_yaml_str
            
            parsed_llm_data = yaml.safe_load(yaml_content)

            if parsed_llm_data and isinstance(parsed_llm_data, dict):
                updated_topic_item["rephrased_title"] = parsed_llm_data.get("rephrased_title", original_topic_title).strip()
                
                llm_questions = parsed_llm_data.get("questions", [])
                processed_questions_from_llm = []
                
                # Match LLM questions back to original questions if necessary, or assume order
                # For simplicity, we'll map them by order, ensuring we don't create more than we had.
                for i, q_data_orig in enumerate(updated_topic_item["questions"]):
                    if i < len(llm_questions) and isinstance(llm_questions[i], dict):
                        llm_q_item = llm_questions[i]
                        processed_questions_from_llm.append({
                            "original": q_data_orig["original"], # Keep original from before LLM
                            "rephrased": str(llm_q_item.get("rephrased", q_data_orig["original"])).strip(),
                            "answer": str(llm_q_item.get("answer", "Answer not provided by LLM.")).strip()
                        })
                    else:
                        # If LLM provided fewer questions than original, keep original with no answer
                        processed_questions_from_llm.append({
                            "original": q_data_orig["original"],
                            "rephrased": q_data_orig["original"], # Fallback
                            "answer": "Answer not generated."
                        })
                updated_topic_item["questions"] = processed_questions_from_llm
            else:
                print(f"Warning: LLM response for topic '{original_topic_title}' was not in expected dict format or empty. LLM Raw: {llm_response_yaml_str}")
                # Keep original data if parsing fails for this item

        except yaml.YAMLError as e:
            print(f"Error parsing YAML for topic '{original_topic_title}': {e}. LLM Raw: {llm_response_yaml_str}")
        except Exception as e:
            print(f"An unexpected error occurred during YAML processing for topic '{original_topic_title}': {e}. LLM Raw: {llm_response_yaml_str}")
            
        return updated_topic_item # Return the (potentially) modified topic_item

    def post(self, shared, prep_res, exec_res_list):
        # exec_res_list contains the processed topic_items from each exec() call
        shared["topics"] = exec_res_list # Update shared store with fully processed topics
        print(f"Node: Finished batch processing. Stored {len(shared['topics'])} fully processed topics.")
        return "default"


class GenerateHTMLNode(Node):
    """Create final HTML output."""
    def prep(self, shared):
        print("Node: Preparing to generate HTML report.")
        return shared.get("video_info", {}), shared.get("topics", [])

    def exec(self, prep_res):
        video_info, topics_data = prep_res
        print(f"Node: Generating HTML with video title '{video_info.get('title', 'N/A')}' and {len(topics_data)} topics.")
        if not video_info:
            print("Warning: Video info is missing for HTML generation.")
            video_info = {"title": "Error: Video Info Missing", "thumbnail_url": ""}
        return generate_html_report(video_info, topics_data)

    def post(self, shared, prep_res, exec_res):
        shared["html_output"] = exec_res # exec_res is the HTML string
        
        # 确保examples目录存在
        examples_dir = os.path.join(os.getcwd(), "examples")
        if not os.path.exists(examples_dir):
            os.makedirs(examples_dir)
            print(f"Created directory: {examples_dir}")
        
        # 从视频标题生成安全的文件名
        video_title = shared.get("video_info", {}).get("title", "unknown_video")
        
        # 简单的文件名清理函数
        def clean_filename(filename):
            # 移除非法字符并将空格替换为下划线
            return re.sub(r'[^\w\-_\. ]', '', filename).replace(' ', '_')[:200]
        
        safe_filename = clean_filename(video_title)
        
        # 如果文件名为空，使用默认名称
        if not safe_filename:
            safe_filename = "youtube_eli5_summary"
        
        # 添加.html扩展名
        html_filename = f"{safe_filename}.html"
        output_path = os.path.join(examples_dir, html_filename)
        
        # 保存HTML文件
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(exec_res)
        
        print(f"Node: Stored HTML output (length: {len(shared['html_output'])} chars).")
        print(f"Node: Saved HTML report to {output_path}")
        
        return "default"

# According to design.md, Content Processing is a subgraph containing ProcessTopic.
# In PocketFlow, this can be represented by a Flow that is then run by a BatchFlow or as a BatchNode directly.
# For simplicity with the current design, ProcessTopicNode is a BatchNode.
# If `contentBatch` was a BatchFlow, it would look like:
# class ContentBatchFlow(BatchFlow):
#     def prep(self, shared):
#         # This would return a list of parameter dictionaries, one for each topic
#         # e.g., [{"topic_index": 0}, {"topic_index": 1}, ...]
#         return [{"topic_index": i} for i, _ in enumerate(shared.get("topics", []))]
    
#     def post(self, shared, prep_res, exec_res_list):
#         # exec_res_list here would be results from each sub-flow run
#         # We would then need to aggregate/update shared["topics"] accordingly
#         print(f"ContentBatchFlow: Processed {len(exec_res_list)} items.")
#         # Logic to update shared["topics"] based on the results of sub-flow runs
#         # This part is more complex as each sub-flow run modifies shared_store or returns data
#         return "default"

# And ProcessTopicNode would be a regular Node in that case, using params["topic_index"]
# class ProcessTopicNodeForBatchFlow(Node):
#     def prep(self, shared):
#         topic_index = self.params["topic_index"]
#         return shared["topics"][topic_index]
#     def exec(self, topic_item): ... # same as ProcessTopicNode.exec
#     def post(self, shared, prep_res, exec_res):
#         topic_index = self.params["topic_index"]
#         shared["topics"][topic_index] = exec_res # exec_res is the processed topic_item
#         return "default"
