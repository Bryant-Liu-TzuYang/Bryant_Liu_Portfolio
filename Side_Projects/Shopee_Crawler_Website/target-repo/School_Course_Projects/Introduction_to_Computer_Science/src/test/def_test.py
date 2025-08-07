def remove_inline_comment(aline):
    aline = aline.split("#")[0]
    aline.strip()
    return aline


a = "this is a test"  # test
remove_inline_comment(a)
print(a)

print(a[-1:])

b = "(hello.2)"
b = b.strip("().2")
print(b)
