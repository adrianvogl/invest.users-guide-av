import docutils
import importlib

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
        arg_type (str): the type to format

    Returns:
        formatted string that links to a description of the input type
    """
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
        return f'`CSV <{INPUT_TYPES_HTML_FILE}#CSV>`__'
    else:
        return f'`{arg_type} <{INPUT_TYPES_HTML_FILE}#{arg_type}>`__'


def format_units_string(unit):
    """Represent a pint Unit as a user-friendly phrase.

    Args:
        unit (pint.Unit): the unit to format

    Returns:
        string describing the unit
    """
    # pluralize the first unit so that it reads more naturally
    custom_unit_plurals = {
        'foot': 'feet',
        'degree_Celsius': 'degrees_Celsius'
    }
    units_string = str(unit)
    if units_string == 'none':
        return ''

    words = units_string.split(' ')
    first_unit = words[0]
    # check if it has an irregular plural form
    if first_unit in custom_unit_plurals:
        words[0] = custom_unit_plurals[first_unit]
    # for all others, add 's' to the end
    else:
        words[0] = words[0] + 's'
    units_string = ' '.join(words)
    # pint separates words with underscores
    units_string = units_string.replace('_', ' ')
    # represent exponents with a caret rather than asterisks
    units_string = units_string.replace(' ** ', '^')
    # remove spaces around slashes
    units_string = units_string.replace(' / ', '/')
    return units_string


def format_required_string(required):
    """Represent an arg's required status as a user-friendly string.

    Args:
        required (bool | str): required property of an arg. May be `True`,
            `False`, or a conditional string.

    Returns:
        string
    """
    if required is True:
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
        list(geometries),
        key=lambda g: GEOMETRY_ORDER.index(g))
    return ', '.join(geom.lower() for geom in sorted_geoms)


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
    sorted_options = sorted(list(options.keys()))
    for option in sorted_options:
        lines.append(f'- {option}: {options[option]}')
    return lines


def format_options_string_from_set(options):
    """Represent a set of options as a comma-separated list.

    Args:
        options (set): the set of options to document

    Returns:
        string of alphabetically sorted, comma-separated options
    """
    return ', '.join(sorted(list(options)))


def format_args(args):
    """Format multiple args into a bulleted list.

    This is used for documenting:
        - all args for a model
        - a CSV's rows or columns
        - a vector's fields
        - a directory's contents

    Args:
        args (dict): a dictionary mapping keys to arg spec dictionaries

    Returns:
        list of strings, where each string is a line of RST-formatted text
    """
    items = []
    for arg_key, arg_spec in args.items():
        arg_name = arg_spec['name'] if 'name' in arg_spec else arg_key
        nested_spec = format_arg(arg_name, arg_spec)
        nested_spec[0] = f'- {nested_spec[0]}'
        items += nested_spec
    return items


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
        units_string = format_units_string(units)
        if units_string:
            in_parentheses.append(units_string)

    # Represent the required state as a string, defaulting to required
    # It doesn't make sense to include this for boolean checkboxes
    if spec['type'] != 'boolean':
        if 'required' in spec:
            required_string = format_required_string(spec['required'])
        else:
            required_string = 'required'
        in_parentheses.append(required_string)

    # Nested args may not have an about section
    if 'about' in spec:
        about_string = f': {spec["about"]}'
    else:
        about_string = ''

    first_line = f"**{name}** ({', '.join(in_parentheses)}){about_string}"

    # Add details for the types that have them
    indented_block = []
    if spec['type'] == 'option_string':
        # may be either a dict or set
        if isinstance(spec['options'], dict):
            indented_block.append('Options:')
            indented_block += format_options_string_from_dict(spec['options'])
        else:
            formatted_options = format_options_string_from_set(spec['options'])
            indented_block.append(f'Options: {formatted_options}')

    elif spec['type'] == 'vector':
        indented_block.append(
            'Accepted geometries: '
            f'{format_geometries_string(spec["geometries"])}')
        if spec['fields']:
            indented_block.append('Fields:')
            indented_block += format_args(spec['fields'])

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
        else:
            indented_block.append(f'{header_name.capitalize()}:')
            indented_block += format_args(spec[header_name])

    elif spec['type'] == 'directory' and 'contents' in spec and spec['contents']:
        indented_block.append('Contents:')
        indented_block += format_args(spec['contents'])

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
        lineno (int): the line number where the interpreted text beings.
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
    arguments = text.split(' ')
    # access the `investspec_module_prefix` config setting from conf.py
    prefix = inliner.document.settings.env.app.config.investspec_module_prefix
    if prefix:
        module_name = f'{prefix}.{arguments[0]}'
    else:
        module_name = arguments[0]
    # import the specified module (that should have an ARGS_SPEC attribute)
    module = importlib.import_module(module_name)

    # if only one argument to the role, document all args in the ARGS_SPEC
    if len(arguments) == 1:
        rst = '\n\n'.join(format_args(module.ARGS_SPEC['args']))

    # if two arguments to the role, document the (nested) arg at that location
    elif len(arguments) == 2:
        # Get the key:value pair at the specified location in the module's spec
        value = module.ARGS_SPEC['args']
        for key in arguments[1].split('.'):  # period-separated series of keys
            try:
                # (for raster band numbers only) convert to int
                value = value[int(key)]
            except ValueError:
                value = value[key]

        # format that spec into an RST formatted description
        # these formatting functions return a string
        if key in {'units', 'projection_units'}:
            rst = format_units_string(value)
        elif key == 'type':
            rst = format_type_string(value)
        elif key == 'permissions':
            rst = format_permissions_string(value)
        elif key == 'geometries':
            rst = format_geometries_string(value)
        # these formatting function return a list of strings, one for each line
        elif key == 'options' and isinstance(value, dict):
            rst = '\n\n'.join(format_options_string_from_dict(options))
        elif key == 'options' and isinstance(value, set):
            rst = '\n\n'.join(format_options_string_from_set(options))
        elif key in {'columns', 'rows', 'fields', 'contents'}:
            rst = '\n\n'.join(format_args(value))
        elif key in {'name', 'about', 'expression', 'regexp', 'projected',
                     'excel_ok', 'must_exist'}:
            # all the other
            rst = str(value)
        else:
            arg_name = value['name'] if 'name' in value else key
            rst = '\n\n'.join(format_arg(arg_name, value))

    else:
        raise ValueError(
            f'Expected 1 or 2 space-separated args but got {text}')

    return parse_rst(rst), []


def setup(app):
    """Add the custom extension to Sphinx.

    Sphinx calls this when it runs conf.py which configures
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
