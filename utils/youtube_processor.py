from youtube_transcript_api import YouTubeTranscriptApi
import requests
import re
import json

def extract_video_id(video_url: str) -> str:
    """从YouTube URL中提取视频ID"""
    # 尝试匹配标准YouTube URL
    match = re.search(r'(?:v=|\/)([0-9A-Za-z_-]{11}).*', video_url)
    if match:
        return match.group(1)
    # 尝试匹配短URL
    match = re.search(r'(?:youtu\.be\/)([0-9A-Za-z_-]{11})', video_url)
    if match:
        return match.group(1)
    # 如果URL格式不符合预期，尝试直接使用URL作为ID（如果是11个字符的ID）
    if re.match(r'^[0-9A-Za-z_-]{11}$', video_url):
        return video_url
    
    print(f"警告: 无法从URL提取视频ID: {video_url}")
    return "unknown_video_id"

def get_youtube_video_info(video_url: str) -> dict:
    """
    从YouTube URL获取视频信息，包括标题、缩略图URL、视频ID和字幕。
    使用youtube_transcript_api获取字幕，使用简单的元数据抓取获取标题和缩略图。
    """
    print(f"处理YouTube URL: {video_url}")
    
    video_id = extract_video_id(video_url)
    if video_id == "unknown_video_id":
        # 返回占位符数据
        return {
            "url": video_url,
            "title": "无法获取视频标题 (未知视频ID)",
            "transcript": "无法获取字幕。请检查YouTube URL是否有效。",
            "thumbnail_url": "",
            "video_id": "unknown_video_id"
        }
    
    # 创建结果字典
    result = {
        "url": video_url,
        "title": "",
        "transcript": "",
        "thumbnail_url": f"https://i.ytimg.com/vi/{video_id}/maxresdefault.jpg",
        "video_id": video_id
    }
    
    # 尝试获取字幕
    try:
        transcript_list = YouTubeTranscriptApi.get_transcript(video_id, languages=['zh-CN', 'zh', 'en'])
        # 将字幕转换为纯文本
        full_transcript = " ".join([entry["text"] for entry in transcript_list])
        result["transcript"] = full_transcript
        print(f"成功获取字幕，长度: {len(full_transcript)} 字符")
    except Exception as e:
        error_message = f"获取字幕时出错: {str(e)}"
        print(error_message)
        result["transcript"] = error_message
    
    # 尝试获取视频标题
    try:
        # 使用oEmbed API获取视频信息
        oembed_url = f"https://www.youtube.com/oembed?url=https://www.youtube.com/watch?v={video_id}&format=json"
        response = requests.get(oembed_url)
        if response.status_code == 200:
            oembed_data = response.json()
            result["title"] = oembed_data.get("title", "未知标题")
            print(f"成功获取视频标题: '{result['title']}'")
        else:
            print(f"获取视频元数据失败，HTTP状态码: {response.status_code}")
            result["title"] = f"未知视频标题 (ID: {video_id})"
    except Exception as e:
        print(f"获取视频标题时出错: {str(e)}")
        result["title"] = f"未知视频标题 (ID: {video_id})"
        
    return result

if __name__ == "__main__":
    # 测试代码
    test_url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"  # 著名的Rick Roll视频
    info = get_youtube_video_info(test_url)
    
    print("\nYouTube视频信息:")
    for key, value in info.items():
        if key == "transcript" and value:
            print(f"  {key.capitalize()}: {value[:100]}...")  # 只显示字幕的前100个字符
        else:
            print(f"  {key.capitalize()}: {value}") 