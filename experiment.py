from time import perf_counter
from quadtree_and_linear.Quadtree import qt_run
from quadtree_and_linear.SampleQuadTree import sample_qt_run
from quadtree_and_linear.LienarSearch import linear_run
from box_graph.BoxGraph import box_run
from glob import glob
from pathlib import Path


files = glob("input/*.in")


variants = {
    "BoxGraph" : box_run,
    "QuadTree" : qt_run,
    "Linear Query": linear_run,
}

with open("report.txt", "w") as f: ...

for variant_name, variant in variants.items():
    print(f"========== ON {variant_name} ==========")
    for file in files:
        print(f"{file}")
        in_path = Path(file)
        fname = in_path.stem
        print(fname)
        t_start = perf_counter()
        report = variant(in_path, f"output/{fname}_{variant_name}.out")
        t_end = perf_counter()
        print(f"time {t_end - t_start}")
        with open("report.txt", "a") as f:
            f.write("\n")
            f.write(f"name, {variant_name},dataset, {fname}, total, {t_end-t_start}, ")
            for k,v in report.items():
                f.write(f"{k}, {v}, ")
