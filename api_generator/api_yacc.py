import ply.yacc as yacc
from api_lex import tokens, lexer

def p_start(p):
	'start : NAME SCOPE_BEGIN service SCOPE_END'
	p[0] = {
		'name': p[1],
		'apis': p[3],
	}


def p_service(p):
	r"""service : service api
	            | api"""
	if len(p) == 3:
		p[0] = p[1]
		p[0].append(p[2])
	else:
		p[0] = [p[1]]


def p_api(p):
	'api : NAME annotations'
	p[0] = p[2]
	p[0]['name'] = p[1]


def p_annotations(p):
	"""annotations : API_ANNOTATION api_summary
	               | api_summary"""
	if len(p) == 3:
		p[0] = p[2]
		p[0]['http_method'] = p[1][0].lower()
		p[0]['http_path'] = p[1][1]
	else:
		p[0] = p[1]


def p_api_summary(p):
	r"""api_summary : API_SUMMARY
	                |"""
	p[0] = {}
	if len(p) == 2:
		p[0]['summary'] = p[1]


def p_error(p):
	raise Exception("Syntax error in input: %s", p)


# Build the parser
parser = yacc.yacc()


def parse(s):
	result = parser.parse(s, lexer=lexer)
	return result
