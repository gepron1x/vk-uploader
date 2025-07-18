from rules import list_startswith

url1 = "dash.youtube.com"

url2 = "youtube.com"

print(list_startswith(url2.split(".")[::-1], url1.split(".")[::-1]))