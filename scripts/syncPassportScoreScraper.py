from urllib.request import urlopen

url = "https://www.syncpassport.com/MyScores"

page = urlopen(url)
html_bytes = page.read()
html = html_bytes.decode("utf_8")
print(html)