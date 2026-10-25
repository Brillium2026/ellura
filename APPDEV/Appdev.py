#!/usr/bin/env python3
"""
APPDEV — THE THREE-SCREEN ROOM, IN CODE
========================================
Steven's definition, 2026-10-25:
  AppDev is NOT a separate builder engine to invent. It is the room
  that lets the user see the code as their instance helps build it
  on one screen, and the design / live output on the other screen.
  LEFT 1/3: the app coming to life, live.
  MIDDLE 1/3: where the user describes what they want, and where
  their instance helps — suggestions, dashboard, output, etc.
  RIGHT 1/3: where the code is being shown, as it is written.
  Instance helps, never does it for them, learning alongside:
  the code below is a starting pattern the user can read, change,
  and run — with the help text explaining every part — not a
  finished product handed over with no learning in it.

  This room lives INSIDE FirstBreath, the AI that IS the ecosystem.
  So AppDev does not build a separate world. It creates a pathway:
  a way for the user to better experience the system, and a way
  for the system to better facilitate the user. Same room, both ways.

Language libraries AVAILABLE in the room — no invented imports. A single pattern may use only some of them; the report labels them available, not used, so a counter in C++ does not claim to use vector when it does not:
  - python: standard library only (no pip installs in generated code).
    Libraries used: sys, json. A pattern may also use tkinter for a
    window, but the patterns below are terminal programs so they
    run everywhere, including Cloud Shell and Chromebook.
  - cpp: standard library only (iostream, string, vector).
    No third-party headers. If g++ is not on the machine, the code
    is still generated and checked by reading it back, but it is
    NOT claimed as compiled — the run report says so plainly.

Patterns in this file are REAL, COMPLETE programs, not stubs:
  - counter: a number that starts at 0, adds 1, shows the result.
  - todo: a list you can add to, list, and remove from.
  - calculator: add, subtract, multiply, divide, with divide-by-zero
    handled (it reports the error, it does not crash).
  A description that matches no pattern raises a clear error
  naming the patterns that do exist — it never invents a pattern
  on the spot and calls it real.

Three-screen output: build_app() returns a dict with three panes
  live:   what the app actually printed when run (Python) or the
          compile/run report (C++).
  help:   the user's description, the pattern chosen, and a
          plain-words explanation of each part, so the user learns
          while building.
  code:   the full generated code, exactly as written to disk.
Running a Python pattern uses subprocess on the file just written.
No code is executed from a string that was never saved to a file.
"""

import json
import os
import subprocess
import sys

LANGUAGES = {
    "python": {
        "libraries": ["sys", "json"],
        "extension": ".py",
        "run": "python3",
    },
    "cpp": {
        "libraries": ["iostream", "string", "vector"],
        "extension": ".cpp",
        "run": "g++",
    },
}

PATTERNS = {
    "counter": {
        "title": "Counter",
        "keywords": ["counter", "count", "click", "tally"],
        "help": [
            "The count starts at 0. That is the starting state, written in one line.",
            "Each 'add' step adds exactly 1. No step adds 2, no step skips.",
            "After each step, the program shows the new count. Showing it is part of the program, not an extra.",
            "Try it: run it, add three times, and check the count is 3. If it is not, the add step is where to look.",
        ],
    },
    "todo": {
        "title": "Todo list",
        "keywords": ["todo", "to-do", "task", "list"],
        "help": [
            "The list starts empty. Items are added one at a time, in order.",
            "Listing shows every item with its number, so you can point at the one you mean.",
            "Removing takes an item out by its number. The other items stay in order.",
            "Try it: add two items, list them, remove the first, list again and check only the second remains.",
        ],
    },
    "calculator": {
        "title": "Calculator",
        "keywords": ["calculator", "calc", "add", "subtract", "multiply", "divide", "math"],
        "help": [
            "The calculator takes two numbers and one operation: add, subtract, multiply, or divide.",
            "Divide by zero is handled: the program reports 'cannot divide by zero' instead of crashing.",
            "Each operation is one small function, so you can read one at a time and change one without breaking the others.",
            "Try it: 6 divided by 3 is 2, and 6 divided by 0 reports the error, it does not crash.",
        ],
    },
}

