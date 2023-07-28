from flask import Flask, request
from ..data_model_compiler import compiler
from ..api_generator import generator

app = Flask(__name__)


@app.route('/')
def index():
	return app.send_static_file('index.html')


@app.route('/compile_data_model', methods=['POST'])
def compile_data_model():
	result = {}
	try:
		code = request.json['code']
		c = compiler.DataModelCompiler(code)
		result['sql'] = c.generate_sql_create_code()
		result['protobuf'] = c.generate_protocol_buffer()
		result['gorm'] = c.generate_gorm_model()
		result['gocrud'] = c.generate_gorm_crud()
		result['django'] = c.generate_django_model()
	except Exception as ex:
		result['error'] = str(ex)
	return result


@app.route('/generate_api', methods=['POST'])
def generate_api():
	result = {}
	try:
		code = request.json['code']
		g = generator.APIGenerator(code)
		result['protobuf'] = g.generate_protobuf()
		result['gorpc'] = g.generate_golang_grpc()
	except Exception as ex:
		result['error'] = str(ex)
	return result
