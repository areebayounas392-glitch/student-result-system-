from flask import Flask, render_template, request, abort

app = Flask(__name__)

students = []

SUBJECTS = [
    {"key": "urdu", "name": "Urdu", "th": 100, "pr": 0},
    {"key": "english", "name": "English", "th": 100, "pr": 0},
    {"key": "math", "name": "Mathematics", "th": 100, "pr": 0},
    {"key": "physics", "name": "Physics", "th": 85, "pr": 30},
    {"key": "computer", "name": "Computer Science", "th": 75, "pr": 50},
]


def fmt(x):
    return int(x) if float(x).is_integer() else round(x, 2)


def get_grade(p):
    if p >= 80: return "A+"
    if p >= 70: return "A"
    if p >= 60: return "B"
    if p >= 50: return "C"
    if p >= 40: return "D"
    if p >= 33: return "E"
    return "F"


@app.route("/", methods=["GET", "POST"])
def home():
    error = None

    if request.method == "POST":
        try:
            info = {
                "name": request.form.get("name", "").strip(),
                "father": request.form.get("father", "").strip(),
                "roll_no": request.form.get("roll_no", "").strip(),
                "reg_no": request.form.get("reg_no", "").strip(),
                "group": request.form.get("group", "").strip(),
                "institution": request.form.get("institution", "").strip(),
            }

            if not info["name"] or not info["roll_no"]:
                raise ValueError("Student name aur Roll No zaroori hain.")

            results = []
            grand_total = 0
            grand_max = 0
            failed = []

            for s in SUBJECTS:
                p1 = float(request.form.get(s["key"] + "_1", ""))
                p2 = float(request.form.get(s["key"] + "_2", ""))
                pr = float(request.form.get(s["key"] + "_pr", "0") or 0) if s["pr"] else 0

                if not (0 <= p1 <= s["th"] and 0 <= p2 <= s["th"]):
                    raise ValueError(f"{s['name']}: theory marks 0 se {s['th']} ke darmiyan hon.")
                if s["pr"] and not (0 <= pr <= s["pr"]):
                    raise ValueError(f"{s['name']}: practical marks 0 se {s['pr']} ke darmiyan hon.")

                max_total = s["th"] * 2 + s["pr"]
                total = p1 + p2 + pr
                percent = total / max_total * 100
                status = "PASS" if percent >= 33 else "FAIL"
                if status == "FAIL":
                    failed.append(s["name"])

                results.append({
                    "name": s["name"],
                    "th_label": f"{s['th']}+{s['th']}",
                    "pr_label": s["pr"] if s["pr"] else "--",
                    "max_total": max_total,
                    "p1": fmt(p1),
                    "p2": fmt(p2),
                    "pr": fmt(pr) if s["pr"] else "--",
                    "total": fmt(total),
                    "percent": round(percent, 2),
                    "grade": get_grade(percent),
                    "status": status,
                })
                grand_total += total
                grand_max += max_total

            percentage = round(grand_total / grand_max * 100, 2)

            students.append({
                **info,
                "subjects": results,
                "grand_total": fmt(grand_total),
                "grand_max": grand_max,
                "percentage": percentage,
                "grade": get_grade(percentage),
                "failed": failed,
                "passed": len(failed) == 0,
            })

        except ValueError as e:
            msg = str(e)
            error = msg if "zaroori" in msg or ":" in msg else "Sab marks sahi numbers mein likhein."

    return render_template("index.html", students=students, subjects=SUBJECTS, error=error)


@app.route("/result/<int:student_id>")
def result(student_id):
    if student_id < 0 or student_id >= len(students):
        abort(404)
    return render_template("result.html", student=students[student_id])


if __name__ == "__main__":
    app.run(debug=True)