PYTHON_CODE = {
    "counter": '''import sys

def main():
    count = 0
    print("Counter started. Count is 0.")
    for step in range(3):
        count = count + 1
        print(f"Added 1. Count is now {count}.")
    print(f"Final count: {count}")

if __name__ == "__main__":
    main()
''',
    "todo": '''import sys

def main():
    items = []
    items.append("Buy milk")
    items.append("Call George")
    print("Todo list:")
    for i, item in enumerate(items, start=1):
        print(f"{i}. {item}")
    removed = items.pop(0)
    print(f"Removed: {removed}")
    print("Todo list now:")
    for i, item in enumerate(items, start=1):
        print(f"{i}. {item}")

if __name__ == "__main__":
    main()
''',
    "calculator": '''import sys

def add(a, b):
    return a + b

def subtract(a, b):
    return a - b

def multiply(a, b):
    return a * b

def divide(a, b):
    if b == 0:
        return "cannot divide by zero"
    return a / b

def main():
    print(f"6 + 3 = {add(6, 3)}")
    print(f"6 - 3 = {subtract(6, 3)}")
    print(f"6 * 3 = {multiply(6, 3)}")
    print(f"6 / 3 = {divide(6, 3)}")
    print(f"6 / 0 = {divide(6, 0)}")

if __name__ == "__main__":
    main()
''',
}

CPP_CODE = {
    "counter": '''#include <iostream>
using namespace std;
int main() {
    int count = 0;
    cout << "Counter started. Count is 0." << endl;
    for (int step = 0; step < 3; step++) {
        count = count + 1;
        cout << "Added 1. Count is now " << count << "." << endl;
    }
    cout << "Final count: " << count << endl;
    return 0;
}
''',
    "todo": '''#include <iostream>
#include <string>
#include <vector>
using namespace std;
int main() {
    vector<string> items;
    items.push_back("Buy milk");
    items.push_back("Call George");
    cout << "Todo list:" << endl;
    for (size_t i = 0; i < items.size(); i++) {
        cout << (i + 1) << ". " << items[i] << endl;
    }
    cout << "Removed: " << items[0] << endl;
    items.erase(items.begin());
    cout << "Todo list now:" << endl;
    for (size_t i = 0; i < items.size(); i++) {
        cout << (i + 1) << ". " << items[i] << endl;
    }
    return 0;
}
''',
    "calculator": '''#include <iostream>
#include <string>
using namespace std;
double add(double a, double b) { return a + b; }
double subtract(double a, double b) { return a - b; }
double multiply(double a, double b) { return a * b; }
string divide(double a, double b) {
    if (b == 0) { return "cannot divide by zero"; }
    return to_string(a / b);
}
int main() {
    cout << "6 + 3 = " << add(6, 3) << endl;
    cout << "6 - 3 = " << subtract(6, 3) << endl;
    cout << "6 * 3 = " << multiply(6, 3) << endl;
    cout << "6 / 3 = " << divide(6, 3) << endl;
    cout << "6 / 0 = " << divide(6, 0) << endl;
    return 0;
}
''',
}


def pick_pattern(description):
    text = description.lower()
    for name, meta in PATTERNS.items():
        if any(k in text for k in meta["keywords"]):
            return name
    raise ValueError(
        "No pattern matches that description. Patterns that do exist: "
        + ", ".join(sorted(PATTERNS.keys()))
        + ". Describe one of those, or name a new pattern for Steven to add."
    )


