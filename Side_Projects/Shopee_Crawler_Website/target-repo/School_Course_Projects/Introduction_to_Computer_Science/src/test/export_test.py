file_path = input()
file_name = file_path.split(".")[0]

new_file_name = file_name + ".hack"
f = open(new_file_name, "w")
f.write("hello" + "\n")
f.write("hi")
f.close
