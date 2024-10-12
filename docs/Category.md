- [Category Assignment](#category-assignment)
  - [Tag Assignment](#tag-assignment)
    - [Tag Types](#tag-types)
    - [Ordered Tags](#ordered-tags)
    - [Unordered Tags](#unordered-tags)
    - [Collecting Tags](#collecting-tags)
    - [Tag Sets](#tag-sets)
  - [Categories](#categories)
    - [Ceategorizer!](#ceategorizer)

# Category Assignment

Category assignment includes two steps:

- Assigning tags to statements
- Assigning category based on the tags

## Tag Assignment

Let's start with an example.
Consider the following SQL:

```sql
SELECT publisher, COUNT(*)
FROM publication
GROUP BY publisher;
```

We assign the following tags to this statement:

```
UnconditionalGroup,MultiColumn,SingleTable
```

As you can see, each tag determines whether the
statement has some specific feature or not.

### Tag Types

Tags are partitioned into different types.
For instance, for the select clause we have
`SelectType` tags that include two tags: `SingleColumn`
and `MultiColumn`.

### Ordered Tags

We consider some features of SQL harder than others.
For instance, a `MultiColumn` SQL is considered harder
than a `SingleColumn` statement.
So, some tag types are defined as `OrderedTag` to indicate
that there is a total ordering among the tags of this type.
We say `t2 >= t1` if `t2` is a harder tag than `t1`.
For example, for `SelectType` we have `MultiColumn` > `SingleColumn`.

### Unordered Tags

Unordered tags has no ordering among them, so we have `t2 >= t1 `
iff `t2 == t1`.

### Collecting Tags

To collect tags for a given statement, we use a separate visitor
for each tag type and then use the union of all collected tags.

### Tag Sets

Let `s1` and `s2` be two tag sets.
We use the notion `s1 <= s2` to indicate that `s2` contains
tags that are at least as hard as the tags in `s1`.
Here are some examples:

```python
{SingleColumn} <= {MultiColumn}
{SingleColumn, MultiTable} <= {MultiColumn, MultiTable}
{SingleColumn} <= {SingleColumn, SingleTable}
```

As another example,
two sets `{SingleColumn, MultiTable}` and `{MultiColumn, SingleTable}`
are not comparable, so neither is harder than the other.

> Currently, we only allow ordering among tags of the same type.
> But, we can change this later to allow comparison of tags
> of different types 🤔.
> For instance, we might have `MultiTable` >= `MultiColumn`.

## Categories

We assume ordering among categories too.
So, for instance, category `c4` is considered harder than `c2`.

We specify each category using a set of tag sets as a matching rule.
Let's `ts` be the tag set of a given statement `s`.
We say `s` is included in category `c` if `ts` be at least as hard
as some tag set in `c`.
For instance consider the following category:

```python
c = {{MultiTable}, {SingleTable, MultiColumn}}
```

`ts = {MultiTable}` matches this category since there
is a tag set `{MultiTable}` such that `ts` is
at least hard as it.
But, `ts = {SingleTable, SingleColumn}` doesn't
match this category since it is not as least as
hard of neither `{MultiTable}` nor `{SingleTable, MultiColumn}`.

### Ceategorizer!

Having the specification of each category,
to find a category for a given statement,
we start from the hardest category and check if
it matches the statement.
Thus, we return the first category match we find
starting from the hardest category.





