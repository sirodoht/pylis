def parse_coefficients(coefficient_list, monomial):
    """
    :rtype : None
    :param coefficient_list: List in which coefficients will be stored
    :param monomial: A string (e.g. -3x1) which will be parsed to its coefficient (e.g. -3)
    """
    import re

    # Check which pattern matches. Valid are: (s)(n)lv
    #   parenthesis indicate optional existence
    #   s is + or - (absence means +)
    #   n is a number (coefficient, absence means 1)
    #   l is a lowercase latin letter (variable letter)
    #   v is a number, probably incremental (variable number)
    if re.match('[ ]*[\+ ]?[\d]+[\.]?[\d]*', monomial):
        float_cast = float(re.match('[ ]*[\+ ]?[\d]+[\.]?[\d]*', monomial).group(0))
        coefficient_list.append(float_cast)
    elif re.match('[ ]*[\-][\d]+[\.]?[\d]*', monomial):
        float_cast = float(re.match('[ ]*[\-][\d]+[\.]?[\d]*', monomial).group(0))
        coefficient_list.append(float_cast)
    elif re.match('[ ]*[\+]*[a-z][\d]+', monomial):
        coefficient_list.append(1)
    elif re.match('[ ]*[\-][a-z][\d]+', monomial):
        coefficient_list.append(-1)


def parse_lp1(input_filename, output_filename):
    """
    :rtype : tuple
    :param input_filename: Filename of the linear problem input
    :param output_filename: Filename of the output, produced by this function
    :return: Returns A-matrix, b-vector, c-vector, Eqin, MinMax
    """
    import re

    # Initialize error variable
    #   If error != 0 then there was a file input problem
    error = 0

    try:
        infile = open(input_filename)
    except FileNotFoundError:
        error = 1
        print('\nInput file error: File not found.')

    lines = []
    if error != 1:
        for line in infile:
            lines.append(line)

        infile.close()

    for line in lines:
        print(line, end='')

    # Check if problem is max or min
    minmax_line = ''
    for line in lines:
        if re.match('^[ ]*max|min', line):
            minmax_line = line

    minmax = 0
    objective_function = ''
    if re.match('^[ ]*max', minmax_line):
        minmax = 1
        objective_function = minmax_line
        objective_function = objective_function.strip('max')
    elif re.match('^[ ]*min', minmax_line):
        minmax = -1
        objective_function = minmax_line
        objective_function = objective_function.strip('min')

    if minmax_line == '' and minmax == 0:
        error = 2
        print('\nInput file error: Objective function not found.')

    # Fill c-vector with objective function coefficients
    c_vector = []

    regex = re.compile('^[\+\- ]?[\d]*[\.]?[\d]*[a-z][\d+]')
    while regex.match(objective_function):
        monomial = regex.match(objective_function).group(0)
        parse_coefficients(c_vector, monomial)
        objective_function = objective_function.replace(monomial, '', 1)

    # Fill A-matrix, b-vector and Eqin using problem constraints
    a_matrix = []
    b_vector = []
    eqin = []

    st_line = ''
    st_index = 0
    for index, line in enumerate(lines):
        if 'st' in line:
            st_index = index
            st_line = line

    if re.match('^[ ]*st', st_line):
        st_line = st_line.replace('st', '  ', 1)

    if st_line == '':
        error = 3
        print('\nInput file error: Constraints line not found. No \'st\' keyword.')

    while st_index < len(lines) - 1:
        sub_a_vector = []
        a_matrix.append(sub_a_vector)
        while True:
            st_line = st_line.strip(' ')
            if re.match('^[\+\- ]?[\d]*[\.]?[\d]*[a-z][\d+]', st_line):
                monomial = re.match('^[\+\- ]?[\d]*[\.]?[\d]*[a-z][\d+]', st_line).group(0)
                parse_coefficients(sub_a_vector, monomial)
                st_line = st_line.replace(monomial, '', 1)
            elif re.match('^[<>=]+', st_line):
                monomial = re.match('^[<>=]+', st_line).group(0)
                if monomial == '<=':
                    eqin.append(-1)
                elif monomial == '>=':
                    eqin.append(1)
                elif monomial == '=':
                    eqin.append(0)
                else:
                    error = 4
                    print('\nInput file error: Unexpected character; expected <=, >=, = but got', monomial)
                st_line = st_line.replace(monomial, '', 1)
            elif re.match('^[\d]+', st_line):
                monomial = re.match('^[\d]+', st_line).group(0)
                int_cast = int(re.match('^[\d]+', st_line).group(0))
                b_vector.append(int_cast)
                st_line = st_line.replace(monomial, '', 1)
            else:
                if not sub_a_vector:    # Evaluates true when the are empty lines among the constraints
                    a_matrix.pop()
                break

        # Increment line number and get the next one
        st_index += 1
        st_line = lines[st_index]

        # Search for final statement and no errors
        if st_line == 'end\n' and error == 0:
            print('\nFile input successful.')
            break

    # Write problem to output file
    outfile = open(output_filename, 'w')
    outfile.write('c-vector: [' + ', '.join(map(str, c_vector)) + ']\n')

    outfile.write('\nA-matrix: [')
    thing = ''
    for index, sub_a_vector in enumerate(a_matrix):
        thing += '[ ' + ', '.join(map(str, sub_a_vector)) + ']'
        if index != (len(a_matrix) - 1):
            thing += ', '
    outfile.write(thing + ']\n')

    outfile.write('\nb-vector: [' + ', '.join(map(str, b_vector)) + ']\n')
    outfile.write('\nEqin: [' + ', '.join(map(str, eqin)) + ']\n')
    outfile.write('\nMinMax: [' + str(minmax) + ']\n')
    outfile.close()

    # Return all lists and variable created
    return a_matrix, b_vector, c_vector, eqin, minmax
