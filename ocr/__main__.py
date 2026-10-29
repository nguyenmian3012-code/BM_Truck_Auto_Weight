import json
import sys

from ocr.engine import read_image
from ocr.sync import sync_forever


def main(argv):
    if "--sync" in argv:
        sync_forever(once="--once" in argv)
        return 0
    paths = [a for a in argv if not a.startswith("-")]
    if not paths:
        print("python -m ocr anh.jpg | python -m ocr --sync [--once]", file=sys.stderr)
        return 2
    for path in paths:
        with open(path, "rb") as fh:
            print(json.dumps(read_image(fh.read()), ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
