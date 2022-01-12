/******************************************************************************

                            This is a test Java file
                after making the file make a folder called build
                then run: javac -d ./build *.java
                then go to the directory
                then run: jar cvf YourJar.jar *
                -----
                jar -tf YourJar.jar

*******************************************************************************/

public class Main
{
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

	public static void main(String[] args) {
		System.out.println("Hello World");
		Day day = Day.SUNDAY;
		System.out.println(day);
		Level level = Level.MEDIUM;
        System.out.println(level.getLevelCode());
	}

	public int test()
	{
	    return 1;
	}

}