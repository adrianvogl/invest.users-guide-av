import docutils
import importlib

import pint
from natcap.invest import spec_utils

INPUT_TYPES_HTML_FILE = 'input_types.html'
# accepted geometries for a vector will be displayed in this order
GEOMETRY_ORDER = [
    'POINT',
    'MULTIPOINT',
    'LINESTRING',
    'MULTILINESTRING',
    'POLYGON',
    'MULTIPOLYGON']


def format_type_string(arg_type):
    """Represent an arg type as a user-friendly string.

    Args:
        arg_type (str|set(str)): the type to format. May be a single type or a
            set of types.

    Returns:
        formatted string that links to a description of the input type(s)
    """
    def format_single_type(arg_type):
        # Represent the type as a string. Some need a more user-friendly name.
        # we can only use standard docutils features here, so no :ref:
        # this syntax works to link to a section in a different page, but it
        # isn't universally supported and depends on knowing the built page name.
        if arg_type == 'freestyle_string':
            return f'`text <{INPUT_TYPES_HTML_FILE}#text>`__'
        elif arg_type == 'option_string':
            return f'`option <{INPUT_TYPES_HTML_FILE}#option>`__'
        elif arg_type == 'boolean':
            return f'`true/false <{INPUT_TYPES_HTML_FILE}#truefalse>`__'
        elif arg_type == 'csv':
            return f'`CSV <{INPUT_TYPES_HTML_FILE}#csv>`__'
        else:
            return f'`{arg_type} <{INPUT_TYPES_HTML_FILE}#{arg_type}>`__'
    if isinstance(arg_type, set):
        return ' or '.join(format_single_type(t) for t in sorted(arg_type))
    else:
        return format_single_type(arg_type)


def format_required_string(required):
    """Represent an arg's required status as a user-friendly string.

    Args:
        required (bool | str | None): required property of an arg. May be
            `True`, `False`, `None`, or a conditional string.

    Returns:
        string
    """
    if required is None or required is True:
        return 'required'
    elif required is False:
        return 'optional'
    else:
        # assume that the about text will describe the conditional
        return 'conditionally required'


def format_geometries_string(geometries):
    """Represent a set of allowed vector geometries as user-friendly text.

    Args:
        geometries (set(str)): set of geometry names

    Returns:
        string
    """
    # sort the geometries so they always display in a consistent order
    sorted_geoms = sorted(
        geometries,
        key=lambda g: GEOMETRY_ORDER.index(g))
    return '/'.join(geom.lower() for geom in sorted_geoms)


def format_permissions_string(permissions):
    """Represent a rwx-style permissions string as user-friendly text.

    Args:
        permissions (str): rwx-style permissions string

    Returns:
        string
    """
    permissions_strings = []
    if 'r' in permissions:
        permissions_strings.append('read')
    if 'w' in permissions:
        permissions_strings.append('write')
    if 'x' in permissions:
        permissions_strings.append('execute')
    return ', '.join(permissions_strings)


def format_options_string_from_dict(options):
    """Represent a dictionary of option: description pairs as a bulleted list.

    Args:
        options (dict): the dictionary of options to document, where keys are
            options and values are descriptions of the options

    Returns:
        list of RST-formatted strings, where each is a line in a bullet list
    """
    lines = []
    # casefold() is a more aggressive version of lower() that may work better
    # for some languages to remove all case distinctions
    sorted_options = sorted(
        list(options.keys()),
        key=lambda option: option.casefold()
    )
    for option in sorted_options:
        lines.append(f'- {option}: {options[option]}')
    return lines


def format_options_string_from_list(options):
    """Represent options as a comma-separated list.

    Args:
        options (list[str]): the set of options to document

    Returns:
        string of comma-separated options
    """
    return ', '.join(options)


def capitalize(title):
    """Capitalize a string into title case.

    Args:
        title (str): string to capitalize

    Returns:
        capitalized string (each word capitalized except linking words)
    """

    def capitalize_word(word):
        """Capitalize a word, if appropriate."""
        if word in {'of', 'the'}:
            return word
        else:
            return word[0].upper() + word[1:]

    title = ' '.join([capitalize_word(word) for word in title.split(' ')])
    title = '/'.join([capitalize_word(word) for word in title.split('/')])
    return title


def format_arg(name, spec):
    """Format an arg spec into user-friendly documentation.

    This is used for documenting:
        - a single top-level arg
        - a row or column in a CSV
        - a field in a vector
        - an item in a directory

    Args:
        name (str): Name to give the section. For top-level args this is
            arg['name']. For nested args it's typically their key in the
            dictionary one level up.
        spec (dict): A arg spec dictionary that conforms to the InVEST args
            spec specification. It must at least have the key `'type'`, and
            whatever other keys are expected for that type.
    Returns:
        list of strings, where each string is a line of RST-formatted text.
        The first line has the arg name, type, required state, description,
        and units if applicable. Depending on the type, there may be additional
        lines that are indented, that describe details of the arg such as
        vector fields and geometries, option_string options, etc.
    """
    type_string = format_type_string(spec['type'])
    in_parentheses = [type_string]

    # For numbers and rasters that have units, display the units
    units = None
    if spec['type'] == 'number':
        units = spec['units']
    elif spec['type'] == 'raster' and spec['bands'][1]['type'] == 'number':
        units = spec['bands'][1]['units']
    if units:
        units_string = spec_utils.format_unit(units)
        if units_string and units_string != 'none':
            in_parentheses.append(f'units: **{units_string}**')

    if spec['type'] == 'vector':
        in_parentheses.append(format_geometries_string(spec["geometries"]))

    # Represent the required state as a string, defaulting to required
    # It doesn't make sense to include this for boolean checkboxes
    if spec['type'] != 'boolean':
        # get() returns None if the key doesn't exist in the dictionary
        required_string = format_required_string(spec.get('required'))
        in_parentheses.append(f'*{required_string}*')

    # Nested args may not have an about section
    if 'about' in spec:
        about_string = f': {spec["about"]}'
    else:
        about_string = ''

    first_line = f"**{name}** ({', '.join(in_parentheses)}){about_string}"

    # Add details for the types that have them
    indented_block = []
    if spec['type'] == 'option_string':
        # may be either a dict or set. if it's empty, the options are
        # dynamically generated. don't try to document them.
        if spec['options']:
            if isinstance(spec['options'], dict):
                indented_block.append('Options:')
                indented_block += format_options_string_from_dict(spec['options'])
            else:
                formatted_options = format_options_string_from_list(spec['options'])
                indented_block.append(f'Options: {formatted_options}')

    elif spec['type'] == 'csv':
        if 'columns' in spec:
            header_name = 'columns'
        elif 'rows' in spec:
            header_name = 'rows'
        else:
            header_name = None

        if header_name is None:
            first_line += (
                ' Please see the sample data table for details on the format.')

    # prepend the indent to each line in the indented block
    return [first_line] + ['\t' + line for line in indented_block]


