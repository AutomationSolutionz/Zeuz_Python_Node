from .selenium import declarations as selenium_declarations


_excluded = {
    "click and hold",
    "validate table",
    "validate table row size",
    "validate table column size",
    "playwright",
}

declarations = tuple(
    {**declaration, "module": "playwright"}
    for declaration in selenium_declarations
    if declaration["name"] not in _excluded
)
