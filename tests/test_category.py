import pytest

from src.cat.catter import Catter
from src.parse.parser import SqlParser


@pytest.mark.parametrize("sql, expected_sub_cat", [
    ("SELECT cows, total_horses FROM farm", "s1"),
    ("SELECT * FROM farm", "s2"),
    ("SELECT Official_Name FROM city ORDER BY Population DESC", "s3"),
    ("SELECT * FROM head WHERE age > 56", "s4"),
    ("SELECT date, max_temperature_f - min_temperature_f FROM weather", "s5"),
    ("SELECT AVG(price) FROM products", "s6"),
    ("SELECT Publisher FROM publication LIMIT 1", "s7"),
    ("SELECT DISTINCT start_station_name FROM trip", "s8"),
    ("SELECT Publisher FROM publication GROUP BY Publisher", "s9"),
    ("SELECT T1.engineer_id, T1.first_name, T1.last_name FROM Maintenance_Engineers AS T1 JOIN Engineer_Visits AS T2",
     "s10"),
    ("SELECT e.employee_name, d.department_name FROM employees AS e JOIN departments AS d ON e.department_id = d.department_id;",
     "s10"),
    (
            "SELECT e.employee_name, p.position_title FROM employees AS e JOIN positions AS p ON e.salary > p.min_salary AND e.salary < p.max_salary",
            "s11"),
    ("SELECT date FROM weather WHERE mean_sea_level_pressure_inches BETWEEN 30.3 AND 31", "s12"),
    ("SELECT T2.name FROM Flight AS T1 JOIN Aircraft AS T2 WHERE T1.flno = 99", "s13"),
    ("SELECT dept_name, AVG (salary) FROM instructor WHERE salary > 42000 GROUP BY dept_name", "s14"),
    ("SELECT t2.customer_details FROM policies AS t1 JOIN customers AS t2 GROUP BY t2.customer_details", "s15"),
    ("SELECT policy_type_code FROM policies GROUP BY policy_type_code HAVING count(*) > 2", "s16"),
    ("SELECT name FROM employees WHERE name LIKE 'J%'", "s17"),
    ("SELECT c.customer_name  FROM Customers c WHERE c.order_id IS NULL", "s18"),
    ("SELECT name, age FROM students WHERE age > 18 AND grade = 'A'", "s19"),
    ("SELECT border FROM border_info WHERE state_name = (SELECT border FROM border_info WHERE state_name = 'florida')",
     "s20"),
    ("SELECT name FROM employees WHERE department = 'Sales' UNION SELECT name FROM freelancers WHERE project = 'Sales'",
     "s21"),
    (
            "SELECT name FROM employees WHERE department IN (SELECT department FROM managers WHERE location = 'Toronto')",
            "s22"),
    # FIXME: ("SELECT name FROM students LEFT OUTER JOIN employees", "s22"),
    (
            "SELECT name FROM students INNER JOIN employees",
            "s23"
    ),
    (
            "SELECT name FROM students INNER JOIN employees ORDER BY age",
            "s24"
    ),
    (
            "SELECT name FROM students LEFT JOIN employees GROUP BY age",
            "s25"
    ),
    (
            "SELECT AVG(name) FROM students LEFT JOIN employees",
            "s26"
    ),
    (
            "SELECT name FROM students JOIN employees JOIN class JOIN university",
            "s27"
    ),
    (
            "SELECT department, salary FROM employees WHERE department IN (SELECT department FROM managers) GROUP BY department",
            "s28"),
    ("SELECT grade FROM Highschooler WHERE id IN (SELECT T1.student_id FROM Friend AS T1 JOIN Highschooler AS T2)",
     "s29"),
    (
            "SELECT AVG(salary) FROM employees WHERE department_id IN (SELECT department_id FROM departments WHERE location = 'NY')",
            "s30"),
    (
            "SELECT name FROM students WHERE id IN (SELECT student_id FROM courses WHERE course_id IN (SELECT id FROM courses WHERE course_name = 'Math'))",
            "s31"),
    (
            "SELECT employee_name FROM employees WHERE employee_id IN (SELECT manager_id  FROM departments WHERE department_id IN (SELECT department_id FROM projects WHERE client_id IN (SELECT client_id FROM clients WHERE client_name = 'ABC Corporation')))",
            "s34"),
    ("SELECT name FROM scientists EXCEPT SELECT name FROM scientists WHERE hours = (SELECT max(hours) FROM projects)",
     "s33"),
    (
            "SELECT name, salary, CASE WHEN salary >= 70000 THEN 'High Salary' WHEN salary >= 50000 THEN 'Medium Salary' ELSE 'Low Salary' END AS salary_category FROM Employees",
            "s32"),
    (
            "WITH RECURSIVE DeptHierarchy AS (SELECT id, name, parent_dept FROM departments WHERE parent_dept IS NULL ) SELECT * FROM DeptHierarchy",
            "s35"),
    ("SELECT name, salary, RANK() OVER (PARTITION BY department ORDER BY salary DESC) AS dept_rank FROM employees",
     "s36")
])
def test_exprs(sql, expected_sub_cat):
    parser = SqlParser()
    catter = Catter()
    cat, sub_cat = catter.categorize(sql)
    assert sub_cat.name == expected_sub_cat
    # tags = tagger.extract_tags(ast)
