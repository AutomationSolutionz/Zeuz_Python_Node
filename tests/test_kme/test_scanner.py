"""Tests for the Generic Scanner (Layer A)."""

import os
import tempfile
import textwrap

import pytest

from Framework.knowledge_map_engine.scanner.language_detect import detect_language
from Framework.knowledge_map_engine.scanner.file_classifier import classify_file
from Framework.knowledge_map_engine.scanner.symbol_extractor import extract_symbols
from Framework.knowledge_map_engine.scanner.generic_scanner import GenericScanner


class TestLanguageDetect:
    def test_python_extension(self):
        assert detect_language("src/main.py") == "python"
        assert detect_language("utils.pyi") == "python"

    def test_javascript_extension(self):
        assert detect_language("app.js") == "javascript"
        assert detect_language("component.jsx") == "javascript"

    def test_typescript_extension(self):
        assert detect_language("app.ts") == "typescript"
        assert detect_language("component.tsx") == "typescript"

    def test_go_extension(self):
        assert detect_language("main.go") == "go"

    def test_rust_extension(self):
        assert detect_language("lib.rs") == "rust"

    def test_java_extension(self):
        assert detect_language("App.java") == "java"

    def test_csharp_extension(self):
        assert detect_language("Program.cs") == "csharp"

    def test_ruby_extension(self):
        assert detect_language("app.rb") == "ruby"

    def test_special_filenames(self):
        assert detect_language("Makefile") == "makefile"
        assert detect_language("Dockerfile") == "dockerfile"
        assert detect_language("Gemfile") == "ruby"

    def test_shebang_python(self):
        assert detect_language("script", "#!/usr/bin/env python3") == "python"
        assert detect_language("script", "#!/usr/bin/python") == "python"

    def test_shebang_node(self):
        assert detect_language("script", "#!/usr/bin/env node") == "javascript"

    def test_shebang_bash(self):
        assert detect_language("script", "#!/bin/bash") == "shell"

    def test_unknown_extension(self):
        assert detect_language("file.xyz") == "unknown"

    def test_config_files(self):
        assert detect_language("data.json") == "json"
        assert detect_language("config.yaml") == "yaml"
        assert detect_language("settings.toml") == "toml"


class TestFileClassifier:
    def test_generated_files(self):
        assert classify_file("dist/bundle.js").is_generated is True
        assert classify_file("file.min.js").is_generated is True
        assert classify_file("proto_pb2.py").is_generated is True
        assert classify_file("package-lock.json").is_generated is True
        assert classify_file("node_modules/pkg/index.js").is_generated is True

    def test_test_files(self):
        assert classify_file("tests/test_main.py").is_test is True
        assert classify_file("test_utils.py").is_test is True
        assert classify_file("app.test.js").is_test is True
        assert classify_file("app.spec.ts").is_test is True
        assert classify_file("AppTest.java").is_test is True
        assert classify_file("conftest.py").is_test is True

    def test_config_files(self):
        assert classify_file("pyproject.toml").is_config is True
        assert classify_file("package.json").is_config is True
        assert classify_file(".eslintrc.json").is_config is True
        assert classify_file("Makefile").is_config is True
        assert classify_file(".github/workflows/ci.yml").is_config is True
        assert classify_file("docker-compose.yml").is_config is True

    def test_documentation(self):
        assert classify_file("README.md").is_documentation is True
        assert classify_file("docs/guide.rst").is_documentation is True
        assert classify_file("CHANGELOG.md").is_documentation is True

    def test_vendored(self):
        assert classify_file("vendor/lib/foo.go").is_vendored is True
        assert classify_file("third_party/lib.py").is_vendored is True
        assert classify_file("node_modules/react/index.js").is_vendored is True

    def test_binary(self):
        assert classify_file("logo.png").is_binary is True
        assert classify_file("app.exe").is_binary is True
        assert classify_file("font.woff2").is_binary is True

    def test_source_file(self):
        cls = classify_file("src/main.py")
        assert cls.is_generated is False
        assert cls.is_test is False
        assert cls.is_binary is False


