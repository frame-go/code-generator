import ply.yacc as yacc
from dm_lex import tokens, lexer

start = 'dbs'


def p_dbs(p):
	"""dbs : table
	       | db newlines dbs
	       | table newlines dbs"""
	if len(p) == 2:
		p[0] = [p[1], ]
	else:
		p[0] = p[3]
		if p[1]['kind'] == 'DB':
			for table in p[3]:
				if 'db' not in table:
					table['db'] = p[1]
		else:
			p[0].insert(0, p[1])


def p_db(p):
	"""db : AT IDENTIFIER NEWLINE
	      | AT IDENTIFIER R_BRACKET_BEGIN attributes R_BRACKET_END NEWLINE"""
	p[0] = {'kind': 'DB', 'name': p[2]}
	if len(p) == 7:
		p[0]['attributes'] = p[4]


def p_table(p):
	"""table : IDENTIFIER NEWLINE columns
	         | IDENTIFIER R_BRACKET_BEGIN attributes R_BRACKET_END NEWLINE columns"""
	if len(p) == 4:
		p[0] = p[3]
	else:
		p[0] = p[6]
		p[0]['attributes'] = p[3]
	p[0]['kind'] = 'TABLE'
	p[0]['name'] = p[1]


def p_columns(p):
	"""columns : column NEWLINE
	           | column NEWLINE indexes
	           | column NEWLINE columns"""
	if len(p) == 3:
		p[0] = {
			'columns': [p[1], ],
			'indexes': [],
		}
	else:
		if isinstance(p[3], list):
			p[0] = {
				'columns': [p[1], ],
				'indexes': p[3],
			}
		else:
			p[0] = p[3]
			p[0]['columns'].insert(0, p[1])


def p_column(p):
	"""column : column_type IDENTIFIER
	      	  | column_type IDENTIFIER R_BRACKET_BEGIN attributes R_BRACKET_END"""
	p[0] = {
		'kind': 'COLUMN',
		'name': p[2],
	}
	p[0].update(p[1])
	if len(p) == 6:
		p[0]['attributes'] = p[4]


def p_attributes(p):
	"""attributes : attribute
	               | attribute COMMA attributes"""
	if len(p) == 2:
		p[0] = p[1]
	else:
		p[0] = p[3]
		p[0].update(p[1])


def p_attribute(p):
	"""attribute : IDENTIFIER
	             | IDENTIFIER EQUAL IDENTIFIER
	             | IDENTIFIER EQUAL STRING"""
	p[0] = {}
	if len(p) == 2:
		p[0][p[1].lower()] = True
	else:
		p[0][p[1].lower()] = p[3]


def p_column_type(p):
	"""column_type : DATA_TYPE
	               | DATA_TYPE S_BRACKET_BEGIN lengths S_BRACKET_END"""
	p[0] = {
		'type': p[1].upper()
	}
	if len(p) == 5:
		p[0]['lengths'] = p[3]


def p_lengths(p):
	"""lengths : IDENTIFIER
	           | IDENTIFIER COMMA lengths"""
	value = int(p[1])
	if len(p) == 2:
		p[0] = [value,]
	else:
		p[0] = p[3]
		p[0].insert(0, value)


def p_indexes(p):
	"""indexes : index NEWLINE
	           | index NEWLINE indexes"""
	if len(p) == 3:
		p[0] = [p[1],]
	else:
		p[0] = p[3]
		p[0].insert(0, p[1])


def p_index(p):
	"""index : index_type R_BRACKET_BEGIN fields R_BRACKET_END
	         | index_type IDENTIFIER R_BRACKET_BEGIN fields R_BRACKET_END"""
	p[0] = {
		'kind': 'INDEX',
		'type': p[1],
	}
	if len(p) == 5:
		p[0]['fields'] = p[3]
	else:
		p[0]['name'] = p[2]
		p[0]['fields'] = p[4]


def p_index_type(p):
	"""index_type : INDEX_TYPE
	              | INDEX_TYPE INDEX_TYPE"""
	p[0] = ' '.join(p[1:]).upper()


def p_fields(p):
	"""fields : IDENTIFIER
	          | IDENTIFIER COMMA fields"""
	if len(p) == 2:
		p[0] = [p[1],]
	else:
		p[0] = p[3]
		p[0].insert(0, p[1])


def p_newlines(p):
	"""newlines : NEWLINE
	            | NEWLINE newlines"""
	pass


def p_error(p):
	raise Exception("Syntax error in input: %s", p)


parser = yacc.yacc()


def normalize_text(s):
	s = s.strip()
	s += '\n'
	return s


def parse(s):
	s = normalize_text(s)
	return parser.parse(s, lexer=lexer)
