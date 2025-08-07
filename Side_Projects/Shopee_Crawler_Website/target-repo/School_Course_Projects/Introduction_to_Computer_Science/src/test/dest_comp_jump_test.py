a = "dest = comp;jump"
b = a.split("=")
dest = b[0].strip()
c = b[1].split(";")
comp = c[0].strip()
jump = c[1].strip()
print(b)
print(c)
print(dest, comp, jump)
