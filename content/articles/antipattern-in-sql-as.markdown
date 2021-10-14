title: SQL 反模式读书笔记-AS
date: 2013-1-11
category: readings
tags: antipattern, sql
slug: antipattern-sql-as
author: tonychow
summary: 

P16

    :::sql
    SELECT c.product_id, COUNT(*) AS products_per_account
    FROM Contacts
    GROUP BY account_id

其中 Contacts 表是 Products 表和 Accounts 表的中间表，这个 SQL 查询语句的作用是查询每个账号相关的产品数量。

    :::sql
    SELECT c.product_id, c.accounts_per_product
    FROM (
        SELECT product_id, COUNT(*) AS accounts_per_product
        FROM Contacts
        GROUP BY product_id
    ) AS c
    HAVING c.accounts_per_product = MAX(c.accounts_per_product)

这个 SQL 查询语句的作用是查询相关账号最多的产品。在这两个查询语句中我注意到的是 accounts_per_product 和 products_per_account 这两个本来不存在的字段。很明显这两个是通过 AS 得到的字段。AS 也就是 Alias (别名)，通过 Alias 可以方便组织多表查询特别是在涉及到自身对应自身表的时候，比如评论表如果想要父级和子级的结果查询，同时也可以用 Alias 给表的字段起一个别名，便于输出，比如上面的两个 SQL 查询。

第一个 SQL 查询语句中，通过将 c.product_id，COUNT(*) 这个要查询的字段 alias 成 products_per_account，这样输出的结果类似于：

    :::sql
    products_per_account
    7

就很容易阅读了。

第二个 SQL 查询语句中

    :::sql
    SELECT product_id, COUNT(*) AS accounts_per_product
    FROM Contacts
    GROUP BY product_id

这样一段查询得到结果集合被 alias 成了 c ，此外其中也将根据 product_id 查询得到的 products 数量 alias 成了 accounts_per_product，所以 c 这个集合中也多了一个字段 accounts_per_product，通过这样的处理，想要得到关联账号最多的产品的 product_id 就简单得好像以下：

    :::sql
    SELECT product_id, accounts_per_product
    FROM c 
    HAVING accounts_per_product = MAX(accounts_per_product)

这个查询语句通过 AS，写得相当优雅，易懂。
