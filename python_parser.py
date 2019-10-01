# Python + HTML | By Bernard - Joao Lucas Bernardi
import traceback
from io import StringIO
import sys

def execute(code, _globals={}, _locals={}):
	fake_stdout = StringIO()
	__stdout = sys.stdout
	sys.stdout = fake_stdout
	try:
		#try if this is expressions
		ret = eval(code, _globals, _locals)
		result = fake_stdout.getvalue()
		sys.stdout = __stdout
		if ret:
			result += str(ret)
		return result
	except:
		try:
			exec(code, _globals, _locals)
		except:
			sys.stdout = __stdout			
			buf = StringIO()
			traceback.print_exc(file=buf)
			return buf.getvalue()
		else:
			sys.stdout = __stdout
			return fake_stdout.getvalue()

code = ""
def pythonfier(contents, vars={}):
	code = contents
	cookie = ""
	code_lines = contents.replace("\n", "\\n").split("<python>")[1:]
	for code_line in code_lines:
		cd = code_line.split("</python>")[0].replace("\t", "•")		
		cut_size = 0
		for char in list(cd):
			if char in ["n", " ", "\\", "•"]:
				cut_size += 1
			else:
				break
		cd = code_line.split("</python>")[0].replace("•", " ")[cut_size:].replace("\\n", "\n")
		code_exec = execute(cd, _globals=vars)
		check = code_exec.split("⌠")
		if len(check) == 2:
			cookie = check[1]
			code_exec = check[0]		
		code = code.replace("<python>"+(code_line.split("</python>")[0]+"</python>").replace("\\n", "\n").replace("•", "\t"), code_exec)
	return cookie, code.encode()

