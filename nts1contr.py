import os.path
import argparse
import sys
import platform
import time
import json
import random
import rtmidi

midi_specs = {
    0: range(0, 127),
    14: [0, 25, 50, 75],
    16: range(0, 127),
    19: range(0, 127),
    20: range(0, 127),
    21: range(0, 127),
    24: range(0, 127),
    26: range(0, 127),
    28: range(0, 127),
    29: range(0, 127),
    30: range(0, 127),
    31: range(0, 127),
    33: range(0, 127),
    34: range(0, 127),
    35: range(0, 127),
    36: range(0, 127),
    42: [0, 18, 36, 54, 72, 90, 127],  # filter type
    43: range(0, 127),
    44: range(0, 127),
    45: range(0, 127),
    46: range(0, 127),
    53: [0, 25, 50, 75],  # osc_type,
    54: range(0, 127),
    55: range(0, 127),
    88: [0, 25, 50, 75, 127],  # fx_modulation
    89:  [0, 21, 42, 63, 84, 127],  # fx_delay,
    90: [0, 21, 42, 63, 84, 127],  # fx_reverb
    117: [0, 12, 24, 36, 48, 60, 72, 84, 96, 127],  # arp_pattern_length,
    118: [0, 21, 42, 63, 84, 127],  # intervals
    119: range(0, 127),
}


def main(args=None):
    parser = argparse.ArgumentParser()
    parser.add_argument('--midi', type=str, help='MIDI output port')
    parser.add_argument('--load', '-l', action='store_true', help='JSON file')
    parser.add_argument('--write', '-w', action='store_true', help='JSON file')
    parser.add_argument('--filename', '-f', type=str, help='JSON file')
    args = parser.parse_args()

    if (args.write is False and args.load is False):
        parser.error("either --write or --load is mandatory")

    if (args.filename is None):
        parser.error("--filename parameter is needed")

    filename = os.path.join(os.path.dirname(__file__), args.filename)

    if (args.load is True and not os.path.isfile(filename)):
        parser.error('Filename %s does not exist' % (filename))

    midi_out = rtmidi.MidiOut()
    for idx, name in enumerate(midi_out.get_ports()):
        if args.midi in name:
            print('Found preferred MIDI output device %d: %s' % (idx, name))
            midi_out.open_port(idx)
            break
        else:
            print('Ignoring unselected MIDI device: ', name)

    if not midi_out.is_port_open():
        if platform.system() == 'Windows':
            print(
                'Virtual MIDI outputs are not currently supported on Windows, see python-rtmidi documentation.')
        else:
            print('Creating virtual MIDI output.')
            midi_out.open_virtual_port(args.midi)

    if args.write is True:
        write(midi_out, filename)
    else:
        load(midi_out, filename)

        midi_out.close_port()
    del midi_out


def load(midi_out, filename):
    with open(filename) as json_file:
        bank = json.load(json_file)
        for cc, values in bank['values'].items():
            cc = int(cc)
            if (type(values) is dict):
                choosen_value = midi_specs[cc][int(values['value'])]
            else:
                choosen_value = values

            message = [0xb0, cc, int(choosen_value)]
            print(message)
            midi_out.send_message(message)


def write(midi_out, filename):

    data = {
        'name': None,
        'values': {}
    }

    for cc, values in midi_specs.items():
        random_value = random.choice(values)

        message = [0xb0, cc, random_value]
        midi_out.send_message(message)

        if (cc in [42, 88, 89, 90]):
            data['values'][cc] = {'value': values.index(
                random_value), 'active': True}
        elif (cc in [14, 53, 117, 118]):
            data['values'][cc] = values.index(random_value)
        else:
            data['values'][cc] = random_value

    if filename is not None:
        print('Saving values in %s' % (filename))
        with open(filename, 'w') as outfile:
            outfile.write(json.dumps(data))
    else:
        print(json.dumps(data))


if __name__ == '__main__':
    sys.exit(main() or 0)
