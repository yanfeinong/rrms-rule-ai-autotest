# 文本规则输入（自然语言粘贴）

按以下格式粘贴一条或多条规则，`parse` 会优先读取本文件：

规则ID：R1001
执行规则ID：4ade39c90f7b96c1f669eb91a98d6c66
规则名：非空判定（组合）
表达式：IsNotNullComb(product_name,sku_code)=1
说明：这里空值指 空 或 字符串空；对于 null 或 NULL 不算空值；大小写敏感。

规则ID：R1002
规则名：不全相同判定
表达式：IsNotAllTheSame(pay_channel)=1
说明：字段不允许全部数据相同；大小写敏感。

可选项（如果你已知对象可以提供，不提供也可自动生成）：
- 对象示例：`对象：rrms_db.table_name.field_a,field_b`
