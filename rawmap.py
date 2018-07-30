"""Module to load Don't Satrve Together (DST) map save files.
"""
__author__ = 'Gabda'
__version__ = '1.0'


class Loader(object):
    """Loads a Don't Starve Together map into a structure of lists and dicts.
    As the save file is not sensitive to the order of the items in the dicts,
    this order is not retained.
    The class has the option to save the map in a human readable form.
    """

    def __init__(self, filename, save_to_file=True):
        self.filename = filename
        self.counter = 1
        self.parsed_map = []

        self.parsed_map = self._raw_map_to_list(save_to_file)
        self.map_data = self._map_reader()

    def _raw_map_to_list(self, write_to_file=False):
        """Makes the raw map into a list, which is human readable if written to
        a file. Divides the functional element of the input file into separate
        list elements, works as preprocessing to read the map data structure.

        Args:
            write_to_file: bool: if True, the return list is written to a
                file as well.

        Returns:
            list: Functionally parsed map.
        """

        # The map reader function is highly dependent on the structure of the
        # return value of this function. Caution is advised in case of
        # modifying this function.

        with open(self.filename, 'r') as raw_map:
            data = raw_map.readline()

        extended_map = []
        indents = 0
        in_quote = False

        for ch in data:

            if ch == "{":
                extended_map += ch
                indents += 1
                extended_map += "\n"
                extended_map += "\t" * indents
            elif ch == ",":
                extended_map += ch
                if not in_quote:
                    extended_map += "\n"
                    extended_map += "\t" * indents
            elif ch == "}":
                indents -= 1
                extended_map += "\n"
                extended_map += "\t" * indents
                extended_map += ch
            else:
                extended_map += ch

            if ch == '"':
                in_quote = not in_quote

        if write_to_file:
            indented_map_filename = self.filename + '.txt'
            with open(indented_map_filename, 'w') as readable_map:
                readable_map.write(''.join(extended_map))

        return ''.join(extended_map).split('\n')

    def _map_reader(self):
        """Recursively reads the parsed map list and saves into a structure
        of lists and dictionaries. The state of the recursion is saved in an
        internal global variable, and does not need to be given at function
        call.

        The map structure consists of 3 type of data:
        1, pure list
        2, pure dictionary
        3, mix of list and dict, from some point the items have keys that are
            numbers. For example when a treasure chest have item in the 1st,
            2nd and 9th places, only the item at the 9th place get a dict key.

        Returns:
            A fully loaded list or dict, a whole logical unit which starts at
            the line self.counter of the parsed map list, and ends when the
            logical unit is closed.
            If called when self.counter=1 (normal use case), returns the
            whole map.
        """

        def change_data_type(data_string):
            """All data is read as string from the save file. In case the type
            of the data is not intended to be string, the type chane happens
            here.

            Args:
                data_string: input data as string.

            Returns:
                Data with the appropriate type.
            """
            if not data_string:
                return ""

            if data_string == 'true':
                return True

            if data_string == 'false':
                return False

            if '"' in data_string:
                return data_string

            if "." in data_string:
                return float(data_string)

            return int(data_string)

        def get_next_line():
            # The counter is increased after every read from parsed_map.
            next_line = self.parsed_map[self.counter].strip()
            self.counter += 1
            return next_line.rstrip(",")

        line = get_next_line()

        if "=" not in line:
            """The data in this logical portion is a list, but it can be mixed
            with numbered items resembling a dictionary. In case of a numbered
            item, an appropriate number of empty items are added to the output
            list, so the data (the numerical value) in the key is not lost.
            """

            return_data = []
            next_element = 0  # Used for the list dict mixed cases

            while "}" not in line:
                if "{" in line:
                    # A new, embedded logical part (list or dict) is starting
                    if "=" in line:
                        # An item with a dict like key.
                        data = line.split("=")[0].strip()
                        # The number in the key is enclosed in [ ].
                        data = int(data[1:-1])
                        for i in range(next_element, data):
                            return_data.append('')
                        next_element = data + 1

                    return_data += [self._map_reader()]

                else:
                    next_element += 1
                    data = line

                    return_data += [change_data_type(data)]

                line = get_next_line()
                if not line:
                    print("Unexpected end of file")
                    return []

            return return_data

        """The data contained in this logical portion of the map data is in the
        form of a dictionary.
        """

        return_data = {}

        while "}" not in line:

            if "=" in line:
                parts = line.split('=')
                key = parts[0]
                data = '='.join(parts[1:])

                if data == "{":
                    data = self._map_reader()
                else:
                    data = change_data_type(data)

                return_data[key] = data

            else:
                print("Unhandled line in a dictionary like logical part:",
                      line)
                print("It can be found at line number {}.".format(
                    self.counter))

            line = get_next_line()

        return return_data
