import asyncio
import os
import os

import psutil
from loguru import logger

from src.configs.datasets import BIRD_SMALL
from src.eval.lib import Timer
from src.eval.metrics import ExecAcc, GoldNotEmpty
from src.parse.parser import SqlParser
from src.rel.base_matcher import SubsetMatcher
from src.rel.db_facade import DatabaseFacade
from src.rel.result_transformer import IgnoreListOrderTransformer, IgnoreColOrderTransformer
from src.rel.sql_data import SqlInputData
from src.rel.sql_transformer import AddLimitTransformer, LiteralCorrectorTransformer, \
    ColCorrectorTransformer
from src.rel.transformer_detector import TransformerDetector


async def main():
    conf = BIRD_SMALL
    db_id = "card_games"
    sql = "SELECT T1.id FROM cards AS T1 INNER JOIN rulings AS T2 ON T1.uuid = T2.uuid INNER JOIN legalities AS T3 ON T1.uuid = T3.uuid WHERE T3.status = 'Legal' AND T1.types = 'Creature'"
    facade = DatabaseFacade(conf.get_db_path())
    for i in range(10):
        timer = Timer.start()
        await facade.exec_query_async(db_id, sql)
        print(timer.lap())


if __name__ == '__main__':
    asyncio.run(main())


exit(0)

# 2740434
# db_id = "csail_stata_nova"
sql = """
SELECT s
FROM (SELECT instances.created_at AS instances_created_at, instances.updated_at AS instances_updated_at, instances.deleted_at AS instances_deleted_at, instances.deleted AS instances_deleted, instances.id AS instances_id, instances.user_id AS instances_user_id, instances.project_id AS instances_project_id, instances.image_ref AS instances_image_ref, instances.kernel_id AS instances_kernel_id, instances.ramdisk_id AS instances_ramdisk_id, instances.hostname AS instances_hostname, instances.launch_index AS instances_launch_index, instances.key_name AS instances_key_name, instances.key_data AS instances_key_data, instances.power_state AS instances_power_state, instances.vm_state AS instances_vm_state, instances.task_state AS instances_task_state, instances.memory_mb AS instances_memory_mb, instances.vcpus AS instances_vcpus, instances.root_gb AS instances_root_gb, instances.ephemeral_gb AS instances_ephemeral_gb, instances.ephemeral_key_uuid AS instances_ephemeral_key_uuid, instances.host AS instances_host, instances.node AS instances_node, instances.instance_type_id AS instances_instance_type_id, instances.user_data AS instances_user_data, instances.reservation_id AS instances_reservation_id, instances.launched_at AS instances_launched_at, instances.terminated_at AS instances_terminated_at, instances.availability_zone AS instances_availability_zone, instances.display_name AS instances_display_name, instances.display_description AS instances_display_description, instances.launched_on AS instances_launched_on, instances.locked AS instances_locked, instances.locked_by AS instances_locked_by, instances.os_type AS instances_os_type, instances.architecture AS instances_architecture, instances.vm_mode AS instances_vm_mode, instances.uuid AS instances_uuid, instances.root_device_name AS instances_root_device_name, instances.default_ephemeral_device AS instances_default_ephemeral_device, instances.default_swap_device AS instances_default_swap_device, instances.config_drive AS instances_config_drive, instances.access_ip_v4 AS instances_access_ip_v4, instances.access_ip_v6 AS instances_access_ip_v6, instances.auto_disk_config AS instances_auto_disk_config, instances.progress AS instances_progress, instances.shutdown_terminate AS instances_shutdown_terminate, instances.disable_terminate AS instances_disable_terminate, instances.cell_name AS instances_cell_name, instances.internal_id AS instances_internal_id, instances.cleaned AS instances_cleaned
FROM instances
WHERE instances.deleted = 0 AND (instances.vm_state != 'soft-delete' OR instances.vm_state IS NULL) AND instances.project_id = 'bfd50153a2e9476f93e33e30e922cd06' AND (instances.display_name REGEXP 'void') ORDER BY instances.created_at DESC, instances.id DESC
LIMIT 3000) AS anon_1 LEFT OUTER JOIN (security_group_instance_association AS security_group_instance_association_1 INNER JOIN security_groups AS security_groups_1 ON security_groups_1.id = security_group_instance_association_1.security_group_id AND security_group_instance_association_1.deleted = 0 AND security_groups_1.deleted = 0) ON security_group_instance_association_1.instance_uuid = anon_1.instances_uuid AND anon_1.instances_deleted = 0 LEFT OUTER JOIN instance_info_caches AS instance_info_caches_1 ON instance_info_caches_1.instance_uuid = anon_1.instances_uuid ORDER BY anon_1.instances_created_at DESC, anon_1.instances_id DESC
"""

