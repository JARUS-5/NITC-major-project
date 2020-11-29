d = {"s1":123,"s2":4231}
d["s3"] = 143
print(list(d))
print(eval(str(d)))
print(d.items())
for i in d:
    print(i)