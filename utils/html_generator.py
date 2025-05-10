def generate_html_report(video_info: dict, topics_data: list) -> str:
    """Generates an HTML report from video info and processed topics data with improved styling."""
    print("Generating HTML report with improved styling...")
    
    # Extract values and provide defaults
    video_title_val = video_info.get("title", "YouTube Video Summary")
    thumbnail_url_val = video_info.get("thumbnail_url", "")
    video_url_val = video_info.get("url", "#")

    # Pre-generate thumbnail HTML string using an f-string separately
    # This keeps f-string logic isolated from the main template's .format() method
    thumbnail_html_content = ""
    if thumbnail_url_val:
        thumbnail_html_content = f'<img src="{thumbnail_url_val}" alt="Video Thumbnail" class="thumbnail">'

    # --- Generate HTML for topics ---
    topics_html_parts = []
    if not topics_data:
        topics_html_parts.append("<p class=\"no-content\">No topics were extracted or processed for this video.</p>")
    else:
        for topic_idx, topic in enumerate(topics_data):
            rephrased_topic_title = topic.get("rephrased_title") or topic.get("title", f"Unnamed Topic {topic_idx + 1}")
            
            topic_content = f"""<section class="topic-block">
            <h3>{rephrased_topic_title}</h3>"""

            if not topic.get("questions"):
                topic_content += "<p class=\"no-content\">No questions available for this topic.</p>"
            else:
                for q_idx, q_and_a in enumerate(topic.get("questions", [])):
                    rephrased_question = q_and_a.get("rephrased") or q_and_a.get("original", f"Question {q_idx + 1} not available")
                    # The answer from LLM is expected to be HTML already
                    eli5_answer_html = q_and_a.get("answer", "<p><i>Answer not available.</i></p>")
                    
                    topic_content += f"""<article class="question-block">
                        <strong class="question-text">{rephrased_question}</strong>
                        <div class="answer-text">
                            {eli5_answer_html}
                        </div>
                    </article>"""
            topic_content += "</section>"
            topics_html_parts.append(topic_content)
    
    topics_final_html = "\n".join(topics_html_parts)

    # --- HTML Template (This is NOT an f-string) ---
    # All CSS curly braces are escaped with {{ and }} for the .format() method.
    # Dynamic parts use named placeholders like {v_title_placeholder}.
    html_template = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{v_title_placeholder} - ELI5 Summary</title>
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
            margin: 0;
            padding: 0;
            background-color: #f8f9fa;
            color: #212529;
            line-height: 1.6;
        }}
        .generated-by {{
            font-size: 0.8em;
            color: #6c757d;
            text-align: right;
            padding: 10px 20px;
            background-color: #e9ecef;
        }}
        .container {{
            max-width: 800px;
            margin: 20px auto;
            padding: 20px;
            background-color: #fff;
            border-radius: 8px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.075);
        }}
        .video-header h1 {{
            font-size: 2.2em;
            color: #343a40;
            margin-bottom: 10px;
            font-weight: 600;
        }}
        .video-header .thumbnail {{
            width: 100%;
            max-width: 480px; /* Control thumbnail size */
            height: auto;
            border-radius: 6px;
            margin-bottom: 25px;
            display: block;
            margin-left: auto;
            margin-right: auto;
        }}
        .section-title {{
            font-size: 1.8em;
            color: #007bff; /* Primary color for main section titles */
            margin-top: 30px;
            margin-bottom: 15px;
            padding-bottom: 10px;
            border-bottom: 2px solid #dee2e6;
            font-weight: 500;
        }}
        .topic-block {{
            margin-bottom: 30px;
            padding: 20px;
            background-color: #fdfdff; /* Slightly off-white for topics */
            border: 1px solid #e9ecef;
            border-radius: 6px;
        }}
        .topic-block h3 {{ /* Rephrased Topic Title */
            font-size: 1.5em;
            color: #28a745; /* Success/Green for topic titles */
            margin-top: 0;
            margin-bottom: 15px;
            font-weight: 500;
        }}
        .question-block {{
            margin-bottom: 15px;
            padding-left: 15px;
            border-left: 3px solid #17a2b8; /* Info/Blue accent for questions */
        }}
        .question-block strong.question-text {{ /* Rephrased Question */
            font-size: 1.15em;
            color: #343a40;
            display: block;
            margin-bottom: 8px;
            font-weight: 500;
        }}
        .answer-text {{ /* ELI5 Answer */
            font-size: 1em;
            color: #495057;
            padding-left: 10px; /* Indent answer slightly */
        }}
        .answer-text p, .answer-text ol, .answer-text ul {{
            margin-top: 5px; 
            margin-bottom: 10px;
        }}
        .answer-text b {{ color: #dc3545; }}
        .answer-text i {{ color: #666; }}
        .no-content {{
            text-align: center;
            color: #6c757d;
            font-style: italic;
            padding: 20px;
        }}
        a {{ color: #007bff; text-decoration: none; }}
        a:hover {{ text-decoration: underline; }}
    </style>
</head>
<body>
    <div class="generated-by">Generated by <a href="{v_url_placeholder}" target="_blank">YouTube Made Simple</a></div>
    <div class="container">
        <header class="video-header">
            <h1>{v_title_placeholder}</h1>
            {thumbnail_html_placeholder}
        </header>

        <h2 class="section-title">ELI5 Summary: Key Topics & Questions</h2>
        {topics_html_placeholder}
    </div>
</body>
</html>"""
    
    # Use .format() to insert the dynamic content into the template
    final_html = html_template.format(
        v_title_placeholder=video_title_val,
        v_url_placeholder=video_url_val,
        thumbnail_html_placeholder=thumbnail_html_content,
        topics_html_placeholder=topics_final_html
    )
    return final_html

if __name__ == "__main__":
    # Dummy data for testing the new HTML structure
    sample_video_info = {
        "title": "Adventures in the Land of Dinosaurs",
        "url": "http://example.com/youtube/dino_adventures", # Changed to a generic example URL
        "thumbnail_url": "https://i.ytimg.com/vi/AFY67zOpbSo/hqdefault.jpg"
    }
    sample_topics_data = [
        {
            "title": "Different Types of Dinosaurs",
            "rephrased_title": "Roar-some Dinosaurs: Big and Small!",
            "questions": [
                {
                    "original": "What were the main categories of dinosaurs?",
                    "rephrased": "Were all dinosaurs the same, or were there different kinds?",
                    "answer": "<p>Oh, no! Dinosaurs were super different, like how cats and dogs are different, but even MORE!</p>" \
                              "<ol>" \
                              "  <li><b>Big Stompers (Sauropods):</b> Imagine super-duper tall ones with long necks like <i>Brachiosaurus</i>, munching leaves from tall trees! They went <i>stomp, stomp, stomp</i>!</li>" \
                              "  <li><b>Scary Meat-Eaters (Theropods):</b> Then there were the <b>T-Rex</b> types with big teeth that ate other dinos! Grrrr! They were fast and sneaky.</li>" \
                              "  <li><b>Plant-Chewers with Armor (Thyreophora):</b> Some dinos, like <i>Stegosaurus</i> with cool plates on its back, mostly ate plants and had built-in shields!</li>" \
                              "</ol>" \
                              "<p>So many cool kinds! It was like a giant animal park, but millions of years ago!</p>"
                },
                {
                    "original": "How big could dinosaurs get?",
                    "rephrased": "Did dinosaurs get as big as giants?",
                    "answer": "<p>You bet! Some dinosaurs were HUGE, bigger than houses or even buses! </p>" \
                              "<ul>" \
                              "  <li>The <b>Argentinosaurus</b> was one of the biggest. If it stood up, it would be taller than many buildings! It was as long as three school buses put together!</li>" \
                              "  <li>But some dinos were tiny too, like the <b>Compsognathus</b>, which was only about the size of a chicken! Squawk!</li>" \
                              "</ul><p>So they came in all sizes, from super-big to super-small!</p>"
                }
            ]
        },
        {
            "title": "Dinosaur Extinction Event",
            "rephrased_title": "Where Did All the Dinosaurs Go? Poof!",
            "questions": [
                {
                    "original": "What caused the dinosaurs to go extinct?",
                    "rephrased": "Why aren't there any dinosaurs walking around today?",
                    "answer": "<p>That's a super big mystery that scientists talk about a lot! Most of them think a <b>giant space rock</b>, called an <i>asteroid</i>, crashed into Earth! </p>" \
                              "<ol>" \
                              "  <li><b>Big Boom!:</b> When it hit, it made a HUGE explosion, bigger than any boom we know!</li>" \
                              "  <li><b>Dark and Cold:</b> So much dust and yucky stuff went into the sky that it blocked the sun. It got super dark and cold, and plants couldn't grow.</li>" \
                              "  <li><b>No More Food:</b> The plant-eating dinos had no food, and then the meat-eating dinos had no food. So, sadly, most of them went *poof* and disappeared.</li>" \
                              "</ol>" \
                              "<p>But guess what? Some scientists think that birds today are actually tiny little dinosaurs that survived! Tweet tweet!</p>"
                }
            ]
        }
    ]

    html_output = generate_html_report(sample_video_info, sample_topics_data)
    
    # Save the output to a file for review
    file_name = "youtube_eli5_summary_styled_corrected.html"
    with open(file_name, "w", encoding="utf-8") as f:
        f.write(html_output)
    print(f"\nStyled report saved to {file_name}") 
    # For debugging, you can print a snippet or the whole thing:
    # print("\nHTML Report Snippet (Corrected Styling):")
    # print(html_output[:2000] + "...")