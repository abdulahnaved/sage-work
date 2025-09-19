#!/usr/bin/env python3
import os, sys, nbformat, unittest, io, types, csv, ast

# Correct use of _file_ here
RESULTS_CSV = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "results",
    "grades.csv"
)

def load_notebook(nb_path):
    return nbformat.read(nb_path, as_version=4)

def extract_student_id(first_cell_src):
    try:
        tree = ast.parse(first_cell_src)
        for node in tree.body:
            if isinstance(node, ast.Assign):
                for t in node.targets:
                    if isinstance(t, ast.Name) and t.id.upper() == "STUDENT_ID":
                        if isinstance(node.value, ast.Constant):
                            return str(node.value.value)
    except Exception:
        pass
    return "UNKNOWN"

def split_cells(nb):
    impl, tests = [], []
    first_cell = ""
    for i, cell in enumerate(nb.cells):
        if cell.get("cell_type") != "code":
            continue
        if i == 0:  # first cell
            first_cell = cell.get("source", "")
            continue
        tags = set(map(str.lower, cell.get("metadata", {}).get("tags", [])))
        if "tests" in tags:
            tests.append(cell.get("source", ""))
        else:
            impl.append(cell.get("source", ""))
    return first_cell, impl, tests

def exec_cells(cells, g):
    for src in cells:
        exec(compile(src, "<cell>", "exec"), g)

def run_unittests(test_code_combined, g):
    mod = types.ModuleType("student_tests")
    mod._dict_.update(g)
    exec(compile(test_code_combined, "<tests>", "exec"), mod._dict_)
    suite = unittest.defaultTestLoader.loadTestsFromModule(mod)
    stream = io.StringIO()
    result = unittest.TextTestRunner(stream=stream, verbosity=0).run(suite)

    total  = result.testsRun
    failed = len(result.failures)
    errors = len(result.errors)
    passed = total - failed - errors
    return total, passed, failed + errors

def append_csv(student_id, total, passed, failed):
    score = round((passed / total) * 100, 2) if total > 0 else 0.0
    new = not os.path.exists(RESULTS_CSV)
    os.makedirs(os.path.dirname(RESULTS_CSV), exist_ok=True)
    with open(RESULTS_CSV, "a", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        if new:
            w.writerow(["student_id", "total", "passed", "failed", "score"])
        w.writerow([student_id, total, passed, failed, score])

def main():
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--nb", required=True, help="Path to student notebook")
    args = ap.parse_args()

    nb = load_notebook(args.nb)
    first_cell, impl_cells, test_cells = split_cells(nb)
    student_id = extract_student_id(first_cell)

    g = {"_name_": "student"}
    exec_cells(impl_cells, g)
    total, passed, failed = run_unittests("\n\n".join(test_cells), g)
    append_csv(student_id, total, passed, failed)

    print(f"{student_id}: {passed}/{total} passed ({round((passed/total)*100,2) if total>0 else 0}%)")

if __name__ == "__main__":
    main()