import unittest
from html_generator import generate_html_report

class TestHTMLGenerator(unittest.TestCase):

    def test_empty_inputs(self):
        """Test with empty video_info and empty topics_data."""
        video_info = {}
        topics_data = []
        html_output = generate_html_report(video_info, topics_data)
        self.assertIsInstance(html_output, str)
        self.assertIn("<title>YouTube Video Summary - ELI5 Summary</title>", html_output)
        self.assertIn("<h1>YouTube Video Summary</h1>", html_output)
        self.assertIn("<p class=\"no-content\">No topics were extracted or processed for this video.</p>", html_output)
        self.assertNotIn('<img src=""', html_output) # Check that empty thumbnail doesn't create broken img

    def test_video_info_only(self):
        """Test with populated video_info but empty topics_data."""
        video_info = {
            "title": "Test Video Title",
            "url": "http://example.com/test_video",
            "thumbnail_url": "http://example.com/thumbnail.jpg"
        }
        topics_data = []
        html_output = generate_html_report(video_info, topics_data)
        self.assertIn("<title>Test Video Title - ELI5 Summary</title>", html_output)
        self.assertIn("<h1>Test Video Title</h1>", html_output)
        self.assertIn('<img src="http://example.com/thumbnail.jpg" alt="Video Thumbnail" class="thumbnail">', html_output)
        self.assertIn("<p class=\"no-content\">No topics were extracted or processed for this video.</p>", html_output)
        self.assertIn('<a href="http://example.com/test_video" target="_blank">YouTube Made Simple</a>', html_output)

    def test_basic_content(self):
        """Test with one topic and one question."""
        video_info = {"title": "Basic Test"}
        topics_data = [
            {
                "title": "Original Topic 1",
                "rephrased_title": "Rephrased Topic 1!",
                "questions": [
                    {
                        "original": "Original Q1?",
                        "rephrased": "Rephrased Q1 for kids?",
                        "answer": "<p><b>Answer 1</b> is simple.</p>"
                    }
                ]
            }
        ]
        html_output = generate_html_report(video_info, topics_data)
        self.assertIn("<h3>Rephrased Topic 1!</h3>", html_output)
        self.assertIn("<strong class=\"question-text\">Rephrased Q1 for kids?</strong>", html_output)
        self.assertIn("<div class=\"answer-text\">\n                            <p><b>Answer 1</b> is simple.</p>\n                        </div>", html_output)

    def test_multiple_topics_and_questions(self):
        """Test with multiple topics and questions."""
        video_info = {"title": "Multi Test"}
        topics_data = [
            {
                "title": "Topic A", "rephrased_title": "Topic A Rephrased",
                "questions": [
                    {"rephrased": "Q A1", "answer": "<p>Ans A1</p>"},
                    {"rephrased": "Q A2", "answer": "Ans A2 (no p tags)"}
                ]
            },
            {
                "title": "Topic B", # No rephrased title
                "questions": [
                    {"rephrased": "Q B1", "answer": "Ans B1"}
                ]
            }
        ]
        html_output = generate_html_report(video_info, topics_data)
        self.assertIn("<h3>Topic A Rephrased</h3>", html_output)
        self.assertIn("<strong class=\"question-text\">Q A1</strong>", html_output)
        self.assertIn("<div class=\"answer-text\">\n                            <p>Ans A1</p>\n                        </div>", html_output)
        self.assertIn("<strong class=\"question-text\">Q A2</strong>", html_output)
        self.assertIn("<div class=\"answer-text\">\n                            Ans A2 (no p tags)\n                        </div>", html_output)
        
        self.assertIn("<h3>Topic B</h3>", html_output) # Fallback to original title
        self.assertIn("<strong class=\"question-text\">Q B1</strong>", html_output)
        self.assertIn("<div class=\"answer-text\">\n                            Ans B1\n                        </div>", html_output)

    def test_missing_optional_video_info(self):
        """Test with video_info missing optional keys like thumbnail_url."""
        video_info = {
            "title": "Minimal Video Info",
            "url": "http://example.com/minimal_video"
            # thumbnail_url is missing
        }
        topics_data = []
        html_output = generate_html_report(video_info, topics_data)
        self.assertIn("<h1>Minimal Video Info</h1>", html_output)
        self.assertNotIn('<img src', html_output) # Ensure no broken img tag
        self.assertIn('<a href="http://example.com/minimal_video" target="_blank">YouTube Made Simple</a>', html_output)

    def test_missing_optional_topic_data(self):
        """Test with topics_data items missing optional keys."""
        video_info = {"title": "Missing Topic Data Test"}
        topics_data = [
            { # Topic 1: missing rephrased_title, question parts
                "title": "Original Topic Only",
                "questions": [
                    {
                        "original": "Original Q Only"
                        # missing rephrased, missing answer
                    }
                ]
            },
            { # Topic 2: has rephrased title, but question is missing answer
                "title": "Topic Two Original",
                "rephrased_title": "Topic Two Rephrased",
                "questions": [
                    {
                        "original": "Q2 Orig",
                        "rephrased": "Q2 Rephrased"
                        # missing answer
                    }
                ]
            },
            { # Topic 3: question missing rephrased
                "title": "Topic Three",
                "rephrased_title": "Topic Three Rephrased",
                "questions": [
                    {
                        "original": "Q3 Original",
                        "answer": "<p>Q3 Answer</p>"
                        # missing rephrased
                    }
                ]
            }
        ]
        html_output = generate_html_report(video_info, topics_data)

        # Check Topic 1
        self.assertIn("<h3>Original Topic Only</h3>", html_output) # Fallback for rephrased_title
        self.assertIn("<strong class=\"question-text\">Original Q Only</strong>", html_output) # Fallback for rephrased question
        self.assertIn("<p><i>Answer not available.</i></p>", html_output) # Fallback for answer

        # Check Topic 2
        self.assertIn("<h3>Topic Two Rephrased</h3>", html_output)
        self.assertIn("<strong class=\"question-text\">Q2 Rephrased</strong>", html_output)
        self.assertIn("<p><i>Answer not available.</i></p>", html_output) # Fallback for answer

        # Check Topic 3
        self.assertIn("<h3>Topic Three Rephrased</h3>", html_output)
        self.assertIn("<strong class=\"question-text\">Q3 Original</strong>", html_output) # Fallback for rephrased question
        self.assertIn("<div class=\"answer-text\">\n                            <p>Q3 Answer</p>\n                        </div>", html_output)

    def test_no_questions_for_topic(self):
        """Test a topic that has a title but no questions list or empty questions list."""
        video_info = {"title": "No Questions Test"}
        topics_data_no_q_key = [
            {"title": "Topic With No Questions Key", "rephrased_title": "Rephrased No Q Key"}
            # "questions" key is missing
        ]
        topics_data_empty_q_list = [
            {"title": "Topic With Empty Questions List", "rephrased_title": "Rephrased Empty Q List", "questions": []}
        ]

        html_output_no_key = generate_html_report(video_info, topics_data_no_q_key)
        self.assertIn("<h3>Rephrased No Q Key</h3>", html_output_no_key)
        self.assertIn("<p class=\"no-content\">No questions available for this topic.</p>", html_output_no_key)

        html_output_empty_list = generate_html_report(video_info, topics_data_empty_q_list)
        self.assertIn("<h3>Rephrased Empty Q List</h3>", html_output_empty_list)
        self.assertIn("<p class=\"no-content\">No questions available for this topic.</p>", html_output_empty_list)

    def test_default_topic_title_if_all_missing(self):
        """Test that a default topic title is used if both title and rephrased_title are missing."""
        video_info = {"title": "Default Topic Title Test"}
        topics_data = [
            {
                # Missing "title" and "rephrased_title"
                "questions": [{"rephrased": "A question", "answer": "An answer"}]
            }
        ]
        html_output = generate_html_report(video_info, topics_data)
        # Check for the default title "Unnamed Topic 1"
        self.assertIn("<h3>Unnamed Topic 1</h3>", html_output)
        self.assertIn("<strong class=\"question-text\">A question</strong>", html_output)

if __name__ == '__main__':
    unittest.main()