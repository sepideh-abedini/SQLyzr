from experimental.dscaler.sqlite_scaler import SqliteScaler


def main():
    orig_db_path = "experimental/dscaler/database"
    scaler = SqliteScaler(orig_db_path, 10)
    scaler.scale("farm")
    # table_schema = db_schema.tables['city']
    # col = table_schema.cols['Official_Name']
    # print(col)
    # val_gen = ValueGenerator()
    # val = val_gen.gen_value(col)
    # print(val)


if __name__ == '__main__':
    main()
