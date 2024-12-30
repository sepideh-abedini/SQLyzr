import json


def calculate_cost():
    log_data = json.load(open("data/aug/gpt.log.json"))
    cost = 0
    for row in log_data:
        cost += row['usage']['total_tokens']
    print(f"Total token usage: {cost}")


def main():
    calculate_cost()


if __name__ == '__main__':
    main()
