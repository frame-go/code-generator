import jinja2
from dm_yacc import parse

sql_type_mapping = {
	'INT8': 'TINYINT',
	'UINT8': 'TINYINT UNSIGNED',
	'INT16': 'SMALLINT',
	'UINT16': 'SMALLINT UNSIGNED',
	'INT32': 'INT ',
	'UINT32': 'INT UNSIGNED',
	'INT64': 'BIGINT',
	'UINT64': 'BIGINT UNSIGNED',
	'FLOAT': 'FLOAT',
	'DOUBLE': 'DOUBLE',
	'DECIMAL': 'DECIMAL',
	'CHAR': 'CHAR',
	'VARCHAR': 'VARCHAR',
	'TEXT': 'TEXT',
	'LONGTEXT': 'LONGTEXT',
	'BINARY': 'BINARY',
	'VARBINARY': 'VARBINARY',
	'BLOB': 'BLOB',
	'LONGBLOB': 'LONGBLOB'
}

pb_type_mapping = {
	'INT8': 'int32',
	'UINT8': 'uint32',
	'INT16': 'int32',
	'UINT16': 'uint32',
	'INT32': 'int32',
	'UINT32': 'uint32',
	'INT64': 'int64',
	'UINT64': 'uint64',
	'FLOAT': 'float',
	'DOUBLE': 'double',
	'DECIMAL': 'string',
	'CHAR': 'string',
	'VARCHAR': 'string',
	'TEXT': 'string',
	'LONGTEXT': 'string',
	'BINARY': 'bytes',
	'VARBINARY': 'bytes',
	'BLOB': 'bytes',
	'LONGBLOB': 'bytes'
}

go_type_mapping = {
	'INT8': 'int8',
	'UINT8': 'uint8',
	'INT16': 'int16',
	'UINT16': 'uint16',
	'INT32': 'int32',
	'UINT32': 'uint32',
	'INT64': 'int64',
	'UINT64': 'uint64',
	'FLOAT': 'float32',
	'DOUBLE': 'float64',
	'DECIMAL': 'decimal.Decimal',
	'CHAR': 'string',
	'VARCHAR': 'string',
	'TEXT': 'string',
	'LONGTEXT': 'string',
	'BINARY': '[]byte',
	'VARBINARY': '[]byte',
	'BLOB': '[]byte',
	'LONGBLOB': '[]byte'
}

django_type_mapping = {
	'INT8': 'models.TinyIntegerField',
	'UINT8': 'models.PositiveTinyIntegerField',
	'INT16': 'models.SmallIntegerField',
	'UINT16': 'models.PositiveSmallIntegerField',
	'INT32': 'models.IntegerField',
	'UINT32': 'models.PositiveIntegerField',
	'INT64': 'models.BigIntegerField',
	'UINT64': 'models.PositiveBigIntegerField',
	'FLOAT': 'models.FloatField',
	'DOUBLE': 'models.FloatField',
	'DECIMAL': 'models.DecimalField',
	'CHAR': 'models.CharField',
	'VARCHAR': 'models.CharField',
	'TEXT': 'models.TextField',
	'LONGTEXT': 'models.TextField',
	'BINARY': 'models.BinaryField',
	'VARBINARY': 'models.BinaryField',
	'BLOB': 'models.BinaryField',
	'LONGBLOB': 'models.BinaryField'
}

django_auto_type_mapping = {
	'INT32': 'models.AutoField',
	'UINT32': 'models.PositiveAutoField',
	'INT64': 'models.BigAutoField',
	'UINT64': 'models.PositiveBigAutoField'
}

