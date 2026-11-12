import csv
from collections import Counter

from cluster_model import predict_cluster

SKILL_COLUMNS = [
    "skill_programming",
    "skill_data_stats",
    "skill_frontend_design",
    "skill_business_pitch",
]


def assign_groups(students, n_groups=8):
    labeled = []
    for student in students:
        skills = [float(student[column]) for column in SKILL_COLUMNS]
        labeled.append({
            "id": student["id"],
            "cluster": predict_cluster(skills),
        })

    counts = Counter(row["cluster"] for row in labeled)
    cluster_order = sorted(counts, key=lambda cluster: (-counts[cluster], cluster))

    deal = []
    for cluster in cluster_order:
        members = [row for row in labeled if row["cluster"] == cluster]
        members.sort(key=lambda row: row["id"])
        deal.extend(members)

    group_by_id = {
        row["id"]: (index % n_groups) + 1
        for index, row in enumerate(deal)
    }

    return [
        {
            "id": row["id"],
            "cluster": row["cluster"],
            "group": group_by_id[row["id"]],
        }
        for row in labeled
    ]


def main():
    with open("class_dataset.csv", newline="") as handle:
        students = [
            {"id": row["netid"], **{column: row[column] for column in SKILL_COLUMNS}}
            for row in csv.DictReader(handle)
        ]

    assigned = assign_groups(students)
    clusters = sorted({row["cluster"] for row in assigned})
    missing = 0

    for group in range(1, 9):
        members = [row for row in assigned if row["group"] == group]
        cluster_counts = Counter(row["cluster"] for row in members)
        counts_text = ", ".join(
            f"cluster {cluster}: {cluster_counts[cluster]}" for cluster in clusters
        )
        print(f"group {group}: {len(members)} students  {counts_text}")
        if any(cluster_counts[cluster] == 0 for cluster in clusters):
            missing += 1

    print(f"groups missing a cluster: {missing}")


if __name__ == "__main__":
    main()
