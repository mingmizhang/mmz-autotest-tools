package mingmi;

import org.testng.Assert;
import org.testng.annotations.Test;

import static org.mockito.Mockito.*;

/**
 * Created by zhangmingmi on 16/8/17.
 */
public class MockitoDemoTwo {
    @Test
    public void demo2(){
        Person mockPerson = mock(Person.class);
        doNothing().when(mockPerson).printname();
        doCallRealMethod().when(mockPerson).setAddress("jinyunlu");
        mockPerson.setAddress("jinyunlu");
        Assert.assertTrue(mockPerson.address.equals("jinyunlu"));
        doCallRealMethod().when(mockPerson).printaddress();
        mockPerson.printaddress();
        doCallRealMethod().when(mockPerson).printall();
        mockPerson.printall();

    }
}
