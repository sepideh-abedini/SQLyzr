SELECT e.name
FROM (SELECT e.name, o.city
      FROM employees e
               JOIN offices o
                    ON e.office_id = o.id) subquery
WHERE subquery.city = 'London';