class TestSymbolExtractor:
    def test_python_function(self):
        code = textwrap.dedent("""\
            def hello(name: str) -> str:
                \"\"\"Greet someone.\"\"\"
                return f"Hello, {name}"
        """)
        symbols = extract_symbols("hello.py", code, "python")
        assert len(symbols) == 1
        assert symbols[0].name == "hello"
        assert symbols[0].kind.value == "function"
        assert symbols[0].signature == "def hello(name: str) -> str"
        assert symbols[0].docstring == "Greet someone."

    def test_python_class_and_methods(self):
        code = textwrap.dedent("""\
            class MyClass:
                \"\"\"A sample class.\"\"\"
                def method_one(self):
                    pass

                async def method_two(self, x: int) -> bool:
                    pass
        """)
        symbols = extract_symbols("models.py", code, "python")
        classes = [s for s in symbols if s.kind.value == "class"]
        methods = [s for s in symbols if s.kind.value == "method"]
        assert len(classes) == 1
        assert classes[0].name == "MyClass"
        assert len(methods) == 2
        assert methods[0].parent == "MyClass"

    def test_javascript_function(self):
        code = textwrap.dedent("""\
            export function handleRequest(req, res) {
                return res.json({ok: true});
            }

            export async function fetchData() {
                return await fetch('/api');
            }
        """)
        symbols = extract_symbols("handler.js", code, "javascript")
        funcs = [s for s in symbols if s.kind.value == "function"]
        assert len(funcs) == 2
        names = {s.name for s in funcs}
        assert "handleRequest" in names
        assert "fetchData" in names

    def test_javascript_class(self):
        code = textwrap.dedent("""\
            export class UserService {
                constructor() {}
            }
        """)
        symbols = extract_symbols("service.ts", code, "typescript")
        classes = [s for s in symbols if s.kind.value == "class"]
        assert len(classes) == 1
        assert classes[0].name == "UserService"

    def test_go_symbols(self):
        code = textwrap.dedent("""\
            func main() {
            }

            func (s *Server) HandleRequest(w http.ResponseWriter, r *http.Request) {
            }

            type Server struct {
                port int
            }

            type Handler interface {
                Handle()
            }
        """)
        symbols = extract_symbols("main.go", code, "go")
        funcs = [s for s in symbols if s.kind.value == "function"]
        types = [s for s in symbols if s.kind.value in ("class", "type")]
        assert len(funcs) == 2
        assert len(types) == 2

    def test_rust_symbols(self):
        code = textwrap.dedent("""\
            pub fn process(data: &[u8]) -> Result<(), Error> {
                Ok(())
            }

            pub struct Config {
                name: String,
            }

            pub async fn handle_request() {
            }
        """)
        symbols = extract_symbols("lib.rs", code, "rust")
        funcs = [s for s in symbols if s.kind.value == "function"]
        structs = [s for s in symbols if s.kind.value == "class"]
        assert len(funcs) == 2
        assert len(structs) == 1
        assert structs[0].name == "Config"

    def test_unknown_language_fallback(self):
        code = textwrap.dedent("""\
            function doSomething(x) {
            }
            class Widget {
            }
        """)
        symbols = extract_symbols("file.unknown", code, "unknown_lang")
        # Should still extract something via generic fallback
        assert len(symbols) >= 1


class TestGenericScanner:
    def test_scan_empty_directory(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            scanner = GenericScanner()
            snapshot = scanner.scan(tmpdir)
            assert snapshot.root_path == str(os.path.realpath(tmpdir))
            assert len(snapshot.files) == 0

    def test_scan_python_file(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            py_file = os.path.join(tmpdir, "main.py")
            with open(py_file, "w") as f:
                f.write(textwrap.dedent("""\
                    import os

                    def main():
                        \"\"\"Entry point.\"\"\"
                        print("hello")

                    class App:
                        pass
                """))

            scanner = GenericScanner()
            snapshot = scanner.scan(tmpdir)

            assert len(snapshot.files) == 1
            assert snapshot.files[0].language == "python"
            assert len(snapshot.symbols) >= 2  # main + App

            sym_names = {s.name for s in snapshot.symbols}
            assert "main" in sym_names
            assert "App" in sym_names

    def test_scan_multi_language(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            # Python file
            with open(os.path.join(tmpdir, "app.py"), "w") as f:
                f.write("def handler(): pass\n")

            # JS file
            with open(os.path.join(tmpdir, "index.js"), "w") as f:
                f.write("function render() {}\n")

            # Config file
            with open(os.path.join(tmpdir, "package.json"), "w") as f:
                f.write('{"name": "test"}\n')

            scanner = GenericScanner()
            snapshot = scanner.scan(tmpdir)

            languages = {f.language for f in snapshot.files}
            assert "python" in languages
            assert "javascript" in languages
            assert "json" in languages

    def test_scan_skips_git_directory(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            git_dir = os.path.join(tmpdir, ".git")
            os.makedirs(git_dir)
            with open(os.path.join(git_dir, "config"), "w") as f:
                f.write("[core]\n")

            with open(os.path.join(tmpdir, "main.py"), "w") as f:
                f.write("x = 1\n")

            scanner = GenericScanner()
            snapshot = scanner.scan(tmpdir)

            paths = {f.path for f in snapshot.files}
            assert not any(".git" in p for p in paths)

    def test_scan_detects_hazards_huge_file(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            big_file = os.path.join(tmpdir, "big.py")
            # Write a file > 100KB
            with open(big_file, "w") as f:
                f.write("x = 1\n" * 20000)

            scanner = GenericScanner()
            snapshot = scanner.scan(tmpdir)

            huge_hazards = [
                h for h in snapshot.hazards if h.kind.value == "huge_file"
            ]
            assert len(huge_hazards) >= 1

    def test_scan_metadata(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            with open(os.path.join(tmpdir, "app.py"), "w") as f:
                f.write("def foo(): pass\n")

            scanner = GenericScanner()
            snapshot = scanner.scan(tmpdir)

            assert "languages" in snapshot.metadata
            assert "python" in snapshot.metadata["languages"]
            assert snapshot.metadata["scanner"] == "generic"

    def test_scan_invalid_path(self):
        scanner = GenericScanner()
        with pytest.raises(ValueError, match="not a directory"):
            scanner.scan("/nonexistent/path/abc123")
