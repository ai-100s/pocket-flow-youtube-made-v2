def generate_html_report(video_info: dict, topics_data: list) -> str:
    """
    Placeholder for generating an HTML report from video info and processed topics data.
    """
    print("Generating HTML report (Placeholder)...")
    
    title = video_info.get("title", "YouTube Video Summary")
    thumbnail_url = video_info.get("thumbnail_url", "")

    html_content = f"""\
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title}</title>
    <style>
        body {{ font-family: sans-serif; margin: 20px; background-color: #f4f4f9; color: #333; }}
        .container {{ background-color: #fff; padding: 20px; border-radius: 8px; box-shadow: 0 0 10px rgba(0,0,0,0.1); }}
        h1 {{ color: #d9534f; }}
        h2 {{ color: #5cb85c; border-bottom: 2px solid #5cb85c; padding-bottom: 5px; }}
        h3 {{ color: #f0ad4e; }}
        .topic-block {{ margin-bottom: 20px; padding: 15px; border: 1px solid #ddd; border-radius: 5px; background-color: #f9f9f9; }}
        .question-block {{ margin-left: 20px; margin-bottom: 10px; padding: 10px; border: 1px solid #eee; border-radius: 4px; background-color: #fff; }}
        img.thumbnail {{ max-width: 320px; height: auto; border-radius: 5px; margin-bottom: 20px; }}
        p {{ line-height: 1.6; }}
    </style>
</head>
<body>
    <div class="container">
        <h1>{title}</h1>
        <img src="{thumbnail_url}" alt="Video Thumbnail" class="thumbnail">
        
        <h2>Summary - Explained Like I'm 5!</h2>
    """

    if not topics_data:
        html_content += "<p>No topics were extracted or processed.</p>"
    else:
        for topic in topics_data:
            rephrased_topic_title = topic.get("rephrased_title", topic.get("title", "Unnamed Topic"))
            html_content += f"""\
        <div class="topic-block">
            <h3>{rephrased_topic_title}</h3>
            """
            if not topic.get("questions"):
                html_content += "<p>No questions for this topic.</p>"
            else:
                for q_and_a in topic["questions"]:
                    rephrased_question = q_and_a.get("rephrased", q_and_a.get("original", "Question not available"))
                    eli5_answer = q_and_a.get("answer", "Answer not available")
                    html_content += f"""\
            <div class="question-block">
                <strong>Question:</strong> {rephrased_question}<br>
                <strong>Answer (ELI5):</strong> {eli5_answer}
            </div>
            """
            html_content += "</div>"
    
    html_content += """\
    </div>
</body>
</html>
    """
    return html_content

if __name__ == "__main__":
    # Dummy data for testing
    sample_video_info = {
        "title": "The Magic of Rainbows",
        "thumbnail_url": "https://via.placeholder.com/320x180.png?text=Rainbow+Video"
    }
    sample_topics_data = [
        {
            "title": "How Rainbows Form",
            "rephrased_title": "How Do Rainbows Magically Appear?",
            "questions": [
                {
                    "original": "What causes rainbows?",
                    "rephrased": "Why do we see colorful bows in the sky?",
                    "answer": "Rainbows are like magic pictures in the sky! When sunlight shines through tiny raindrops, the light bends and splits into pretty colors, like red, orange, yellow, green, blue, and purple. It's like the raindrops are tiny prisms making a colorful smile in the sky for us to see!"
                },
                {
                    "original": "Can you touch a rainbow?",
                    "rephrased": "Can I go and touch a rainbow?",
                    "answer": "That's a fun idea! But rainbows are like pictures made of light, so you can't really touch them. They look like they are in one place, but if you try to walk to them, they seem to move away. It's like trying to catch a sunbeam!"
                }
            ]
        },
        {
            "title": "Colors of the Rainbow",
            "rephrased_title": "What Are All The Pretty Colors in a Rainbow?",
            "questions": [
                {
                    "original": "What are the colors in a rainbow?",
                    "rephrased": "What colors make a rainbow so pretty?",
                    "answer": "Rainbows have seven main colors! You can remember them with a name like ROY G. BIV. That stands for Red, Orange, Yellow, Green, Blue, Indigo (which is like a dark blue-purple), and Violet (which is like purple). All these colors together make the rainbow super beautiful!"
                }
            ]
        }
    ]

    html_output = generate_html_report(sample_video_info, sample_topics_data)
    print("\nHTML Report (Placeholder - first 500 chars):")
    print(html_output[:500] + "...")

    # To save and view the full HTML:
    # with open("report_eli5.html", "w", encoding="utf-8") as f:
    #     f.write(html_output)
    # print("\nFull report saved to report_eli5.html") 