parser.parse(sql)

exit(0)

gold_str = "SELECT LOCATION ,  name FROM stadium WHERE capacity BETWEEN 5000 AND 10000"
pred_str = "SELECT Location, Name FROM stadium WHERE Capacity BETWEEN 5000 AND 10000;"


async def main():
    db_id = "concert_singer"
    ea = ExecAcc("ea", SPIDER_DEV)
    gne = GoldNotEmpty("gne", SPIDER_DEV)
    detector = TransformerDetector(SPIDER_DEV, [
        AddLimitTransformer(),
        LiteralCorrectorTransformer(),
        ColCorrectorTransformer(),
        IgnoreListOrderTransformer(),
        IgnoreColOrderTransformer(),
        SubsetMatcher()
    ])
    pred = SqlInputData(db_id, pred_str)
    gold = SqlInputData(db_id, gold_str)
    working_sub = await detector.find_working_sub_sync(pred, gold)
    rea_score = calc_rea_score(working_sub, DIN_SPIDER_DEV_EVAL)
    ea_score = await ea.calc(gold_str, pred_str, db_id)
    gold_is_empty = 1 - await gne.calc(gold_str, pred_str, db_id)
    print(rea_score)
    print(ea_score)
    print(gold_is_empty)


if __name__ == '__main__':
    asyncio.run(main())
    exit(0)
# Initialize the progress bar
spinner = PixelSpinner('Loading ')
for i in range(20):
    # Do some work
    time.sleep(2.1)
    spinner.next()
print("salam")

exit(0)
# a CPU-bound task
bar = {}
n = 1 * (10 ** 6)
for i in range(n):
    bar[i] = i * i
for i in range(n):
    bar[i] += 1
# for i in range(n):
#     print(bar[i])
pu = ProcessUsage()
pu.dump("usage.json")
usage = getrusage(RUSAGE_SELF)


def memory_usage_psutil():
    # return the memory usage in MB
    process = psutil.Process(os.getpid())
    print(process.cpu_times())
    print(process.memory_info())
    print(process.threads())
    process.cpu_times()
    mem = process.memory_info()[0] / float(2 ** 20)
    return mem


print("Memory: ", memory_usage_psutil())

# print(usage)
# print("Shared memory: ", usage.ru_ixrss)
# print("Unshared: ", usage.ru_idrss)
# print("Stack: ", usage.ru_isrss)
#
exit(0)

