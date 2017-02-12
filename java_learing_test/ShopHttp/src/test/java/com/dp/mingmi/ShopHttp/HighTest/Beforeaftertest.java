package com.dp.mingmi.ShopHttp.HighTest;

import org.testng.annotations.*;

/**
 * Created by zhangmingmi on 16/8/16.
 */
public class Beforeaftertest {

    @BeforeMethod
    public void beforemethod() {
        System.out.println("BeforeMethod操作");
    }
    @BeforeTest
         public void beforetest() {
        System.out.println("BeforeTest操作");
    }
    @BeforeClass
    public void beforeclass() {
        System.out.println("Beforeclass操作");
    }

    @Test
    public void test1() {
        String str = "TestAdd";
        System.out.println("testing test1");
    }
    @Test
    public void test2() {
        System.out.println("testing test2");
    }

    @AfterTest
    public void aftertest() {
        System.out.println("After" +
                "Test操作");
    }
    @AfterClass
    public void afterclass() {
        System.out.println("After class操作");
    }

    @AfterMethod
    public void aftermethod() {
        System.out.println("After Method操作");
    }
}
