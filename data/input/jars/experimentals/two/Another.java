public class Another {
    public final double pi = 3.14;

	public enum Day {
    SUNDAY, MONDAY, TUESDAY, WEDNESDAY,
    THURSDAY, FRIDAY, SATURDAY
    }

    public enum Level {
        HIGH  (3),  //calls constructor with value 3
        MEDIUM(231),  //calls constructor with value 2
        LOW   (14)   //calls constructor with value 1
        ; // semicolon needed when fields / methods follow


        private final int levelCode;

        Level(int levelCode) {
            this.levelCode = levelCode;
        }

        public int getLevelCode() {
            return this.levelCode;
        }

    }

	public int test()
	{
	    System.out.println("test is okay - for Another class");
	    return 1;
	}
}