# catter = Catter()
#
# sql = "SELECT T1.`School Name`, T2.Street, T2.City, T2.State, T2.Zip FROM frpm AS T1 INNER JOIN schools AS T2 ON T1.CDSCode = T2.CDSCode WHERE T2.County = 'Monterey' AND T1.`Free Meal Count (Ages 5-17)` > 800 AND T1.`School Type` = 'High Schools (Public)'"
# sql = "SELECT T2.School, T1.AvgScrWrite, T2.Phone FROM schools AS T2 LEFT JOIN satscores AS T1 ON T2.CDSCode = T1.cds WHERE strftime('%Y', T2.OpenDate) > '1991' OR strftime('%Y', T2.ClosedDate) < '2000'"
# sql = "SELECT x FROM schools WHERE strftime('%Y', T2.OpenDate) > '1991'"
sql = "SELECT count(*) FROM bar WHERE (SELECT bar from baz where (SELECT mar from maz where (SELECT x from nar))) UNION SELECT foo from Baz"
sql = "SELECT e.name, d.department_name, p.project_name, c.client_name FROM employees AS e JOIN departments AS d ON e.department_id = d.department_id JOIN projects AS p ON e.project_id = p.project_id JOIN clients AS c ON p.client_id = c.client_id"
sql = "SELECT name FROM students WHERE EXISTS (SELECT 1 FROM enrollments WHERE enrollments.student_id = students.id AND enrollments.course = 'Math')"
sql = "SELECT name FROM employees WHERE department IN (SELECT department FROM managers WHERE location = 'Toronto');"
sql = "SELECT name FROM employees WHERE department IN (SELECT department FROM managers WHERE location = 'Toronto');"
sql = "SELECT name, salary, RANK() OVER (PARTITION BY department ORDER BY salary DESC) AS dept_rank FROM employees;"
# sql = "WITH RECURSIVE DeptHierarchy AS (SELECT id, name, parent_dept FROM departments WHERE parent_dept IS NULL UNION ALL SELECT d.id, d.name, d.parent_dept FROM departments d JOIN DeptHierarchy dh ON d.parent_dept = dh.id) SELECT * FROM DeptHierarchy;"
sql = "WITH RECURSIVE DeptHierarchy AS (SELECT id FROM departments) SELECT * FROM DeptHierarchy"
sql = "WITH RECURSIVE DeptHierarchy AS (SELECT id, name, parent_dept FROM departments WHERE parent_dept IS NULL UNION ALL SELECT d.id, d.name, d.parent_dept FROM departments d JOIN DeptHierarchy dh ON d.parent_dept = dh.id) SELECT * FROM DeptHierarchy;"
sql = "SELECT T1.engineer_id, T1.first_name, T1.last_name FROM Maintenance_Engineers AS T1 JOIN Engineer_Visits AS T2;"
sql = "SELECT T1.engineer_id, T1.first_name, T1.last_name FROM Maintenance_Engineers AS T1 JOIN Engineer_Visits AS T2;"
sql = "SELECT e.employee_name, p.position_title FROM employees AS e JOIN positions AS p ON e.salary > p.min_salary AND e.salary < p.max_salary"
sql, cat = ("SELECT Publisher FROM publication GROUP BY Publisher", "s9")
sql, cat = (
    "SELECT T1.engineer_id, T1.first_name, T1.last_name FROM Maintenance_Engineers AS T1 JOIN Engineer_Visits AS T2",
    "s10")

sql, cat = ("SELECT date FROM weather WHERE mean_sea_level_pressure_inches BETWEEN 30.3 AND 31", "s12")
sql, cat = ("SELECT name FROM employees WHERE name LIKE 'J%'", "s17")
sql, cat = (
    "SELECT c.customer_name  FROM Customers c JOIN Orders o ON c.customer_id = o.customer_id  WHERE o.order_id IS NULL",
    "s18")
sql, cat = (
    "SELECT border FROM border_info WHERE state_name = (SELECT border FROM border_info WHERE state_name = 'florida')",
    "s20")
sql, cat = (
    "SELECT name FROM students WHERE EXISTS (SELECT 1 FROM enrollments WHERE enrollments.student_id = students.id AND enrollments.course = 'Math')",
    "s23")
sql, cat = (
    "SELECT name, salary, CASE WHEN salary >= 70000 THEN 'High Salary' WHEN salary >= 50000 THEN 'Medium Salary' ELSE 'Low Salary' END AS salary_category FROM Employees",
    "s32")
sql, cat = (
    "SELECT e.employee_name, d.department_name FROM employees AS e LEFT JOIN departments AS d ON e.department_id = d.department_id;",
    "s25")

# sql = "SELECT cows FROM farm WHERE x + 2 > y"
# sql = "SELECT COUNT(*) FROM lists WHERE SUBSTR(list_update_timestamp_utc, 1, 4) - SUBSTR(list_creation_timestamp_utc, 1, 4) > 10"

