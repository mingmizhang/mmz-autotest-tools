package com.dp.mingmi.pigeontest;

/**
 * Created by zhangmingmi on 16/8/25.
 */
import com.dianping.pigeon.remoting.ServiceFactory;
import com.dp.arts.client.SearchService;

import java.io.BufferedReader;
import java.io.File;
import java.io.FileReader;
import java.io.IOException;
import java.util.ArrayList;
import java.util.List;
import java.util.concurrent.CountDownLatch;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;


/**
 * Created by zhangmingmi on 16/8/24.
 */
public class RequestGenerate {
    public List<String> read_file_to_list(String filename) {
        File file = new File(filename);
        List<String> list = new ArrayList<String>();
        BufferedReader reader = null;
        try {
            //System.out.println("以行为单位读取文件内容，一次读一整行：");
            reader = new BufferedReader(new FileReader(file));
            String tempString = null;
            int line = 1;
            // 一次读入一行，直到读入null为文件结束
            while ((tempString = reader.readLine()) != null) {
                // 显示行号
                //System.out.println("line " + line + ": " + tempString);
                list.add(tempString);
                line++;
            }
            reader.close();
        } catch (IOException e) {
            e.printStackTrace();
        } finally {
            if (reader != null) {
                try {
                    reader.close();
                } catch (IOException e1) {
                    e1.printStackTrace();
                }
            }
            return list;
        }
    }

    //    public static void main(String[] args) {
//        RequestParser request = new RequestParser();
//        List<String> query_list = new ArrayList<String>();
//        RequestGenerate requestGenerate = new RequestGenerate();
//        query_list = requestGenerate.read_file_to_list("/Users/zhangmingmi/Desktop/query.log");
//        for (int i = 0; i < query_list.size(); i++) {
//            Request req = request.parse(query_list.get(i));
//            SearchService searchService = ServiceFactory.getService("search.arts.shop", SearchService.class, 20000);
//            Response response = searchService.search(req);
//            System.out.println("The request status is : "+response.getStatus());
//        }
//    }
    public static void main(String[] args) throws InterruptedException {
        String filename = args[0];//"/Users/zhangmingmi/Desktop/query.log";
        int Thread_number = Integer.parseInt(args[1]);
        int loop_time = Integer.parseInt(args[2]);
        String bizname = args[3];
        //SearchService searchService = ServiceFactory.getService("search.arts.shop", SearchService.class, 20000);
        SearchService searchService = ServiceFactory.getService(bizname, SearchService.class, 20000);
        List<String> query_list = new ArrayList<String>();
        RequestGenerate requestGenerate = new RequestGenerate();
        //用于等待线程全部完成工作结束后退出的标志
        CountDownLatch countDownLatch = new CountDownLatch(Thread_number);
        query_list = requestGenerate.read_file_to_list(filename);
        SendRequest multisend = new SendRequest(query_list,searchService,countDownLatch,loop_time);
        ExecutorService fixedThreadPool = Executors.newFixedThreadPool(Thread_number);
        for (int i = 0; i < Thread_number; i++) {
            System.out.print("the thread " + i + "\n");
            fixedThreadPool.execute(multisend);
        }
        fixedThreadPool.shutdown();
        countDownLatch.await();
        System.exit(0);
    }


}

