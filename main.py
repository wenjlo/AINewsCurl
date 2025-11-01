from module.source import ETToday


if __name__ == "__main__":
    news = ETToday()
    news.output(scroll_count=3)
    print("執行完成!")
