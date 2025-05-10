import os
import google.generativeai as genai

# Learn more about calling the LLM: https://the-pocket.github.io/PocketFlow/utility_function/llm.html
def call_llm(prompt: str, system_message: str = "You are a helpful assistant.", model_name: str = "gemini-2.5-flash-preview-04-17"):
    """
    Calls a Large Language Model, currently configured for Gemini.
    Uses the GOOGLE_API_KEY environment variable.
    The system_message for Gemini is typically handled by forming a specific prompt structure
    or using the system_instruction parameter if available for the chosen model/method.
    For basic text generation with gemini-flash, we can prepend the system message to the user prompt.
    """
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        print("Error: GOOGLE_API_KEY environment variable not found.")
        print("Please set it to your Google API key for Gemini.")
        print("Returning placeholder response.")
        # Fallback to placeholder if API key is missing
        if "extract topics" in prompt.lower():
            return "Placeholder Topics: Topic 1, Topic 2, Topic 3, Topic 4, Topic 5"
        elif "generate questions" in prompt.lower():
            return "Placeholder Questions: Question 1?, Question 2?, Question 3?"
        # ... (keep other placeholder conditions if needed or remove them)
        return "Placeholder LLM Response due to missing API key"

    try:
        genai.configure(api_key=api_key)
        
        # For Gemini, system messages can be part of the prompt or a specific parameter.
        # Here, we prepend the system message to the main prompt for simplicity with generate_content.
        # More complex scenarios (e.g. chat) might use `start_chat` with history including roles.
        
        # Note: Gemini API's `generate_content` can take `system_instruction` for some models.
        # Let's assume we are using a model and method where prepending is fine for now.
        # Effective system message handling depends on the exact Gemini model and client usage.
        
        full_prompt = []
        if system_message and system_message != "You are a helpful assistant.": # Avoid default if not meaningful
            # Gemini prefers a structured format for messages if using a chat-like model
            # For a simple generation, we might just prepend.
            # If the model supports system_instruction, that would be better.
            # For now, let's assume it's a general text model and prepend to user prompt.
            # A more robust solution would involve checking model capabilities for system instructions.
            full_prompt.append(system_message) # Or format as a specific role if using a chat model
        
        full_prompt.append(prompt)
        
        model = genai.GenerativeModel(model_name)
        response = model.generate_content(full_prompt)
        
        if response.parts:
            return response.text
        else:
            # Handle cases where the response might be empty or blocked
            print(f"Warning: Gemini response was empty or potentially blocked. Block reason: {response.prompt_feedback.block_reason if response.prompt_feedback else 'N/A'}")
            safety_ratings_str = ", ".join([f"{rating.category}: {rating.probability}" for rating in response.prompt_feedback.safety_ratings]) if response.prompt_feedback else "N/A"
            print(f"Safety ratings: {safety_ratings_str}")
            return "Error or empty response from LLM. Check logs."

    except Exception as e:
        print(f"Error calling Gemini: {e}")
        return "Error during LLM call. Check logs."

if __name__ == "__main__":
    print("Testing call_llm with Gemini (ensure GOOGLE_API_KEY is set):")
    
    # Test 1: Simple question
    # print("\nTest 1: Simple Question")
    # question = "What is the capital of France?"
    # answer = call_llm(question)
    # print(f"Prompt: {question}")
    # print(f"Gemini_Response: {answer}")

    # Test 2: Topic extraction (example)
    print("\nTest 2: Topic Extraction")
    transcript_sample = "PocketFlow is a lightweight LLM framework. It focuses on simplicity and extensibility. Users can define nodes and connect them into flows to build complex AI applications."
    topics_prompt = f"Extract up to 3 key topics from the following text. List them separated by commas: {transcript_sample}"
    extracted_topics = call_llm(topics_prompt, system_message="You are an expert in identifying key topics from text.")
    print(f"Prompt for topics: {topics_prompt}")
    print(f"Gemini_Topics: {extracted_topics}")

    # Test 3: Question generation (example)
    print("\nTest 3: Question Generation")
    example_topic = "AI Ethics in Autonomous Vehicles"
    questions_prompt = f"Generate 2 insightful questions about the topic: '{example_topic}'. List them separated by semicolons."
    generated_questions = call_llm(questions_prompt, system_message="You are an expert at generating thought-provoking questions.")
    print(f"Prompt for questions: {questions_prompt}")
    print(f"Gemini_Questions: {generated_questions}")

    # Test 4: ELI5 explanation
    print("\nTest 4: ELI5 Explanation")
    eli5_prompt = "Explain black holes like I'm 5 years old."
    eli5_answer = call_llm(eli5_prompt, system_message="You explain complex topics to a 5-year-old child.")
    print(f"ELI5 Prompt: {eli5_prompt}")
    print(f"Gemini_ELI5_Response: {eli5_answer}")
