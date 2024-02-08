import requests
from lxml import etree
from tqdm import tqdm
from concurrent.futures import ThreadPoolExecutor
import ffmpeg


def check_link(url):
    try:
        (
            ffmpeg.input(url)
            .output("pipe:", format="null", t=0.1)
            .run(capture_stdout=True, capture_stderr=True)
        )
        return True
    except ffmpeg.Error:
        # 打印错误信息，便于调试
        # print("FFmpeg error:", e.stderr.decode())
        # if "404 Not Found" in e.stderr.decode():
        #     print("Stream not found:", url)
        return False


def get_url(tv):
    url = "http://tonkiang.us/"
    data = {"search": tv}
    r = requests.post(url, data=data)
    html = r.text
    tree = etree.HTML(html)
    m3u8_links = tree.xpath('.//div[@class="m3u8"]/table/td[2]/text()')

    for link in m3u8_links:
        if check_link(link.strip()):
            return f'#EXTINF:-1 tvg-id="{tv}" ,{tv}\n{link}\n'
    return None


def gen_table():
    with open("tv.txt", "r", encoding="utf-8") as f:
        tv_lists = [line.strip() for line in f.readlines()]

    lines_to_write = []

    with ThreadPoolExecutor(max_workers=10) as executor:
        results = list(
            tqdm(
                executor.map(get_url, tv_lists),
                total=len(tv_lists),
                desc="Processing URLs",
            )
        )

    lines_to_write = [result for result in results if result]

    with open("tv.m3u8", "w+", encoding="utf-8") as f:
        f.writelines(lines_to_write)


def main():
    # TODO
    # check argument , if has -v 4 ,only accept ipv4 ,leave ipv6 default
    gen_table()


if __name__ == "__main__":
    main()
