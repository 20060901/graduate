# from selenium import webdriver
# from selenium.webdriver.common.by import By
# from selenium.webdriver.support.ui import WebDriverWait
# from selenium.webdriver.support import expected_conditions as EC
#
# # 初始化浏览器驱动
# browser = webdriver.Edge()
#
# # 访问网页
# url = 'https://www.zhipin.com/web/geek/job?city=100010000&position=100109'
# browser.get(url)
#
# # 等待最多10秒，直到元素可见
# element = WebDriverWait(browser, 10).until(
#     EC.visibility_of_element_located((By.XPATH, '//*[@id="wrap"]/div[2]/div[2]/div/div[1]/div[2]'))
# )
# print(element.text)


