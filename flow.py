from pocketflow import Flow, BatchFlow # Assuming pocketflow.py is available
from nodes import (
    ProcessYouTubeURLNode,
    ExtractTopicsAndQuestionsNode,
    ProcessTopicNode, # This is a BatchNode
    GenerateHTMLNode
)

# The design doc shows: videoProcess --> topicsQuestions --> contentBatch --> htmlGen
# contentBatch is a subgraph that processes each topic.
# ProcessTopicNode is a BatchNode, which handles the iteration over topics internally.
# So, the main flow can be linear if ProcessTopicNode correctly handles the batch of topics.

# Option 1: Linear flow where ProcessTopicNode is a BatchNode
# This aligns with ProcessTopicNode being defined as BatchNode in nodes.py
def create_youtube_eli5_flow():
    """Create the main ELI5 YouTube summarization flow."""
    
    # Instantiate nodes
    video_process_node = ProcessYouTubeURLNode()
    extract_topics_questions_node = ExtractTopicsAndQuestionsNode()
    
    # ProcessTopicNode is a BatchNode. It will internally iterate over topics
    # provided by its prep method (which reads shared["topics"]).
    process_topic_node = ProcessTopicNode()
    
    generate_html_node = GenerateHTMLNode()

    # Connect nodes in sequence
    video_process_node >> extract_topics_questions_node
    extract_topics_questions_node >> process_topic_node
    process_topic_node >> generate_html_node
    
    # Create flow starting with the first node
    main_flow = Flow(video_process_node)
    print("YouTube ELI5 Flow (Linear with BatchNode) created.")
    return main_flow

# Option 2: Using a BatchFlow for contentBatch (more explicit for the diagram)
# This would require ProcessTopicNode to be a regular Node and a ContentBatchFlow wrapper.
# (Commented out as Option 1 is simpler with current Node definitions)

# from nodes import ProcessTopicNodeForBatchFlow # Assuming this variant exists

# class ContentBatchProcessingFlow(BatchFlow):
#     """A BatchFlow to process each topic individually using a sub-flow."""
#     def prep(self, shared):
#         # Returns a list of parameter dicts, one for each topic to process.
#         # Each dict could contain the index of the topic in shared["topics"].
#         num_topics = len(shared.get("topics", []))
#         print(f"ContentBatchProcessingFlow: Preparing to process {num_topics} topics.")
#         return [{"topic_index": i} for i in range(num_topics)]

#     def post(self, shared, prep_res, exec_res_list):
#         # exec_res_list contains results from each sub-flow run (one per topic)
#         # The shared["topics"] should have been updated by the sub-flow's ProcessTopicNodeForBatchFlow
#         print(f"ContentBatchProcessingFlow: Finished processing {len(exec_res_list)} topics via sub-flows.")
#         # No specific data aggregation needed here if sub-nodes write directly to shared["topics"][topic_index]
#         return "default"

# def create_youtube_eli5_flow_with_batchflow():
#     video_process_node = ProcessYouTubeURLNode()
#     extract_topics_questions_node = ExtractTopicsAndQuestionsNode()
    
#     # Sub-flow for processing a single topic
#     # process_single_topic_node = ProcessTopicNodeForBatchFlow() # This would be a regular Node
#     # single_topic_processing_flow = Flow(start=process_single_topic_node)
    
#     # BatchFlow that runs the single_topic_processing_flow for each topic
#     # content_batch_flow = ContentBatchProcessingFlow(start=single_topic_processing_flow)

#     # For now, sticking to BatchNode as per current nodes.py
#     process_topic_batch_node = ProcessTopicNode() # Using the BatchNode directly

#     generate_html_node = GenerateHTMLNode()

#     video_process_node >> extract_topics_questions_node
#     extract_topics_questions_node >> process_topic_batch_node # Connect to the BatchNode
#     process_topic_batch_node >> generate_html_node
    
#     main_flow = Flow(start=video_process_node)
#     print("YouTube ELI5 Flow (with conceptual BatchFlow) created.")
#     return main_flow

