from pathlib import Path


def main() -> None:
    program_path = Path("data/program-data.js")
    insert_path = Path(".devtools/kaged_lean_weeks_js.txt")

    if not program_path.exists():
        raise SystemExit("program-data.js not found")
    if not insert_path.exists():
        raise SystemExit("kaged_lean_weeks_js.txt not found")

    text = program_path.read_text(encoding="utf-8")
    if "kagedLean" in text:
        raise SystemExit("kagedLean program already present in program-data.js")

    insert = insert_path.read_text(encoding="utf-8").strip()

    stripped = text.rstrip()
    if not stripped.endswith("};"):
        raise SystemExit("program-data.js does not end with '};' as expected")

    updated = stripped[:-2].rstrip() + ",\n" + insert + "\n};\n"
    program_path.write_text(updated, encoding="utf-8")
    print("Inserted kagedLean program definition.")


if __name__ == "__main__":
    main()