def parse_rst(text):
    """Parse RST text into a list of docutils nodes.

    Args:
        text (str): RST-formatted text to parse. May only use standard
            docutils features (no Sphinx roles etc)

    Returns:
        list[docutils.Node]
    """
    doc = docutils.utils.new_document(
        '',
        settings=docutils.frontend.OptionParser(
            components=(docutils.parsers.rst.Parser,)
        ).get_default_values())
    parser = docutils.parsers.rst.Parser()
    parser.parse(text, doc)

    # Skip the all-encompassing document node
    first_node = doc.next_node()
    number_of_top_level_nodes = len(
        first_node.traverse(descend=False, siblings=True))
    # if the content is wrapped in a paragraph node,
    # skip it so it can display in-line
    if (isinstance(first_node, docutils.nodes.paragraph) and
            number_of_top_level_nodes == 1):
        first_node = first_node.next_node()

    # This is a list of the node and its siblings
    return list(first_node.traverse(descend=False, siblings=True))


def invest_spec(name, rawtext, text, lineno, inliner, options={}, content=[]):
    """Custom docutils role to generate InVEST model input docs from spec.

    Docutils expects a function that accepts all of these args.

    Args:
        name (str): the local name of the interpreted text role, the role name
            actually used in the document.
        rawtext (str): a string containing the entire interpreted text
            construct. Return it as a ``problematic`` node linked to a system
            message if there is a problem.
        text (str): the interpreted text content, with backslash escapes
            converted to nulls (``\x00``).
        lineno (int): the line number where the interpreted text begins.
        inliner (Inliner): the Inliner object that called the role function.
            It defines the following useful attributes: ``reporter``,
            ``problematic``, ``memo``, ``parent``, ``document``.
        options (dict): A dictionary of directive options for customization, to
            be interpreted by the role function.  Used for additional
            attributes for the generated elements and other functionality.
        content (list[str]): the directive content for customization
            ("role" directive).  To be interpreted by the role function.

    Interpreted role functions return a tuple of two values:

    Returns:
        a tuple of two values:
            - A list of nodes which will be inserted into the document tree at
                the point where the interpreted role was encountered
            - A list of system messages, which will be inserted into the
                document tree immediately after the end of the current
                inline block.
    """
    # expect one or two space-separated arguments
    # the first argument is a module name to import (that has an ARGS_SPEC)
    # the second argument is a period-separated series of dictionary keys
    # that says what layer in the nested ARGS_SPEC dictionary to document
    arguments = text.split(' ', maxsplit=1)
    # access the `investspec_module_prefix` config setting from conf.py
    prefix = inliner.document.settings.env.app.config.investspec_module_prefix
    if prefix:
        module_name = f'{prefix}.{arguments[0]}'
    else:
        module_name = arguments[0]
    # import the specified module (that should have an ARGS_SPEC attribute)
    try:
        module = importlib.import_module(module_name)
    except ImportError:
        raise ValueError(
            f'Could not import the module "{module_name}" (line {lineno})')

    # document the (nested) arg at the given location
    # Get the key:value pair at the specified location in the module's spec
    value = module.ARGS_SPEC['args']
    keys = arguments[1].split('.')  # period-separated series of keys
    for i, key in enumerate(keys):
        # convert raster band numbers to ints
        if keys[i - 1] == 'bands':
            key = int(key)
        try:
            value = value[key]
        except KeyError:
            keys_so_far = '.'.join(keys[:i + 1])
            raise ValueError(
                f"Could not find the key '{keys_so_far}' in the "
                f"{module_name} model's ARGS_SPEC (line {lineno})")

    # format that spec into an RST formatted description string
    if isinstance(value, dict):
        arg_name = capitalize(value['name']) if 'name' in value else key
        rst = '\n\n'.join(format_arg(arg_name, value))
    elif isinstance(value, pint.Unit):
        rst = spec_utils.format_unit(value)
    else:
        rst = str(value)

    return parse_rst(rst), []


def setup(app):
    """Add the custom extension to Sphinx.

    Sphinx calls this when it runs conf.py which contains
    `extensions = ['investspec']`

    Args:
        app (sphinx.application.Sphinx)

    Returns:
        empty dictionary
    """
    # tell sphinx to get a config value called investspec_module_prefix from
    # conf.py. it defaults to an empty string.
    # its value will be accessible later in the invest_spec function.
    app.add_config_value('investspec_module_prefix', '', 'html')
    app.add_role("investspec", invest_spec)
    return {}
