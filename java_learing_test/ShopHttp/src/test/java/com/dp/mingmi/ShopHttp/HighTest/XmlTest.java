package com.dp.mingmi.ShopHttp.HighTest;

import org.testng.Reporter;
import org.testng.annotations.Test;
import org.testng.Assert;
import org.testng.annotations.DataProvider;

/**
 * Created by zhangmingmi on 16/8/1.
 */
public class XmlTest {
    @Test(dataProvider = "testData",groups = {"p0"},priority = 1 )
    public void doTest(String testName, int a, int b, int expected) {
        System.out.println(testName);
        Assert.assertEquals(a + b, expected);
    }

    @Test(groups = {"p1"},priority = 3 )
    public void GroupTest() {
        Reporter.log("测试开始");
        System.out.print("grouptest");
        //System.out.println(testName);
        Assert.assertEquals(3 + 4, 7);
        Reporter.log("Pass");
    }

    @Test(groups = {"p1","p0"},priority = 2 )
    public void GroupTest2() {
        Reporter.log("测试开始");
        System.out.print("grouptest2");
        //System.out.println(testName);
        Assert.assertEquals(2 + 5, 7);
        Reporter.log("Pass");
    }

    @DataProvider
    public Object[][] testData() {
        return new Object[][]{
                {"testXml1", 1, 2, 3},
                {"testXml2", 2, 8, 10},
                {"testXml3", 3, 4, 7}};
    }
}
