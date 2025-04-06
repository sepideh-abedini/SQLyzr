import pandas as pd
import tqdm
import tqdm
import seaborn as sns
from matplotlib import pyplot as plt
from natsort import natsorted

from scripts.chart_lib.drawer import Drawer, COL_NAMES, proc_df
from src.util.multi_thread_utils import exec_multi_process

from src.cat.categories import CAT_6, CAT_5, CAT_4, CAT_1, CAT_3
from src.cat.catter import Catter
from src.util.file_utils import read_json

# sql = "SELECT * FROM bar"
# sql = "SELECT T1.engineer_id, T1.first_name, T1.last_name FROM Maintenance_Engineers AS T1 JOIN Engineer_Visits AS T2;"
# sql = "SELECT name FROM students WHERE EXISTS (SELECT 1 FROM enrollments WHERE enrollments.student_id = students.id AND enrollments.course = 'Math');"


# catter = Catter()
# data = read_json("charts/all.json")

# rows = []
# for row in tqdm.tqdm(data, total=len(data)):
#     sql = row['query']
#     cat, sub_cat = catter.categorize(sql)
#     rows.append({'cat': cat, 'sub_cat': sub_cat, 'sql': sql})
# df = pd.DataFrame(rows)
# df.to_csv("charts/all_cats.csv")
# cat, subcat = catter.categorize(sql)
# df['cat'] = df['sub_cat'].map(lambda x: data_dict[x]['cat'] if x in data_dict else df['cat'])

df = pd.read_csv("charts/all_cats.csv")
sub_cats = natsorted(df['sub_cat'].unique())
df['sub_cat'] = pd.Categorical(df['sub_cat'], categories=sub_cats, ordered=True)
group = df.drop(columns=["cat"]).groupby("sub_cat").count()
print(group)
plt.figure(figsize=(20, 5))
sns.countplot(df, x="sub_cat")
plt.show()
