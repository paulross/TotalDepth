import sys


def main() -> int:
    pos = 0
    with open(sys.argv[1], 'rb') as fobj:
        while True:
            by: bytes = fobj.read(1)
            if len(by) == 0:
                break
            while by == b'\xff':
                by: bytes = fobj.read(1)
                if len(by) == 0:
                    break
                if by == b'\x01':
                    new_pos = fobj.tell() - 4
                    print(f'0x{new_pos:08x} 0x{new_pos - pos:08x}')
                    pos = new_pos
    return 0


if __name__ == '__main__':
    sys.exit(main())
