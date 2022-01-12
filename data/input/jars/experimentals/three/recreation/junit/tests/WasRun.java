package junit.tests;

/**
 * A helper test case for testing whether the testing method
 * is run.
 */
public class WasRun {
    public boolean fWasRun = false;

    protected void runTest() {
        fWasRun = true;
    }
}
