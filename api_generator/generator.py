import jinja2
from api_yacc import parse

protobuf_template = r"""service {{ name }} {

{% for api in apis: %}  rpc {{ api.name }} ({{ api.name }}Request) returns ({{ api.name }}Response) {{ "{" }}{% if api.http_path %}
    option (google.api.http) = {
      {{ api.http_method }}: "{{ api.http_path }}"{% if api.http_method == "post" %}
      body: "*"{% endif %}
    };{% endif %}{% if api.summary %}
    option (grpc.gateway.protoc_gen_openapiv2.options.openapiv2_operation) = {
      summary: "{{ api.summary }}"
    };{% endif %}
  }

{% endfor %}}
{% for api in apis: %}
message {{api.name}}Request {
}

message {{api.name}}Response {
}
{% endfor %}
"""

golang_grpc_template = r"""{% for api in apis: %}{% if loop.index != 1 %}
{% endif %}func (s *server) {{ api.name }}(ctx context.Context, req *{{ name_flat }}.{{ api.name }}Request) (*{{ name_flat }}.{{ api.name }}Response, error) {
	result, err := s.service.{{ api.name }}(ctx, req.TODO())
	if err != nil {
		errors.LogError(log.FromContext(ctx).Warn(), err).Msg("{{ api.name_snake }}_error")
		return nil, err
	}
	resp := &{{ name_flat }}.{{ api.name }}Response{
		TODO: result,
	}
	log.FromContext(ctx).Info().Msg("{{ api.name_snake }}")
	return resp, nil
}
{% endfor %}
"""


def camel_to_snake_case(s):
	result = []
	for ch in s:
		if ch >= 'A' and ch <= 'Z':
			if result:
				result.append('_')
			result.append(ch.lower())
		else:
			result.append(ch)
	return ''.join(result)


class APIGenerator:

	def __init__(self, s):
		data = parse(s)
		data['name_snake'] = camel_to_snake_case(data['name'])
		data['name_flat'] = data['name'].lower()
		for api in data['apis']:
			api['name_snake'] = camel_to_snake_case(api['name'])
		self.data = data

	def generate_protobuf(self):
		t = jinja2.Template(protobuf_template)
		return t.render(self.data)

	def generate_golang_grpc(self):
		t = jinja2.Template(golang_grpc_template)
		return t.render(self.data)



def main():
	print("Enter/Paste your content. Ctrl-D or Ctrl-Z ( windows ) to save it.")
	contents = []
	while True:
		try:
			line = input()
		except EOFError:
			break
		contents.append(line)
	content = '\n'.join(contents)
	g = APIGenerator(content)
	print("[Protocol Buffers]")
	print()
	print(g.generate_protobuf())
	print("[Golang GRPC ]")
	print()
	print(g.generate_golang_grpc())


if __name__ == "__main__":
	main()