sql_create_code_template = r"""
{%- for table in tables: -%}
{% if table.new_db %}CREATE DATABASE IF NOT EXISTS `{{table.db.name}}`
	DEFAULT CHARACTER SET={{ table.db.attributes.charset or 'ascii' }}
	DEFAULT COLLATE={{ table.db.attributes.collate or 'ascii_general_ci' }};
	
USE `{{table.db.name}}`;

{% endif -%}
CREATE TABLE IF NOT EXISTS {% if table.db %}`{{ table.db.name }}`.{% endif %}`{{ table.name }}` (
{%- for column in table.columns %}
	`{{ column.name }}` {{ column.sql_type }}
	{%- if column.lengths %}({{ column.lengths | join(",") }}){% endif %}
	{%- if column.attributes.charset %} CHARACTER SET {{ column.attributes.charset }}{% endif %}
	{%- if column.attributes.collate %} COLLATE {{ column.attributes.collate }}{% endif %}
	{%- if column.attributes.null %} NULL{% else %} NOT NULL{% endif %}
	{%- if column.attributes.auto %} AUTO_INCREMENT{% endif %}
	{%- if column.attributes.default %} DEFAULT {{ column.attributes.default }}{% endif %},
{%- endfor %}
{%- for index in table.indexes %}
	{{ index.type }} {% if index.name %}{{ index.name }} {% endif -%}
	(`{{ index.fields | join("`, `") }}`){{ "," if not loop.last }}
{%- endfor %}
)
	ENGINE=InnoDB
	DEFAULT CHARACTER SET={{ table.attributes.charset or 'ascii' }}
	DEFAULT COLLATE={{ table.attributes.collate or 'ascii_general_ci' }};

{% endfor %}
"""

protocol_buffer_template = r"""
{%- for table in tables: -%}
message {{ table.upper_camel_name_short }} 
{
{%- for column in table.columns %}
	{{ column.pb_type }} {{ column.name }} = {{ loop.index }};
{%- endfor %}
}

{% endfor %}
"""

go_model_template = r"""
{%- for table in tables: -%}
type {{ table.upper_camel_name_short }} struct {
{%- for column in table.columns %}
	{{ column.upper_camel_name }} {{ column.go_type }} `gorm:"
{%- if column.primary_key %}primaryKey;
{%- if not column.attributes.auto %}autoIncrement=false;{% endif %}
{%- else %}
{%- if column.attributes.auto %}autoIncrement=true;{% endif %}
{%- endif -%}
column:{{ column.name }}" json:"{{ column.name }}"`
{%- endfor %}
}

func (*{{ table.upper_camel_name_short }}) TableName() string {
	return "{{ table.name }}"
}

{% endfor %}
"""

