执行步骤：
1. 利用mvn clean install进行项目打包
2. mvn assembly:assembly
3. java -jar pigeontest-1.0-SNAPSHOTcom-jar-with-dependencies.jar /Users/zhangmingmi/Desktop/query.log 2 3 search.arts.shop
   (jar包后面传入的三个参数：第一个是query所在的地方；第二个是启动的线程数；第三个是所有的query的循环次数;第4个是pigeon节点名)

PS:也可以直接在main函数修改，直接写入参数执行即可
