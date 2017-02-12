package com.dp.mingmi.SendHttp;


import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;

/**
 * Created by zhangmingmi on 16/8/22.
 */
public class Sendhttpthreadpool {
    public static void main(String[] args) {
        Sendhttpmultithread multihttp = new Sendhttpmultithread("http://****:4053/search/shop?query=term(cityid,2)");
        ExecutorService fixedThreadPool = Executors.newFixedThreadPool(3);
        for (int i = 0; i < 10; i++) {
            System.out.print("the thread "+i+"\n");
            fixedThreadPool.execute(multihttp);
        }

    }
}
