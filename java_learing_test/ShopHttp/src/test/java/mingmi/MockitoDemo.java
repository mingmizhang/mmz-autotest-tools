package mingmi;

import org.testng.annotations.Test;

import static org.mockito.Mockito.doCallRealMethod;
import static org.mockito.Mockito.mock;
import static org.mockito.Mockito.when;


/**
 * Created by zhangmingmi on 16/8/17.
 */
public class MockitoDemo {

    @Test
    public void demo(){
        System.out.println("begin");
        House mockHouse = mock(House.class);
        when(mockHouse.sell()).thenReturn("Mock Price");
        Person mockPerson = mock(Person.class);
        when(mockPerson.getHouse()).thenReturn(mockHouse);
//        mockPerson.setName("mingmi");
//        mockPerson.setAddress("Anhua Rd.");
        doCallRealMethod().when(mockPerson).sellHouse();
        mockPerson.sellHouse();
        System.out.println("end");

        when(mockPerson.getAddress()).thenThrow(new NullPointerException("null Pointer Exception"));
        try{
            mockPerson.getAddress();
        } catch (Exception e){
            e.printStackTrace();
        }

    }
}
