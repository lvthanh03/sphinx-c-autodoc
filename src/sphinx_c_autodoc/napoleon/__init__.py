"""
Extend napoleon to provide a `Members` section for C structs and unions
similar to the `Attributes` section in python objects.
"""
from functools import partial

from typing import Any, List, Union

from sphinx.ext.napoleon import GoogleDocstring


# pylint: disable=too-few-public-methods
class MemberDocString(GoogleDocstring):
    """
    A docstring that can handle documenting c member sections
    """

    def __init__(
        self,
        docstring: Union[str, List[str]],
        config: Any = None,
        app: Any = None,
        what: str = "",
        name: str = "",
        obj: Any = None,
        options: Any = None,
    ) -> None:
        self._sections = {
            "args": self._parse_parameters_section,
            "arguments": self._parse_parameters_section,
            "attention": partial(self._parse_admonition, "attention"),
            "attributes": self._parse_attributes_section,
            "caution": partial(self._parse_admonition, "caution"),
            "danger": partial(self._parse_admonition, "danger"),
            "enumerations": partial(self._parse_nested_section, "macro"),
            "error": partial(self._parse_admonition, "error"),
            "example": self._parse_examples_section,
            "examples": self._parse_examples_section,
            "hint": partial(self._parse_admonition, "hint"),
            "important": partial(self._parse_admonition, "important"),
            "members": partial(self._parse_nested_section, "member"),
            "note": partial(self._parse_admonition, "note"),
            "notes": self._parse_notes_section,
            "parameters": self._parse_parameters_section,
            "return": self._parse_returns_section,
            "returns": self._parse_returns_section,
            "references": self._parse_references_section,
            "see also": self._parse_see_also_section,
            "tip": partial(self._parse_admonition, "tip"),
            "todo": partial(self._parse_admonition, "todo"),
            "warning": partial(self._parse_admonition, "warning"),
            "warnings": partial(self._parse_admonition, "warning"),
            "warns": self._parse_warns_section,
            "yield": self._parse_yields_section,
            "yields": self._parse_yields_section,
        }

        super().__init__(docstring, config, app, what, name, obj, options)

    # pylint: disable=unused-argument
    def _parse_nested_section(self, nested_title: str, section: str) -> List[str]:
        """
        Parse a members section of a comment.

        The members section is only expected to be seen in processing of C
        files. Each item will be formatted using the ``.. c:member:: <name>``
        syntax.

        Args:
            section (str): The name of the parsed section.  Unused.
            nested_title (str): The name to give to the nested items.

        Returns:
            List[str]: The list of lines from `section` converted to the
                appropriate reST.
        """
        # Place a blank line prior to the section this ensures there is a
        # newline prior to the first `.. c:member::` section and thus it
        # doesn't get treated as a sentence in the same paragraph
        lines = [""]

        # Type should be unused, it's not normal in c to do `var (type)` it's
        # usuallly `type var`
        for name, _, desc in self._consume_fields():
            lines.extend([f".. c:{nested_title}:: {name}", ""])
            fields = self._format_field("", "", desc)
            lines.extend(self._indent(fields, 3))
            lines.append("")
        return lines


def process_autodoc_docstring(
    app: Any, what: str, name: str, obj: Any, options: Any, lines: List[str]
) -> None:
    """
    Call back for autodoc's ``autodoc-process-docstring`` event.

    Args:
        app (:class:`Sphinx`): The Sphinx application object
        what (str): The type of the object which the comment belongs to. One
            of "cmodule", "cmember", "ctype", "cfunction", "cstruct".
        name (str): The fully qualified name of the object. For C files this
            may be a little polluted as it will be
            ``my_file.c.some_item.some_items_member``.
        obj (any): The object itself
        options (dict): The options given to the directive.
        lines (List[str]): The lines of the comment.  This is modified in place.
    """
    docstring = MemberDocString(lines, app.config, app, what, name, obj, options)
    result_lines = docstring.lines()
    lines[:] = result_lines[:]


def setup(app):
    """
    Extend sphinx to assist sphinx_c_autodocs to allow Google style
    docstrings for C constructs.

    Args:
        app (:class:`Sphinx`): The Sphinx application object
    """
    app.setup_extension("sphinx.ext.napoleon")
    app.connect("autodoc-process-docstring", process_autodoc_docstring)
