package com.dp.mingmi.SendHttp;

import java.util.concurrent.Executors;
import java.util.concurrent.ScheduledExecutorService;
import java.util.concurrent.TimeUnit;

/**
 * Created by zhangmingmi on 16/8/22.
 */
public class Sendhttpscheduledpool {
    public static void main(String[] args) {
        Sendhttpmultithread multihttp = new Sendhttpmultithread("http://:4053/search/shop?query=term(cityid,2)");
        ScheduledExecutorService shceduledThreadPool = Executors.newScheduledThreadPool(3);
        for (int i = 0; i < 10; i++) {
            System.out.print("the thread "+i+"\n");
            shceduledThreadPool.schedule(multihttp, 3, TimeUnit.SECONDS); //后面加入了等待的时间参数
        }

    }
}
