package com.dp.mingmi.ShopHttp.BaseTest;

//import com.dp.mingmi.ShopHttp.ComputeHashcode;
//import org.mockito.Mockito;
//import org.powermock.api.mockito.PowerMockito;
//import org.powermock.core.classloader.annotations.PrepareForTest;
//import org.testng.Assert;
//import org.testng.annotations.Test;
//
//import static org.mockito.Mockito.when;

import com.dp.mingmi.ShopHttp.ComputeHashcode;
import org.mockito.Mockito;
import org.powermock.api.mockito.PowerMockito;
import org.powermock.core.classloader.annotations.PrepareForTest;
import org.powermock.modules.testng.PowerMockTestCase;
import org.testng.Assert;
import org.testng.annotations.Test;

//import org.junit.runner.RunWith;

/**
 * Created by zhangmingmi on 16/8/17.
 */
@PrepareForTest(ComputeHashcode.class)
public class MockitoTest extends PowerMockTestCase{
    @Test
    public void testStatichashcode() {
        int sta = 5;
        PowerMockito.mockStatic(ComputeHashcode.class);
        Mockito.when(ComputeHashcode.hashCodeStatic("abc")).thenReturn(sta);
        Assert.assertEquals(ComputeHashcode.hashCodeStatic("abc"), sta);
    }

    @Test
    public void testhashcode() {
        /*
            验证mockito的确是起作用了
         */

        int mocked = 3;
        ComputeHashcode hashobj = Mockito.mock(ComputeHashcode.class);
        Mockito.when(hashobj.hashCode("abc")).thenReturn(mocked);
        Assert.assertEquals(hashobj.hashCode("abc"), mocked);
    }

    @Test
    public void testcompute() {
        ComputeHashcode hashobj = Mockito.mock(ComputeHashcode.class);
        Mockito.doNothing().when(hashobj).compute();
    }







}
