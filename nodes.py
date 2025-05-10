import json
from pocketflow import Node, BatchNode, BatchFlow # Assuming pocketflow.py is in the same directory or PYTHONPATH
from utils.youtube_processor import get_youtube_video_info
from utils.call_llm import call_llm
from utils.html_generator import generate_html_report

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
        return shared["video_info"]["transcript"]

    def exec(self, transcript):
        print(f"Node: Extracting topics and questions from transcript (first 50 chars): '{transcript[:50]}...'")
        # 1. Extract up to 5 interesting topics
        # Simplified: using placeholder topics from call_llm
        topics_prompt = f"Extract up to 5 interesting topics from the following transcript. List them separated by commas: {transcript}"
        extracted_topics_str = call_llm(topics_prompt, system_message="You are an expert in identifying key topics.")
        # topics_list = [t.strip() for t in extracted_topics_str.split(",")[:5]]
        # Using the placeholder directly for now which returns "Placeholder Topics: Topic 1, Topic 2, ..."
        topics_list = [t.strip() for t in extracted_topics_str.replace("Placeholder Topics:", "").split(",")[:5] if t.strip()]
        if not topics_list: # Fallback if parsing placeholder fails
            topics_list = ["Fallback Topic 1", "Fallback Topic 2"]

        topics_with_questions = []
        for topic_title in topics_list:
            # 2. For each topic, generate 3 relevant questions
            questions_prompt = f"Generate 3 relevant questions for the topic: '{topic_title}'. List them separated by semicolons." 
            # The placeholder LLM returns a string like "Placeholder Questions: Q1?; Q2?; Q3?"
            questions_str_from_llm = call_llm(questions_prompt, system_message="You are an expert at generating insightful questions.")
            # questions_list = [q.strip() for q in questions_str_from_llm.split(";")[:3]]
            questions_list = [q.strip() for q in questions_str_from_llm.replace("Placeholder Questions:", "").split(";")[:3] if q.strip()]
            if not questions_list: # Fallback
                questions_list = [f"Default Question 1 for {topic_title}?", f"Default Question 2 for {topic_title}?"]

            topics_with_questions.append({
                "title": topic_title,
                "rephrased_title": "", # To be filled by ProcessTopicNode
                "questions": [{"original": q, "rephrased": "", "answer": ""} for q in questions_list]
            })
        return topics_with_questions

    def post(self, shared, prep_res, exec_res):
        shared["topics"] = exec_res # exec_res is the list of topics with questions
        print(f"Node: Stored {len(shared['topics'])} topics with their initial questions.")
        return "default"

class ProcessTopicNode(BatchNode):
    """Batch process each topic for rephrasing titles, questions, and generating ELI5 answers."""
    def prep(self, shared):
        print(f"Node: Preparing to batch process {len(shared.get('topics', []))} topics.")
        # Returns a list of topics. Each item in this list will be passed to exec()
        return shared.get("topics", []) 

    def exec(self, topic_item):
        # topic_item is a single topic dictionary from the list prepared in prep()
        # This method is called for each topic individually by the BatchNode/Flow mechanism.
        print(f"Node: Batch processing topic: '{topic_item['title']}'")
        
        # Rephrase topic title
        rephrase_topic_prompt = f"Rephrase this topic title for clarity and make it engaging for a 5-year-old: '{topic_item['title']}'"
        topic_item["rephrased_title"] = call_llm(rephrase_topic_prompt, system_message="You are skilled at rephrasing content for children.")

        processed_questions = []
        for q_data in topic_item["questions"]:
            original_question = q_data["original"]
            # Rephrase question
            rephrase_q_prompt = f"Rephrase this question to be simple and clear for a 5-year-old: '{original_question}'"
            rephrased_q = call_llm(rephrase_q_prompt, system_message="You are skilled at rephrasing content for children.")
            
            # Generate ELI5 answer
            # For ELI5, it's good to provide some context, like the rephrased topic title.
            answer_prompt = f"For the topic '{topic_item['rephrased_title']}', explain the answer to this question like I'm 5 years old: '{rephrased_q}'"
            eli5_answer = call_llm(answer_prompt, system_message="Explain things very simply, like for a 5-year-old.")
            
            processed_questions.append({
                "original": original_question,
                "rephrased": rephrased_q,
                "answer": eli5_answer
            })
        topic_item["questions"] = processed_questions
        return topic_item # Return the modified topic_item

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
        print(f"Node: Stored HTML output (length: {len(shared['html_output'])} chars).")
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
