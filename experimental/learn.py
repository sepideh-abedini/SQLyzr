import matplotlib.pyplot as plt
from sklearn.feature_selection import RFE
from sklearn.model_selection import train_test_split
from sklearn.tree import DecisionTreeClassifier, plot_tree

from src.util.file_utils import load_csv

features_df = load_csv('exprs/features.num.csv')
features_df = features_df.drop(['id'], axis=1)
features = features_df.columns.values
X = features_df.values.tolist()

eval_df = load_csv('exprs/eval.csv')
s = eval_df['eval']
y = s.values.astype(int).tolist()

# X, _ = make_classification(n_samples=len(y), n_features=len(features))
print(sum(y))

rfe = RFE(estimator=DecisionTreeClassifier(), n_features_to_select=3)
rfe.fit(X, y)

features = rfe.get_feature_names_out(features)
print(features)

X = rfe.transform(X)
X_train, X_test, y_train, y_test = train_test_split(X, y)
model = DecisionTreeClassifier(max_depth=5)
model.fit(X_train, y_train)
print(model.score(X_test, y_test))

plt.figure(figsize=(25, 25))
plot_tree(model, filled=True, feature_names=features, fontsize=12)
# plt.show()

# pipeline = Pipeline(steps=[('s', rfe), ('m', model)])
# # evaluate model
# cv = RepeatedStratifiedKFold(n_splits=10, n_repeats=3, random_state=1)
# n_scores = cross_val_score(pipeline, X, y, scoring='accuracy', cv=cv, n_jobs=-1, error_score='raise')
# print(rfe.get_feature_names_out(features))
# # report performance
# print('Accuracy: %.3f (%.3f)' % (mean(n_scores), std(n_scores)))

# clf = tree.DecisionTreeClassifier()
# clf.score()
# clf = tree.DecisionTreeClassifier(max_depth=3)
# scores = cross_val_score(clf, X, y, cv=20)
# print(scores)
# clf = clf.fit(X_train, y_train)
# print(clf.score(X_test, y_test))

# dot_data = tree.export_graphviz(clf,
#                      feature_names=features,
#                      out_file=None,
#                      filled=True,
#                      rounded=True)
# pydot_graph = pydotplus.graph_from_dot_data(dot_data)
# pydot_graph.write_pdf('tree.pdf')

# plt.figure(figsize=(25, 25))
# tree.plot_tree(clf, filled=True, feature_names=features, fontsize=12)
# plt.show()
