import ply.lex as lex

tokens = [
	'NAME',
	'SCOPE_BEGIN',
	'SCOPE_END',
	'API_ANNOTATION',
	'API_SUMMARY',
]

t_ignore = ' \t'
t_ignore_COMMENT = r'//.+'

t_NAME = r'\w+'
t_SCOPE_BEGIN = r'{'
t_SCOPE_END = r'}'


def t_API_ANNOTATION(t):
	r'\[\S+(\s+\S+)\]'
	t.value = [s.strip() for s in t.value[1:-1].split()]
	return t


def t_API_SUMMARY(t):
	r':.*'
	t.value = t.value[1:].strip()
	return t


def t_newline(t):
	r'\n+'
	t.lexer.lineno += len(t.value)


def t_error(t):
	raise Exception("Illegal character in input: %s", t.value[0])


lexer = lex.lex()
