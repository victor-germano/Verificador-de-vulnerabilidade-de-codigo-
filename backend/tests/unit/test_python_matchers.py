from pathlib import Path

from app.scanner.parsers.python_parser import PythonParser
from app.scanner.rules import matchers as _matchers  # noqa: F401 - registers matchers
from app.scanner.rules.matcher_registry import get_matcher

_parser = PythonParser()


def _matches(rule_id: str, source: str) -> list:
    parsed = _parser.parse(Path("sample.py"), source)
    matcher = get_matcher(rule_id)
    assert matcher is not None
    return matcher(parsed)


def test_sql_injection_flags_concatenated_query() -> None:
    vulnerable = "query = 'SELECT * FROM users WHERE id = ' + user_id\ncursor.execute(query)\n"
    assert len(_matches("SQL001", vulnerable)) == 1


def test_sql_injection_ignores_parameterized_query() -> None:
    safe = "cursor.execute('SELECT * FROM users WHERE id = %s', (user_id,))\n"
    assert _matches("SQL001", safe) == []


def test_command_injection_flags_os_system_with_dynamic_arg() -> None:
    vulnerable = "os.system('ping ' + host)\n"
    assert len(_matches("CMD001", vulnerable)) == 1


def test_command_injection_ignores_list_args_without_shell() -> None:
    safe = "subprocess.run(['ping', '-c', '1', host])\n"
    assert _matches("CMD001", safe) == []


def test_command_injection_flags_shell_true_with_dynamic_string() -> None:
    vulnerable = "subprocess.run(f'ping {host}', shell=True)\n"
    assert len(_matches("CMD001", vulnerable)) == 1


def test_unsafe_eval_flags_dynamic_argument() -> None:
    vulnerable = "result = eval(user_input)\n"
    assert len(_matches("CODE001", vulnerable)) == 1


def test_unsafe_eval_ignores_literal_argument() -> None:
    safe = "result = eval('1 + 1')\n"
    assert _matches("CODE001", safe) == []


def test_path_traversal_flags_joined_path() -> None:
    vulnerable = "path = os.path.join(base_dir, filename)\nopen(path).read()\n"
    assert len(_matches("PATH001", vulnerable)) == 1


def test_path_traversal_ignores_literal_path() -> None:
    safe = "open('/etc/app/config.json').read()\n"
    assert _matches("PATH001", safe) == []


def test_ssrf_flags_dynamic_url() -> None:
    vulnerable = "resp = requests.get(url)\n"
    assert len(_matches("SSRF001", vulnerable)) == 1


def test_ssrf_ignores_literal_url() -> None:
    safe = "resp = requests.get('https://api.internal.example.com/health')\n"
    assert _matches("SSRF001", safe) == []


def test_insecure_deserialization_flags_pickle_loads() -> None:
    vulnerable = "data = pickle.loads(payload)\n"
    assert len(_matches("DESER001", vulnerable)) == 1


def test_insecure_deserialization_flags_yaml_load_without_safe_loader() -> None:
    vulnerable = "config = yaml.load(payload)\n"
    assert len(_matches("DESER001", vulnerable)) == 1


def test_insecure_deserialization_ignores_yaml_safe_load() -> None:
    safe = "config = yaml.safe_load(payload)\n"
    assert _matches("DESER001", safe) == []


def test_insecure_deserialization_ignores_yaml_load_with_safe_loader_kwarg() -> None:
    safe = "config = yaml.load(payload, Loader=yaml.SafeLoader)\n"
    assert _matches("DESER001", safe) == []


def test_xxe_flags_elementtree_parse() -> None:
    vulnerable = "tree = xml.etree.ElementTree.parse(untrusted_file)\n"
    assert len(_matches("XXE001", vulnerable)) == 1


def test_reflected_xss_flags_render_template_string_with_fstring() -> None:
    vulnerable = "return render_template_string(f'<h1>Hello {name}</h1>')\n"
    assert len(_matches("XSS001", vulnerable)) == 1


def test_reflected_xss_ignores_render_template() -> None:
    safe = "return render_template('greeting.html', name=name)\n"
    assert _matches("XSS001", safe) == []


def test_insecure_cookie_flags_missing_flags() -> None:
    vulnerable = "response.set_cookie('session_id', token)\n"
    assert len(_matches("COOKIE001", vulnerable)) == 1


def test_insecure_cookie_ignores_when_secure_and_httponly_set() -> None:
    safe = "response.set_cookie('session_id', token, secure=True, httponly=True)\n"
    assert _matches("COOKIE001", safe) == []


def test_open_redirect_flags_request_arg_target() -> None:
    vulnerable = "target = request.args.get('next')\nreturn redirect(request.args.get('next'))\n"
    assert len(_matches("REDIRECT001", vulnerable)) == 1


def test_open_redirect_ignores_literal_target() -> None:
    safe = "return redirect('/dashboard')\n"
    assert _matches("REDIRECT001", safe) == []


