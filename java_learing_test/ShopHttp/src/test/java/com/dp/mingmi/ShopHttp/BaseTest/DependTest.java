package com.dp.mingmi.ShopHttp.BaseTest;

import org.testng.Assert;
import org.testng.annotations.Test;

/**
 * Created by zhangmingmi on 16/8/16.
 */
public class DependTest {

    @Test
    public void Test1() {
        Assert.assertEquals(3 + 4, 7);
    }


    @Test(dependsOnMethods = {"Test1"})
    public void Test2() {
        Assert.assertEquals(2 + 3, 2);
    }


    @Test(dependsOnMethods = {"Test2"})
    public void Test3() {
        Assert.assertEquals(2 + 3, 5);
    }
}
