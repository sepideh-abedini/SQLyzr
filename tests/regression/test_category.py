from src.cat.categorizer import Categorizer
from src.cat.tag_extractor import TagExtractor
from src.sql_parser.parser import SqlParser
import pytest

TEST_DATA = [
    ("c1", "SELECT cows FROM farm"),
    ("c2", "SELECT cows, total_horses FROM farm"),
    ("c2", "SELECT customer_name, order_id FROM customers, orders"),
    ("c2", "SELECT Official_Name FROM city ORDER BY Population DESC"),
    ("c3", "SELECT count(*) FROM head WHERE age > 56"),
    ("c3", "SELECT date, max_temperature_f - min_temperature_f FROM weather"),
    ("c3", "SELECT Publisher FROM publication LIMIT 1"),
    ("c3", "SELECT DISTINCT start_station_name FROM trip"),
    ("c3", "SELECT Publisher, COUNT(*) FROM publication GROUP BY Publisher"),
    ("c3",
     "SELECT T1.engineer_id, T1.first_name, T1.last_name FROM Maintenance_Engineers AS T1 JOIN Engineer_Visits AS T2"),
    ("c4", "SELECT campus FROM campuses WHERE LOCATION = 'Northridge' AND county = 'Los Angeles'"),
    ("c4", "SELECT date FROM weather WHERE mean_sea_level_pressure_inches BETWEEN 30.3 AND 31"),
    ("c4", "SELECT T2.name FROM Flight AS T1 JOIN Aircraft AS T2 WHERE T1.flno = 99"),
    ("c4", "SELECT dept_name, AVG (salary) FROM instructor WHERE salary > 42000 GROUP BY dept_name"),
    ("c4", "SELECT t2.customer_details FROM policies AS t1 JOIN customers AS t2 GROUP BY t2.customer_details"),
    ("c4", "SELECT policy_type_code FROM policies GROUP BY policy_type_code HAVING count(*) > 2"),
    ("c4", "SELECT name, course_id FROM instructor AS T1 JOIN teaches AS T2 ON T1.ID = T2.ID"),
    ("c4", "SELECT customer_details FROM customers UNION SELECT staff_details FROM staff"),
    ("c5",
     "SELECT border FROM border_info WHERE state_name IN (SELECT border FROM border_info WHERE state_name = 'florida')"),
    ("c6",
     "SELECT count(*), District FROM city WHERE Population > (SELECT avg(Population) FROM city) GROUP BY District"),
    ("c6",
     "SELECT avg(grade) FROM Highschooler WHERE id IN (SELECT T1.student_id FROM Friend AS T1 JOIN Highschooler AS T2)"),
    ("c6",
     "SELECT name FROM scientists EXCEPT SELECT name FROM scientists WHERE hours = (SELECT max(hours) FROM projects)")
]


@pytest.mark.parametrize("expected_cat,sql", TEST_DATA)
def test_categorizer(expected_cat, sql):
    parser = SqlParser()
    ast = parser.parse(sql)
    tag_extractor = TagExtractor()
    categorizer = Categorizer()
    tags = tag_extractor.extract_tags(ast)
    print(tags)
    cat = categorizer.get_category(tags.tag_set)
    assert cat == expected_cat


def test_tags():
    sql = "SELECT publisher, COUNT(*) FROM publication GROUP BY publisher"
    parser = SqlParser()
    ast = parser.parse(sql)
    tag_extractor = TagExtractor()
    tags = tag_extractor.extract_tags(ast)
    print(tags)
