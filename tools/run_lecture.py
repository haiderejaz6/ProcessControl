#!/usr/bin/env python3
"""
Execute a lecture notebook in place, then clear the outputs of cells tagged
`predict` (code-interpretation cells: the class predicts the output before
the instructor runs the cell live).

Everything else keeps its output, so the static slides and Binder/RISE show
results immediately and every cell can still be re-run in class.

Usage:  python3 tools/run_lecture.py NOTEBOOK.ipynb [--timeout 600]
"""
import argparse
import os

import nbformat
from nbclient import NotebookClient


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("notebook")
    ap.add_argument("--timeout", type=int, default=600)
    args = ap.parse_args()

    nb = nbformat.read(args.notebook, as_version=4)
    here = os.path.dirname(os.path.abspath(args.notebook))
    NotebookClient(nb, timeout=args.timeout, kernel_name="python3",
                   resources={"metadata": {"path": here}}).execute()

    cleared = 0
    for c in nb.cells:
        if c.cell_type == "code" and "predict" in c.metadata.get("tags", []):
            c.outputs = []
            c.execution_count = None
            cleared += 1
    nbformat.write(nb, args.notebook)
    print(f"executed {os.path.basename(args.notebook)}; "
          f"cleared {cleared} predict cell(s)")


if __name__ == "__main__":
    main()
