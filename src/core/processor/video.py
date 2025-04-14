import configparser
from pathlib import Path
from time import sleep
from xhs import XhsClient
from uploader.xhs_uploader.main import sign_local, beauty_print

def publish_single_video(video_path, title, tags):
    # 读取配置
    config = configparser.RawConfigParser()
    config.read(Path("uploader/xhs_uploader/accounts.ini"))

    # 获取 cookies
    cookies = config['account1']['cookies']
    xhs_client = XhsClient(cookies, sign=sign_local, timeout=60)

    # 验证 cookies
    try:
        xhs_client.get_video_first_frame_image_id("3214")
    except:
        print("cookie 失效")
        return

    # 处理标签
    tags_str = ' '.join(['#' + tag for tag in tags])
    hash_tags_str = ''
    hash_tags = []

    topics = []

    # 获取hashtag
    for i in tags[:3]:
        topic_official = xhs_client.get_suggest_topic(i)
        if topic_official:
            topic_official[0]['type'] = 'topic'
            topic_one = topic_official[0]
            hash_tag_name = topic_one['name']
            hash_tags.append(hash_tag_name)
            topics.append(topic_one)

    hash_tags_str = ' ' + ' '.join(['#' + tag + '[话题]#' for tag in hash_tags])

    # 发布视频
    note = xhs_client.create_video_note(
        title=title[:20],
        video_path=str(video_path),
        desc=title + tags_str + hash_tags_str,
        topics=topics,
        is_private=False
    )

    beauty_print(note)
    sleep(30)  # 避免风控
