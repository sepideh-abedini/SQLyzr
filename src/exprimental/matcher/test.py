from src.exprimental.matcher.batch_matcher import BatchMatcher


def main():
    in_file = "data/din/din_non_match.csv"
    db_dir = "data/spider/database"
    tables_path = "data/spider/tables.json"
    batch_matcher = BatchMatcher(db_dir=db_dir, tables_path=tables_path)
    match, total = batch_matcher.run(in_file)
    print(f"{match}/{total}")


if __name__ == "__main__":
    main()
