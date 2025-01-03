import asyncio
import time
from datetime import datetime, timedelta

from src.cat.catter import Catter
from src.eval.lib import Timer
from src.gpt.gpt_batch_gateway import GptBatchGateway
from src.gpt.gpt_client import GptBatchClient
from src.gpt.gpt_from_file_sender import GptSingleSender
from src.gpt.gpt_gateway import GptGateway
from src.gpt.models import BatchInputRequest
from src.parse.graph_drawer import draw_graph
from src.parse.parser import SqlParser


# catter = Catter()
#
# sql = "SELECT T1.`School Name`, T2.Street, T2.City, T2.State, T2.Zip FROM frpm AS T1 INNER JOIN schools AS T2 ON T1.CDSCode = T2.CDSCode WHERE T2.County = 'Monterey' AND T1.`Free Meal Count (Ages 5-17)` > 800 AND T1.`School Type` = 'High Schools (Public)'"
# sql = "SELECT T2.School, T1.AvgScrWrite, T2.Phone FROM schools AS T2 LEFT JOIN satscores AS T1 ON T2.CDSCode = T1.cds WHERE strftime('%Y', T2.OpenDate) > '1991' OR strftime('%Y', T2.ClosedDate) < '2000'"
# sql = "SELECT x FROM schools WHERE strftime('%Y', T2.OpenDate) > '1991'"
# parser = SqlParser()
# draw_graph(parser.parse(sql), "graph.png")
#
# cat = catter.get_category(sql)
# print(cat)


async def main():
    bar = GptBatchClient()
    timer = Timer()
    timer.start()
    bar.list_cur_batches()
    print(timer.stop().seconds)
    # timer = Timer()
    # timer.start()
    # gw = GptGateway()
    # gw = GptBatchGateway()
    # reqs = []
    # sender = GptSingleSender()
    # futures = []
    # for i in range(1, 9):
    #     future = gw.send_batch(f"data/din/P{i}.jsonl")
    #     futures.append(future)
    # await asyncio.gather(*futures)
    # await sender.send_from_file(in_file, out_file)
    # with open("data/din/pred_0.0_0.txt.classif.in.jsonl") as file:
    #     for line in file.readlines():
    #         req = BatchInputRequest.model_validate_json(line)
    #         reqs.append(req)
    #
    # futures = []
    # for req in reqs:
    #     future = gw.track_and_send(req)
    #     futures.append(future)
    #     print(f"{req.custom_id} sent")
    #     # print(res)
    #     # futures.append(gw.track_and_send(req))
    #
    # ress = await asyncio.gather(*futures)
    # print(timer.stop())


if __name__ == '__main__':
    asyncio.run(main())
