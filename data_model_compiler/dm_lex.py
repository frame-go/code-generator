import ply.lex as lex

tokens = [
	'NEWLINE',
	'AT',
	'EQUAL',
	'COMMA',
	'R_BRACKET_BEGIN',
	'R_BRACKET_END',
	'S_BRACKET_BEGIN',
	'S_BRACKET_END',
	'DATA_TYPE',
	'INDEX_TYPE',
	'IDENTIFIER',
	'STRING',
]

t_ignore = ' \t'
t_ignore_COMMENT = r'//.+'

t_NEWLINE = r'\n'
t_AT = r'@'
t_EQUAL = r'='
t_COMMA = r','
t_R_BRACKET_BEGIN = r'\('
t_R_BRACKET_END = r'\)'
t_S_BRACKET_BEGIN = r'\['
t_S_BRACKET_END = r'\]'
t_DATA_TYPE = r'(?i)(?!CHARSET)INT8|UINT8|INT16|UINT16|INT32|UINT32|INT64|UINT64|FLOAT|DOUBLE|DECIMAL|CHAR|VARCHAR|TEXT|LONGTEXT|BINARY|VARBINARY|BLOB|LONGBLOB(?=\b)'
t_INDEX_TYPE = r'(?i)PRIMARY|INDEX|UNIQUE|KEY(?=\b)'
t_IDENTIFIER = r'(?i)(?!INT8\b|UINT8\b|INT16\b|UINT16\b|INT32\b|UINT32\b|INT64\b|UINT64\b|FLOAT\b|DOUBLE\b|DECIMAL\b|CHAR\b|VARCHAR\b|TEXT\b|LONGTEXT\b|BINARY\b|VARBINARY\b|BLOB\b|LONGBLOB\b|PRIMARY\b|INDEX\b|UNIQUE\b|KEY\b)[\w.-]+'
t_STRING = r'"[^"]*"'


def t_error(t):
	raise Exception("Illegal character in input: %s", t.value[0])


lexer = lex.lex()