# pred_str = "SELECT name from singer LIMIT 3"
# gold_str = "SELECT name from singer LIMIT 2"
# db_id = "concert_singer"
#
# detector = TransformerDetector(SPIDER_DEV, [
#     LimitRemoverTransformer(),
# AddLimitTransformer(),
# LiteralCorrectorTransformer(),
# ColCorrectorTransformer(),
# IgnoreListOrderTransformer(),
# IgnoreColOrderTransformer(),
# SubsetMatcher()
# ])
#
# pred = SqlInputData(db_id, pred_str)
# gold = SqlInputData(db_id, gold_str)
# db_facade = DatabaseFacade(SPIDER_DEV.get_db_path())
# res = db_facade.exec_query_sync(db_id, gold_str)
# print(res)
# working_sub = asyncio.run(detector.find_working_sub_sync(pred, gold))
# print(working_sub)


# sql = "SELECT DISTINCT LIBRARY_COURSE_INSTRUCTOR.instructor_name, LIBRARY_SUBJECT_OFFERED.subject_title, COUNT(LIBRARY_RESERVE_CATALOG.catalog_isbn) OVER (PARTITION BY LIBRARY_COURSE_INSTRUCTOR.LIBRARY_COURSE_INSTRUCTOR_KEY, LIBRARY_SUBJECT_OFFERED.LIBRARY_SUBJECT_OFFERED_KEY) FROM LIBRARY_COURSE_INSTRUCTOR JOIN LIBRARY_RESERVE_MATRL_DETAIL ON LIBRARY_COURSE_INSTRUCTOR.LIBRARY_COURSE_INSTRUCTOR_KEY = LIBRARY_RESERVE_MATRL_DETAIL.LIBRARY_COURSE_INSTRUCTOR_KEY JOIN LIBRARY_SUBJECT_OFFERED ON LIBRARY_SUBJECT_OFFERED.LIBRARY_SUBJECT_OFFERED_KEY = LIBRARY_RESERVE_MATRL_DETAIL.LIBRARY_SUBJECT_OFFERED_KEY JOIN LIBRARY_RESERVE_CATALOG ON LIBRARY_RESERVE_CATALOG.LIBRARY_RESERVE_CATALOG_KEY = LIBRARY_RESERVE_MATRL_DETAIL.LIBRARY_RESERVE_CATALOG_KEY;"
sql = "SELECT SUM(ROOM_SQUARE_FOOTAGE) OVER (PARTITION BY BUILDING_COMPONENT) FROM SPACE_DETAIL"
sql = "SELECT COUNT(LIBRARY_RESERVE_CATALOG.catalog_isbn) OVER (PARTITION BY LIBRARY_COURSE_INSTRUCTOR.LIBRARY_COURSE_INSTRUCTOR_KEY, LIBRARY_SUBJECT_OFFERED.LIBRARY_SUBJECT_OFFERED_KEY) FROM LIBRARY_COURSE_INSTRUCTOR JOIN LIBRARY_RESERVE_MATRL_DETAIL ON LIBRARY_COURSE_INSTRUCTOR.LIBRARY_COURSE_INSTRUCTOR_KEY = LIBRARY_RESERVE_MATRL_DETAIL.LIBRARY_COURSE_INSTRUCTOR_KEY JOIN LIBRARY_SUBJECT_OFFERED ON LIBRARY_SUBJECT_OFFERED.LIBRARY_SUBJECT_OFFERED_KEY = LIBRARY_RESERVE_MATRL_DETAIL.LIBRARY_SUBJECT_OFFERED_KEY JOIN LIBRARY_RESERVE_CATALOG ON LIBRARY_RESERVE_CATALOG.LIBRARY_RESERVE_CATALOG_KEY = LIBRARY_RESERVE_MATRL_DETAIL.LIBRARY_RESERVE_CATALOG_KEY"
sql = "SELECT COUNT(distinct employee_directory.MIT_ID) OVER (PARTITION BY a.BUILDING_NAME_LONG, a.year_built) as num_employees FROM BAR"
sql = "SELECT at.TERM_CODE, at.TERM_DESCRIPTION, at.IS_CURRENT_TERM2, COUNT(distinct at.SUBJECT_ID) AS Total_SUBJECTS FROM (SELECT at.*, SUBJECT_ID, CASE WHEN at.ACADEMIC_YEAR = EXTRACT(YEAR FROM SYSDATE) AND atp.IS_CURRENT_TERM = 'Y' THEN 'Y' ELSE 'N' END as IS_CURRENT_TERM2 FROM (SELECT ACADEMIC_TERMS_ALL.*, CASE WHEN TERM_CODE LIKE '%FA' THEN 'Y' END AS A ,CASE WHEN TERM_CODE LIKE '%JA' THEN 'Y' END AS B,CASE WHEN TERM_CODE LIKE '%SP' THEN 'Y' END AS C,CASE WHEN TERM_CODE LIKE '%SU' THEN 'Y' END AS D FROM ACADEMIC_TERMS_ALL) at LEFT OUTER JOIN ACADEMIC_TERM_PARAMETER atp ON at.TERM_CODE = atp.TERM_CODE LEFT OUTER JOIN CIS_COURSE_CATALOG ccc ON ccc.ACADEMIC_YEAR = at.ACADEMIC_YEAR AND (IS_OFFERED_FALL_TERM = at.A OR IS_OFFERED_IAP = at.B OR IS_OFFERED_SPRING_TERM = at.C OR IS_OFFERED_SPRING_TERM = at.C OR IS_OFFERED_SUMMER_TERM = at.D)) at GROUP BY at.TERM_CODE, at.TERM_DESCRIPTION, at.IS_CURRENT_TERM2;"
sql = "SELECT at.TERM_DESCRIPTION, at.IS_CURRENT_TERM, COUNT(distinct tso.COURSE_NUMBER) AS Total_Courses, COUNT(DISTINCT tm.isbn) AS Total_materials, MIN(tso.NUM_ENROLLED_STUDENTS) AS Min_Enrolled_Students, MAX(tso.NUM_ENROLLED_STUDENTS) AS Max_Enrolled_Students, COUNT(DISTINCT OFFER_SCHOOL_NAME) AS Total_Num_Schools FROM ACADEMIC_TERMS_ALL at LEFT OUTER JOIN TIP_SUBJECT_OFFERED tso ON at.TERM_CODE = tso.TERM_CODE JOIN TIP_DETAIL td ON td.TIP_SUBJECT_OFFERED_KEY = tso.TIP_SUBJECT_OFFERED_KEY JOIN TIP_MATERIAL tm ON td.TIP_MATERIAL_KEY = tm.TIP_MATERIAL_KEY JOIN TIP_MATERIAL_STATUS tms ON td.TIP_MATERIAL_STATUS_KEY = tms.TIP_MATERIAL_STATUS_KEY GROUP BY at.TERM_CODE, at.TERM_DESCRIPTION, at.IS_CURRENT_TERM;"
parser = SqlParser()
ast = parser.parse(sql)
catter = Catter()
print(ast is not None)


# print(catter.get_category(sql))
# draw_graph(ast, "out.png")


# tagger = TagExtractor()
# collector = StructureType.Collector()
# tags = tagger.extract_tags(ast)
# categorizer = Categorizer()
#
# for t in tags.tag_set.tags:
#     print(t.name)
#
# ast.accept(collector)
# print(collector.max_level)
# s = categorizer.get_sub_category(tags.tag_set)
# print(s)
#

# assert categorizer.get_sub_category(tags).name == cat


# parser = SqlParser()
# draw_graph(parser.parse(sql), "graph.png")
#
# cat = catter.get_category(sql)
# print(cat)


async def main():
    pass
    # bar = GptBatchClient()
    # timer = Timer()
    # timer.start()
    # bar.list_cur_batches()
    # print(timer.stop().seconds)
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