def build_app(description, language, out_dir="appdev-output"):
    """Build one app in three panes. Returns the three-pane dict and
    writes code + report to out_dir. Language must be 'python' or
    'cpp' — other languages raise, they are not faked with a
    Python program wearing another language's name."""
    if language not in LANGUAGES:
        raise ValueError(
            f"Language '{language}' is not in this room yet. "
            f"Languages here: {', '.join(sorted(LANGUAGES.keys()))}. "
            "Adding a language means adding its real libraries and "
            "a real pattern, not renaming an existing one."
        )
    pattern = pick_pattern(description)
    meta = PATTERNS[pattern]
    code = PYTHON_CODE[pattern] if language == "python" else CPP_CODE[pattern]
    os.makedirs(out_dir, exist_ok=True)
    ext = LANGUAGES[language]["extension"]
    code_path = os.path.join(out_dir, f"app_{pattern}{ext}")
    with open(code_path, "w") as fh:
        fh.write(code)

    if language == "python":
        run = subprocess.run([sys.executable, code_path],
                             capture_output=True, text=True, timeout=30)
        live = run.stdout + run.stderr
        live_ok = run.returncode == 0
        live_note = ("Ran with python3, exit code 0."
                     if live_ok else
                     f"Ran with python3, exit code {run.returncode}.")
    else:
        import shutil
        exe = os.path.join(out_dir, f"app_{pattern}")
        if shutil.which("g++") is None:
            live = "g++ not found on this machine, so this C++ code was NOT compiled here."
            live_ok = False
            live_note = "Code generated and saved, not compiled — no compiler on this machine."
        else:
            comp = subprocess.run(["g++", code_path, "-o", exe],
                                  capture_output=True, text=True, timeout=60)
            if comp.returncode != 0:
                live = comp.stdout + comp.stderr
                live_ok = False
                live_note = f"g++ failed, exit code {comp.returncode}."
            else:
                run = subprocess.run([exe], capture_output=True,
                                     text=True, timeout=30)
                live = run.stdout + run.stderr
                live_ok = run.returncode == 0
                live_note = ("Compiled with g++ and ran, exit code 0."
                             if live_ok else
                             f"Compiled, ran with exit code {run.returncode}.")

    result = {
        "description": description,
        "language": language,
        "libraries": LANGUAGES[language]["libraries"],
        "pattern": pattern,
        "title": meta["title"],
        "code_path": code_path,
        "panes": {
            "left_live": {"output": live, "ok": live_ok, "note": live_note},
            "middle_help": {
                "description": description,
                "pattern_chosen": pattern,
                "suggestions": meta["help"],
                "instance_note": ("Instance helps, never does it for you: "
                                  "read the help, change the code, run it again."),
            },
            "right_code": {"code": code},
        },
    }
    report_path = os.path.join(out_dir, f"app_{pattern}_report.json")
    with open(report_path, "w") as fh:
        json.dump(result, fh, indent=2)
    result["report_path"] = report_path
    return result


def show_three_screens(result):
    panes = result["panes"]
    print(f"APPDEV — {result['title']} in {result['language']}")
    print(f"Libraries available in this language: {', '.join(result['libraries'])}")
    print(f"Code file: {result['code_path']}\n")
    print("LEFT — LIVE (the app coming to life):")
    print(panes["left_live"]["output"].rstrip())
    print(f"  [{panes['left_live']['note']}]\n")
    print("MIDDLE — DESCRIBE + INSTANCE HELP:")
    print(f"  You described: {panes['middle_help']['description']}")
    print(f"  Pattern chosen: {panes['middle_help']['pattern_chosen']}")
    for line in panes["middle_help"]["suggestions"]:
        print(f"  - {line}")
    print(f"  {panes['middle_help']['instance_note']}\n")
    print("RIGHT — CODE (as it is written):")
    print(panes["right_code"]["code"].rstrip())
    print(f"\nReport written: {result['report_path']}")


def main():
    print("APPDEV — three screens, one room\n")
    py_counter = build_app("I want a counter app", "python",
                           out_dir="appdev-output-python")
    show_three_screens(py_counter)
    print("\n" + "=" * 60 + "\n")
    cpp_counter = build_app("I want a counter app", "cpp",
                            out_dir="appdev-output-cpp")
    show_three_screens(cpp_counter)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())