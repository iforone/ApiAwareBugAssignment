public class MyProgram
{
    public final int value1 = 1;
    public int value2 = 2;


	public static void main(String[] args) {
		System.out.println("Hello World");

		Another a = new Another();
	    a.test();


        Another.Day day = Another.Day.SUNDAY;
        System.out.println(day);

		Another.Level level = Another.Level.MEDIUM;
        System.out.println(level.getLevelCode());
	}

    private void folderChecker() {
    }

    public String checker() {
        return "test";
    }
}