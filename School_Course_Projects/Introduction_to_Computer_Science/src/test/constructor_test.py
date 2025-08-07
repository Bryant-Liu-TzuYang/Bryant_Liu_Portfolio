file_path = input()
a = open(file_path, "r", encoding="utf-8")

for lines in a:
    print(lines, sep="", end="")

print("")