go_crud_template = r"""
{%- for table in tables: -%}
func (m *Manager) Create{{ table.upper_camel_name_short }}(ctx context.Context, {{ table.camel_name_short }} *models.{{ table.upper_camel_name_short }}) error {
	result := m.{{ table.db.camel_name_short }}DB.WithContext(ctx).Create({{ table.camel_name_short }})
	if result.Error != nil {
		return result.Error
	}
	return nil
}

{% for index in table.indexes -%}
func (m *Manager) Get{{ table.upper_camel_name_short }}{{ 's' if index.type == 'INDEX' }}{% if index.type != 'PRIMARY KEY' %}By{{ index.upper_camel_name_short }}{% endif -%}
(ctx context.Context, {% for column in index.columns %}{{ column.camel_name }} {{ column.go_type }}{{ ", " if not loop.last }}{% endfor -%}
) ({% if index.type == 'INDEX' %}[] {% endif %}*models.{{ table.upper_camel_name_short }}, error) {
{%- if index.type == 'INDEX' %}
	var {{ table.camel_name_short }}s []*models.{{ table.upper_camel_name_short }}
{%- else %}
	{{ table.camel_name_short }} := &models.{{ table.upper_camel_name_short }}{}
{%- endif %}
	result := m.{{ table.db.camel_name_short }}DB.WithContext(ctx)
{%- if index.type == 'PRIMARY KEY' -%}
.First({{ table.camel_name_short }}, {{ index.columns.0.camel_name }})
{%- else -%}
{%for column in index.columns %}.Where("{{ column.name }} = ?", {{ column.camel_name }}){% endfor %}
{%- if index.type == 'INDEX' -%}
.Find(&{{ table.camel_name_short }}s)
{%- else -%}
.First({{ table.camel_name_short }})
{%- endif %}
{%- endif %}
	if result.Error != nil {
		return nil, result.Error
	}
	return {{ table.camel_name_short }}{{ 's' if index.type == 'INDEX' }}, nil
}

{% endfor -%}
func (m *Manager) Update{{ table.upper_camel_name_short }}(ctx context.Context, {{ table.camel_name_short }} *models.{{ table.upper_camel_name_short }}) error {
	result := m.{{ table.db.camel_name_short }}DB.WithContext(ctx).Save({{ table.camel_name_short }})
	if result.Error != nil {
		return result.Error
	}
	return nil
}

{% for index in table.indexes -%}
func (m *Manager) Delete{{ table.upper_camel_name_short }}{{ 's' if index.type == 'INDEX' }}{% if index.type != 'PRIMARY KEY' %}By{{ index.upper_camel_name_short }}{% endif -%}
(ctx context.Context, {% for column in index.columns %}{{ column.camel_name }} {{ column.go_type }}{{ ", " if not loop.last }}{% endfor -%}
) error {
	result := m.{{ table.db.camel_name_short }}DB.WithContext(ctx)
{%- if index.type == 'PRIMARY KEY' -%}
.Delete(&models.{{ table.upper_camel_name_short }}{}, {{ index.columns.0.camel_name }})
{%- else -%}
{%for column in index.columns %}.Where("{{ column.name }} = ?", {{ column.camel_name }}){% endfor -%}
.Delete(&models.{{ table.upper_camel_name_short }}{})
{%- endif %}
	if result.Error != nil {
		return result.Error
	}
	return nil
}

{% endfor -%}
{% endfor %}
"""

django_model_template = r"""
{%- for table in tables: -%}
class {{ table.upper_camel_name }}(models.Model):
{%- for column in table.columns %}
	{{ column.name }} = {{ column.django_type }}({{ column.django_attributes | join(", ") }})
{%- endfor %}

	class Meta:
		managed = False
		db = '{{ table.db.name }}'
		db_table = '{{ table.name }}'

{% endfor %}
"""


def to_upper_camel_case(s):
	return "".join([i[0].upper() + i[1:].lower() for i in s.split("_")])


def to_camel_case(s):
	s = to_upper_camel_case(s)
	return s[0].lower() + s[1:]


