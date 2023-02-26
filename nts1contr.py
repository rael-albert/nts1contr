import argparse
import sys
import platform
import time
import json
import random
import rtmidi

def main(args=None):
    ap = argparse.ArgumentParser()
    ap.add_argument('--midi', type=str, help='MIDI output port')
    ap.add_argument('-r', '--r', help='Read values')
    ap.add_argument('-w', '--write', help='Generate JSON')
    args = ap.parse_args()

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
            print('Virtual MIDI outputs are not currently supported on Windows, see python-rtmidi documentation.')
        else:
            print('Creating virtual MIDI output.')
            midi_out.open_virtual_port(args.midi)

    midi_specs = {
        0: range(0, 127),
        14: [0, 25, 50, 75, 127], # envelope type
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
        42: [0, 18, 36, 54, 72, 90, 127], # filter type
        43: range(0, 127),
        44: range(0, 127),
        46: range(0, 127),
        54: range(0, 127),
        55: range(0, 127),
        88: [0, 25, 50, 75, 127], #fx_modulation
        89:  [0, 21, 42, 63, 84, 127], #fx_delay,
        90: [0, 21, 42, 63, 84, 127], #fx_reverb
        117: range(0, 127),
        118: range(0, 127),
        119: range(0, 127),
    }

    for cc, values in midi_specs.items():
        message  = [0xb0, cc, random.choice(values)]
        print(message)
        midi_out.send_message(message)

    midi_out.close_port()
    del midi_out

if __name__ == '__main__':
    sys.exit(main() or 0)