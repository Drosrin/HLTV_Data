import sys
import argparse
import importlib

def main():
    parser = argparse.ArgumentParser(description="Dynamically run a function from a specified module.")
    parser.add_argument('--module', type=str, required=True,
                        help='The module path (e.g., src.player)')
    parser.add_argument('--entry', type=str, default='main',
                        help='The function name to execute (default: main)')
    args = parser.parse_args()

    try:
        module = importlib.import_module(args.module)
    except ModuleNotFoundError as e:
        print(f"Error: Module '{args.module}' not found.", file=sys.stderr)
        sys.exit(1)

    if not hasattr(module, args.entry):
        print(f"Error: Function '{args.entry}' not found in module '{args.module}'.", file=sys.stderr)
        sys.exit(1)

    func = getattr(module, args.entry)
    if not callable(func):
        print(f"Error: '{args.entry}' is not a callable function in module '{args.module}'.", file=sys.stderr)
        sys.exit(1)

    func()

if __name__ == '__main__':
    main()