 - ### 当当网书籍信息爬取

  

	 - 本项目使用了Scrapy爬虫框架    
	 - 使用LinkExtractor链接提取器    
 	 - 增加了链接去重   
    - 对网页到的空数据进行了补充(并没有删除掉空数据，而是添加了其他内容覆盖掉空数据)

   #### 使用步骤

   1. 首先在搜索框中输入你想要获取的的书籍(如果不需要更改,请跳过步骤1,2,3)
   ![当当网](/img/dangdang.png)
   2. 进入搜索页,选中下面图片的位置，复制a标签的href链接(只复制从key到index=)例如		          key=%CA%E9&act=input&page_index=
   ![当当网](/img/dangdang02.png)
   3. 打开项目文件中的dangdangwang.py文件，把画红色红色的地方替换成你复制的链接(和上一布      的格式一样)
   ![当当网](/img/dangdang03.png)
   4. 创建MySQL数据库,和项目中pipelines.py文件的名称一样,数据类型都是text类型,将数据库信息          换成你自己的信息
   5. 更改完成之后，运行main.py文件，效果如下
   ![当当网](/img/dangdang04.png)
