import numpy as np

outfilename = 'Inc/windowfunctions.h'
# keep both following lines in sync!
size = 32768
bits = 15

def Hann(i, N):
    return 0.5*(1.0-np.cos(2*np.pi*i/N))

def Barlett(i, N):
    return 1.0 - np.abs((i-N/2) / (N/2))

def Welch(i, N):
    return 1.0 - np.square((i-N/2) / (N/2))

windows = [Hann, Barlett, Welch]


def generate_window_table_entries(window):
    entries = ''
    rows = int(pow(2, bits-4-1))  # in each row should be 8 entries, -1 for just writing half of the the size
    _size = float(size)
    for row in range(rows):
        entries += '        '
        for col in range(16):
            i = row * 16 + col
            value = window(i, _size)  # Use float!
            entries += str(value)
            entries += ', '
        entries += '\n'
    entries = entries[:-3]  # remove last \n, colon and whitespace
    return entries


def gen_table():
    content = 'const FFT_DATATYPE windows[WINDOW_FUNCTIONS][WINDOW_FUNCTION_TABLE_SIZE/2] = {\n'
    for window in windows:
        content += '    {\n'
        content += generate_window_table_entries(window)  + '\n'
        content += '    },\n'
    content = content[:-2]  # remove last \n, and colon.
    content += '\n};\n'
    return content


def gen_wss_table_entries(window):
    entries = '{'
    for _bits in range(1, bits+1):
        N = int(pow(2, _bits))
        wss = np.sum(np.square(window(np.linspace(0, N, num=N), N)))
        entries += str(wss) + ', '
    entries = entries[:-2]
    entries += '}'
    return entries


def gen_wss_table():
    table = 'const float windows_ss[%s][%s] = {\n' % (len(windows), str(bits))
    for window in windows:
        table += '    ' + gen_wss_table_entries(window) + ',\n'
    table = table[:-2]
    table += '\n};'
    return table

def main():
    if int(pow(2, bits)) != size:
        raise ValueError("size and bits settings doesn't match")

    with open(outfilename, 'w') as f:
        f.write('/* Generated by "generate_window_functions.py". Consider changing the script for modifications. */\n')
        f.write('#ifndef WINDOWFUNCTIONS_H_\n')
        f.write('#define WINDOWFUNCTIONS_H_\n\n')
        f.write('#include "fft.h"\n')
        f.write('#if (WINDOW_FUNCTION_TABLE_SIZE != {})\n'.format(size))
        f.write('#error "The windowfunctiontable must have the resolution of the doubled max fft size"\n')
        f.write('#endif\n\n')
        f.write('#if (WINDOW_FUNCTIONS != {})\n'.format(len(windows)))
        f.write('#error "The windowfunctiontable must have as much window functiond data as defined in the fft.h"\n')
        f.write('#endif\n\n')
        f.write(gen_table() + '\n\n')
        f.write(gen_wss_table() + '\n')

        f.write('#endif\n')


if __name__ == '__main__':
    main()