class DataModelCompiler:

	def __init__(self, s):
		tables = parse(s)
		self.data = {'tables': tables}
		self._normalize_data()

	def _normalize_data(self):
		last_db = ''
		for table in self.data['tables']:
			if 'db' in table:
				db = table['db']
				db_name = db['name']
				if db_name != last_db:
					table['new_db'] = True
					last_db = db_name
				if 'attributes' not in db:
					db['attributes'] = {}
				self._normalize_attributes(db['attributes'])
				db['camel_name'] = to_camel_case(db_name)
				db['upper_camel_name'] = to_upper_camel_case(db_name)
				if db_name.endswith('_db'):
					db_name = db_name[:-3]
				if db['attributes'].get('prefix'):
					db_name = db_name[db_name.find('_') + 1:]
				db['camel_name_short'] = to_camel_case(db_name)
				db['upper_camel_name_short'] = to_upper_camel_case(db_name)
			if 'attributes' not in table:
				table['attributes'] = {}
			table_name = table['name']
			table['camel_name'] = to_camel_case(table_name)
			table['upper_camel_name'] = to_upper_camel_case(table_name)
			if table_name.endswith('_tab'):
				table_name = table_name[:-4]
			table['camel_name_short'] = to_camel_case(table_name)
			table['upper_camel_name_short'] = to_upper_camel_case(table_name)
			self._normalize_attributes(table['attributes'])
			for index in table['indexes']:
				if 'name' in index:
					index_name = index['name']
					index['camel_name'] = to_camel_case(index_name)
					index['upper_camel_name'] = to_upper_camel_case(index_name)
					if index_name.startswith('idx_'):
						index_name = index_name[4:]
					elif index_name.startswith('uidx_'):
						index_name = index_name[5:]
					index['camel_name_short'] = to_camel_case(index_name)
					index['upper_camel_name_short'] = to_upper_camel_case(index_name)
				index_columns = []
				for field in index['fields']:
					for column in table['columns']:
						if field == column['name']:
							if index['type'] == 'PRIMARY KEY':
								column['primary_key'] = True
							index_columns.append(column)
							break
				index['columns'] = index_columns
			for column in table['columns']:
				column['camel_name'] = to_camel_case(column['name'])
				column['upper_camel_name'] = to_upper_camel_case(column['name'])
				column['sql_type'] = sql_type_mapping[column['type']]
				column['pb_type'] = pb_type_mapping[column['type']]
				column['go_type'] = go_type_mapping[column['type']]
				column['django_type'] = django_type_mapping[column['type']]
				if 'attributes' not in column:
					column['attributes'] = {}
				self._normalize_attributes(column['attributes'])
				self._generate_django_column_attributes(column)

	@staticmethod
	def _normalize_attributes(attributes):
		if 'charset' in attributes:
			charset = attributes['charset']
			if 'collate' not in attributes:
				if charset.startswith('utf'):
					collate = charset + '_unicode_ci'
				else:
					collate = charset + '_general_ci'
				attributes['collate'] = collate
		elif 'collate' in attributes:
			collate = attributes['collate']
			if 'charset' not in attributes:
				attributes['charset'] = collate[0:collate.find('_')]

	@staticmethod
	def _generate_django_column_attributes(column):
		attributes = []
		if column.get('primary_key'):
			attributes.append('primary_key=True')
		if 'lengths' in column:
			lengths = column['lengths']
			if column['type'] == 'DECIMAL':
				attributes.append('max_digits=%d' % lengths[0])
				attributes.append('decimal_places=%d' % lengths[1])
			else:
				attributes.append('max_length=%d' % lengths[0])
		column_attributes = column['attributes']
		if column_attributes.get('null'):
			attributes.append('null=True')
		if column_attributes.get('default'):
			attributes.append('default=' + column_attributes['default'])
		if column_attributes.get('auto'):
			column['django_type'] = django_auto_type_mapping[column['type']]
		column['django_attributes'] = attributes

	def generate_sql_create_code(self):
		t = jinja2.Template(sql_create_code_template)
		return t.render(self.data)

	def generate_protocol_buffer(self):
		t = jinja2.Template(protocol_buffer_template)
		return t.render(self.data)

	def generate_gorm_model(self):
		t = jinja2.Template(go_model_template)
		return t.render(self.data)

	def generate_gorm_crud(self):
		t = jinja2.Template(go_crud_template)
		return t.render(self.data)

	def generate_django_model(self):
		t = jinja2.Template(django_model_template)
		return t.render(self.data)


def main():
	print("Enter/Paste your content. Ctrl-D or Ctrl-Z ( windows ) to save it.")
	lines = []
	while True:
		try:
			line = input()
		except EOFError:
			break
		lines.append(line)
	s = '\n'.join(lines)
	c = DataModelCompiler(s)
	print("[SQL Create Code]")
	print()
	print(c.generate_sql_create_code())
	print("[Protocol Buffers]")
	print()
	print(c.generate_protocol_buffer())
	print("[GORM Model]")
	print()
	print(c.generate_gorm_model())
	print("[GORM CRUD]")
	print()
	print(c.generate_gorm_crud())
	print("[Django Model]")
	print()
	print(c.generate_django_model())


if __name__ == "__main__":
	main()
