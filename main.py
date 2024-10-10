import argparse
import json
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
import time

# 设置命令行参数
parser = argparse.ArgumentParser(description='小红书搜索脚本')
parser.add_argument('-q', '--query', type=str, help='搜索内容', required=True)
parser.add_argument('-n', '--number', type=int, help='获取笔记的数量', default=3)
parser.add_argument('-c', '--comments', type=int, help='查看的评论数量', default=5)
parser.add_argument('-r', '--replies', type=int, help='查看的回复数量', default=5)
args = parser.parse_args()

# 设置Chrome选项
chrome_options = Options()
chrome_options.add_argument("user-data-dir=./User_Data")  # 设置用户数据目录

# 初始化 WebDriver
driver = webdriver.Chrome(options=chrome_options)

try:
    # 打开小红书
    driver.get("https://www.xiaohongshu.com/explore")
    print("已打开小红书主页")
    
    # 等待用户扫码登录
    print("请扫码登录...")

    # 检测页面刷新
    while not driver.find_elements(By.XPATH, '//input[@placeholder="搜索小红书"]'):
        print("等待页面刷新...")
        time.sleep(1)
    print("页面已刷新，开始搜索")

    # 找到搜索框并输入搜索内容
    search_box = driver.find_element(By.XPATH, '//input[@placeholder="搜索小红书"]')
    print("找到搜索框")
    search_content = args.query  # 使用命令行参数传递的搜索内容
    search_box.send_keys(search_content)
    print(f"输入搜索内容: {search_content}")
    search_box.send_keys(Keys.RETURN)
    print("已提交搜索")

    # 等待搜索结果加载
    time.sleep(5)
    print("搜索结果加载完成")

    # 存储笔记信息的列表
    notes_data = []

    # 获取指定数量的笔记
    notes = driver.find_elements(By.XPATH, '//section[@class="note-item"]')[:args.number]
    print(f"找到 {len(notes)} 条笔记")
    print("-" * 20)
    for note in notes:
        # 点击打开笔记详情
        note.click()
        time.sleep(2)  # 等待详情页加载

        # 获取笔记详情
        title = note.find_element(By.XPATH, '//div[@class="note-content"]//div[@class="title"]').text
        author = note.find_element(By.XPATH, '//div[@class="author-container"]//span[@class="username"]').text
        content = note.find_element(By.XPATH, '//div[@class="note-content"]//div[@class="desc"]').text
        like_count = driver.find_element(By.CSS_SELECTOR, '#noteContainer > div.interaction-container > div.interactions.engage-bar > div > div > div.input-box > div.interact-container > div > div.left > span.like-wrapper.like-active > span.count').text
        
        # 实时打印笔记信息
        print("标题:", title)
        print("作者:", author)
        print("内容:", content)
        print("点赞数量:", like_count)

        # 存储当前笔记的信息
        note_info = {
            "title": title,
            "author": author,
            "content": content,
            "like_count": like_count,
            "comments": []
        }

        # 展开指定数量的评论
        try:
            expanded_comments = 0
            while expanded_comments < args.comments:
                load_more_buttons = driver.find_elements(By.XPATH, '//div[contains(text(), "展开")]')
                if not load_more_buttons:
                    break
                for button in load_more_buttons:
                    if expanded_comments >= args.comments:
                        break
                    button.click()
                    expanded_comments += 1
                    time.sleep(1)  # 等待加载更多回复
        except Exception as e:
            print("没有更多回复需要展开或找不到展开按钮:", e)

        # 获取指定数量的父评论
        parent_comments = driver.find_elements(By.XPATH, '//div[@class="parent-comment"]')[:args.comments]

        for parent_comment in parent_comments:
            try:
                # 获取父评论内容
                comment_text = parent_comment.find_element(By.XPATH, './/div[@class="comment-item"]//span[@class="note-text"]').text
                print('评论:', comment_text)  # 实时打印评论

                comment_info = {
                    "comment": comment_text,
                    "replies": []
                }

                # 获取该评论的指定数量的回复
                replies = parent_comment.find_elements(By.XPATH, './/div[@class="reply-container"]//span[@class="note-text"]')[:args.replies]
                for reply in replies:
                    reply_text = reply.text
                    print('回复:', reply_text)  # 实时打印回复
                    comment_info["replies"].append(reply_text)

                note_info["comments"].append(comment_info)
            except Exception as e:
                print('无法获取评论或回复:', e)

        # 将当前笔记的信息添加到列表中
        notes_data.append(note_info)
        print("-" * 20)

        driver.back()  # 返回搜索结果页
        time.sleep(2)  # 等待页面加载

finally:
    # 打印所有笔记的信息为JSON格式
    print(json.dumps(notes_data, ensure_ascii=False, indent=4))

    # 关闭浏览器
    print("-" * 20)
    print("关闭浏览器")
    driver.quit()
