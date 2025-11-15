#!/usr/bin/env python3
import os
import nbformat
import unittest
import io
import types
import csv
import ast

# Updated path for container environment - save in Submissions/results
RESULTS_CSV = "/Submissions/results/grades.csv"

def load_notebook(nb_path):
    return nbformat.read(nb_path, as_version=4)

def extract_student_ids(first_cell_src):
    """
    Extract STUDENT_ID or STUDENT_IDs (list) from the first cell.
    Supports:
        STUDENT_ID = "abc123"
        STUDENT_IDs = ["abc123", "xyz789"]
    """
    try:
        tree = ast.parse(first_cell_src)
        for node in tree.body:
            if isinstance(node, ast.Assign):
                for t in node.targets:
                    # Case 1: Single ID
                    if isinstance(t, ast.Name) and t.id.upper() == "STUDENT_ID":
                        if isinstance(node.value, ast.Constant):
                            return [str(node.value.value)]
                    # Case 2: List of IDs
                    if isinstance(t, ast.Name) and t.id.upper() == "STUDENT_IDS":
                        if isinstance(node.value, (ast.List, ast.Tuple)):
                            ids = []
                            for elt in node.value.elts:
                                if isinstance(elt, ast.Constant):
                                    ids.append(str(elt.value))
                            return ids
    except Exception:
        pass
    return ["UNKNOWN"]

def split_cells(nb):
    """Split notebook into first cell (ID), implementation cells, and test cells"""
    impl, tests = [], []
    first_cell = ""
    for i, cell in enumerate(nb.cells):
        if cell.get("cell_type") != "code":
            continue
        if i == 0:
            first_cell = cell.get("source", "")
            continue
        tags = set(map(str.lower, cell.get("metadata", {}).get("tags", [])))
        if "tests" in tags:
            tests.append(cell.get("source", ""))
        else:
            impl.append(cell.get("source", ""))
    return first_cell, impl, tests

def exec_cells(cells, g):
    """Execute student implementation cells"""
    for src in cells:
        exec(compile(src, "<cell>", "exec"), g)

def run_unittests(test_code_combined, g):
    """Run unittest code from tagged cells"""
    mod = types.ModuleType("student_tests")
    mod.__dict__.update(g)
    exec(compile(test_code_combined, "<tests>", "exec"), mod.__dict__)
    suite = unittest.defaultTestLoader.loadTestsFromModule(mod)
    stream = io.StringIO()
    result = unittest.TextTestRunner(stream=stream, verbosity=0).run(suite)

    total  = result.testsRun
    failed = len(result.failures) + len(result.errors)
    passed = total - failed
    return total, passed, failed

def append_csv(student_ids, total, passed, failed):
    """Append one line per student (single or group) to grades.csv"""
    score = round((passed / total) * 100, 2) if total > 0 else 0.0
    os.makedirs(os.path.dirname(RESULTS_CSV), exist_ok=True)
    new_file = not os.path.exists(RESULTS_CSV)
    with open(RESULTS_CSV, "a", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        if new_file:
            w.writerow(["student_id", "total", "passed", "failed", "score"])
        for sid in student_ids:
            w.writerow([sid, total, passed, failed, score])

def main():
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--nb", required=True, help="Path to student notebook")
    args = ap.parse_args()

    nb = load_notebook(args.nb)
    first_cell, impl_cells, test_cells = split_cells(nb)
    student_ids = extract_student_ids(first_cell)

    g = {"__name__": "student"}
    exec_cells(impl_cells, g)
    total, passed, failed = run_unittests("\n\n".join(test_cells), g)
    append_csv(student_ids, total, passed, failed)

    ids_str = ", ".join(student_ids)
    print(f"{ids_str}: {passed}/{total} passed ({round((passed/total)*100,2) if total>0 else 0}%)")

if __name__ == "__main__":
    main()