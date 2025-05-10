from flow import create_youtube_eli5_flow
import json

# Example main function based on docs/design.md
def main():
    # Initialize shared data structure
    shared = {
        "video_info": {
            "url": "",            # YouTube URL to be provided by user
            "title": "",          # Video title - will be filled by ProcessYouTubeURLNode
            "transcript": "",     # Full transcript - will be filled by ProcessYouTubeURLNode
            "thumbnail_url": "",  # Thumbnail image URL - will be filled by ProcessYouTubeURLNode
            "video_id": ""        # YouTube video ID - will be filled by ProcessYouTubeURLNode
        },
        "topics": [
            # Example structure, will be filled by ExtractTopicsAndQuestionsNode & ProcessTopicNode
            # {
            #     "title": str,             
            #     "rephrased_title": str,   
            #     "questions": [
            #         {
            #             "original": str,      
            #             "rephrased": str,     
            #             "answer": str         
            #         },
            #     ]
            # },
        ],
        "html_output": ""  # Final HTML content - will be filled by GenerateHTMLNode
    }

    # Get YouTube URL from user input or set a default for testing
    youtube_url = input("Enter the YouTube video URL: ")
    if not youtube_url:
        # youtube_url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ" # Example placeholder
        youtube_url = "https://www.youtube.com/watch?v=AFY67zOpbSo" # Simpler for placeholder output
        print(f"No URL entered, using default: {youtube_url}")
    
    shared["video_info"]["url"] = youtube_url

    # The ProcessYouTubeURLNode needs the URL to be in shared["video_info"]["url"]
    # However, its `prep` method is not defined, so `exec` takes `prep_res` directly.
    # For ProcessYouTubeURLNode to work as defined (exec takes the URL),
    # the flow or the node itself needs to ensure `prep_res` is the URL.
    # Let's adjust how the first node gets its input for this placeholder version:
    # We can pass it via params or ensure its prep() method correctly fetches it.

    # For the placeholder `pocketflow.py`, the `ProcessYouTubeURLNode` will get its input
    # from `prep_res`. The first node in a flow typically needs a way to get initial data.
    # One way is for the flow's `run` to pass initial context or for the first node's `prep` to be special.
    # Or, we can set initial params on the first node or the flow.
    # For simplicity, let ProcessYouTubeURLNode.prep fetch from shared["video_info"]["url"]

    # Modify ProcessYouTubeURLNode.prep to fetch the URL
    # (This change should ideally be in nodes.py, but for now, we understand the flow)
    # nodes.ProcessYouTubeURLNode.prep = lambda self, shared_store: shared_store["video_info"]["url"]
    # This kind of dynamic patching is not ideal. Better to define it correctly in the Node itself.
    # Let's assume ProcessYouTubeURLNode.prep = lambda self, shared: shared["video_info"]["url"] is defined in nodes.py
    # For our current nodes.py, exec gets prep_res. The first node's prep will return None if not overridden.
    # The current placeholder Flow doesn't explicitly pass initial data to the first node's prep.
    # The ProcessYouTubeURLNode currently has no prep, so prep_res for its exec is None.
    # It should be: ProcessYouTubeURLNode.prep = lambda self, shared: shared["video_info"]["url"]
    # Let's make that change in nodes.py

    # Create the flow
    eli5_flow = create_youtube_eli5_flow()

    # Run the flow
    print("\nStarting ELI5 YouTube Flow...")
    eli5_flow.run(shared)
    print("ELI5 YouTube Flow finished.")

    # Output the results
    print("\n--- Final Shared Data ---")
    # print(json.dumps(shared, indent=4))
    print(f"Video Title: {shared.get('video_info',{}).get('title')}")
    print(f"Topics Extracted: {len(shared.get('topics',[]))}")
    for i, topic in enumerate(shared.get('topics',[])):
        print(f"  Topic {i+1}: {topic.get('rephrased_title')}")
        for j, q_a in enumerate(topic.get('questions',[])):
            print(f"    Q{j+1}: {q_a.get('rephrased')}")
            print(f"    A{j+1}: {q_a.get('answer')[:50]}...") # Print short answer

    html_file_name = "youtube_eli5_summary.html"
    if shared.get("html_output"):
        with open(html_file_name, "w", encoding="utf-8") as f:
            f.write(shared["html_output"])
        print(f"\nHTML report generated: {html_file_name}")
    else:
        print("\nHTML output was not generated.")

if __name__ == "__main__":
    main()