def test_weak_hash_flags_md5_and_sha1() -> None:
    vulnerable = "hashlib.md5(data).hexdigest()\nhashlib.sha1(data).hexdigest()\n"
    assert len(_matches("CRYPTO001", vulnerable)) == 2


def test_weak_hash_ignores_sha256() -> None:
    safe = "hashlib.sha256(data).hexdigest()\n"
    assert _matches("CRYPTO001", safe) == []


def test_weak_random_flags_sensitive_variable_name() -> None:
    vulnerable = "reset_token = random.randint(100000, 999999)\n"
    assert len(_matches("RANDOM001", vulnerable)) == 1


def test_weak_random_ignores_non_sensitive_variable_name() -> None:
    safe = "dice_roll = random.randint(1, 6)\n"
    assert _matches("RANDOM001", safe) == []


def test_nosql_injection_flags_dynamic_where_operator() -> None:
    vulnerable = 'collection.find({"$where": f"this.name == \'{name}\'"})\n'
    assert len(_matches("NOSQL001", vulnerable)) == 1


def test_nosql_injection_ignores_native_query_operators() -> None:
    safe = 'collection.find({"name": name})\n'
    assert _matches("NOSQL001", safe) == []


def test_ssti_flags_template_constructed_from_dynamic_string() -> None:
    vulnerable = "template = Template(user_input)\n"
    assert len(_matches("SSTI001", vulnerable)) == 1


def test_ssti_ignores_get_template_from_file() -> None:
    safe = "template = env.get_template('greeting.html')\n"
    assert _matches("SSTI001", safe) == []


def test_ldap_injection_flags_concatenated_filter() -> None:
    vulnerable = "conn.search(base_dn, f'(uid={username})', attributes=['cn'])\n"
    assert len(_matches("LDAP001", vulnerable)) == 1


def test_ldap_injection_ignores_literal_filter() -> None:
    safe = "conn.search(base_dn, '(objectClass=person)', attributes=['cn'])\n"
    assert _matches("LDAP001", safe) == []


def test_xpath_injection_flags_concatenated_expression() -> None:
    vulnerable = "nodes = tree.xpath(f\"//user[name='{username}']\")\n"
    assert len(_matches("XPATH001", vulnerable)) == 1


def test_xpath_injection_ignores_literal_expression() -> None:
    safe = "nodes = tree.xpath('//user')\n"
    assert _matches("XPATH001", safe) == []


def test_unsafe_file_upload_flags_raw_filename() -> None:
    vulnerable = "file.save(os.path.join(UPLOAD_DIR, file.filename))\n"
    assert len(_matches("UPLOAD001", vulnerable)) == 1


def test_unsafe_file_upload_ignores_secure_filename() -> None:
    safe = "file.save(os.path.join(UPLOAD_DIR, secure_filename(file.filename)))\n"
    assert _matches("UPLOAD001", safe) == []


def test_resource_leak_flags_open_without_with() -> None:
    vulnerable = "f = open(path)\ndata = f.read()\nf.close()\n"
    assert len(_matches("RESOURCE001", vulnerable)) == 1


def test_resource_leak_ignores_open_inside_with() -> None:
    safe = "with open(path) as f:\n    data = f.read()\n"
    assert _matches("RESOURCE001", safe) == []


def test_insecure_tempfile_flags_mktemp() -> None:
    vulnerable = "path = tempfile.mktemp()\n"
    assert len(_matches("TEMPFILE001", vulnerable)) == 1


def test_insecure_tempfile_ignores_named_temporary_file() -> None:
    safe = "f = tempfile.NamedTemporaryFile(delete=False)\n"
    assert _matches("TEMPFILE001", safe) == []


def test_unsafe_reflection_flags_dynamic_getattr_call() -> None:
    vulnerable = "action = request.args.get('action')\ngetattr(handler, action)()\n"
    assert len(_matches("REFLECT001", vulnerable)) == 1


def test_unsafe_reflection_ignores_constant_attribute_name() -> None:
    safe = "getattr(handler, 'list')()\n"
    assert _matches("REFLECT001", safe) == []


def test_unsafe_dynamic_import_flags_non_constant_module_name() -> None:
    vulnerable = "module = importlib.import_module(plugin_name)\n"
    assert len(_matches("FILEINC001", vulnerable)) == 1


def test_unsafe_dynamic_import_ignores_constant_module_name() -> None:
    safe = "module = importlib.import_module('plugins.pdf')\n"
    assert _matches("FILEINC001", safe) == []


def test_matchers_return_empty_list_on_syntax_error() -> None:
    broken = _parser.parse(Path("broken.py"), "def foo(:\n")
    for rule_id in ("SQL001", "CMD001", "CODE001"):
        matcher = get_matcher(rule_id)
        assert matcher is not None
        assert matcher(broken) == []
