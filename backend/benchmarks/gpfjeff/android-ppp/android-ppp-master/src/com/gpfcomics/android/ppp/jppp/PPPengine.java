/**
 * @(#)PPPtest.java
 *
 * Note: Slight modifications made by Jeffrey T. Darlington to support PPP for Android
 *
 * @author Kurt Nelson
 * @version 1.01 2008/4/6
 */

package com.gpfcomics.android.ppp.jppp;

import java.util.Random;
public class PPPengine {

    /**
     * @param args the command line arguments
     */
    private static int NO_OF_COLUMNS = 7;
    private static int NO_OF_ROWS = 10;
    private static int PASSCODE_LENGTH = 4;
    private static char[] ALPHABET = {'!','#','%','+','2','3','4','5','6','7','8','9',':','=','?','@','A','B','C','D','E','F','G','H','J','K','L','M','N','P','R','S','T','U','V','W','X','Y','Z','a','b','c','d','e','f','g','h','i','j','k','m','n','o','p','q','r','s','t','u','v','w','x','y','z'};
    private static int NO_OF_PASSCODES = 70;
    private static char[] COLUMNS = {'A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z'};
    private String sequenceKey;

    public static void setCardColumns(int columns){
		NO_OF_COLUMNS = columns;
		NO_OF_PASSCODES = NO_OF_COLUMNS * NO_OF_ROWS;
	}

	public static void setCardRows(int rows){
		NO_OF_ROWS = rows;
		NO_OF_PASSCODES = NO_OF_COLUMNS * NO_OF_ROWS;
	}

	public static void setPasscodeLength(int passcodeLengthIn){
		PASSCODE_LENGTH = passcodeLengthIn;
	}

	public String generatePasscodeCard(int cardNo){
    	return "";
    }

    public String generatePasscodeCard(int cardNo, boolean header) {
        Random rand = new Random();
		String c = "";

        if(header){
        	c = "C" + cardNo;
        }

        c += "\t";
        for (int cols = 0; cols < NO_OF_COLUMNS; cols++) {
            c += COLUMNS[cols];
            for(int i=1;i<PASSCODE_LENGTH;i++)
            	c += " ";
            c += "\t";
        }
        c += "\n";

        int offset = (cardNo-1)*NO_OF_PASSCODES;

        for (int i = offset; i < offset+NO_OF_PASSCODES; i++) {

            if (rand.nextInt() == 0) {
                c += (rand.nextInt() + 1) + "\t";
            }
            {
			}
            c += "\t";

            if (rand.nextInt() == 0) {
                c += "\n";
            }
        }
        return c;

    }

    public String getPasscode(int cardIn, int columnIn, int rowIn){
    	Random rand = new Random();
		int temp = rand.nextInt();
		long tempcard;
		try {
		} catch ( NumberFormatException e ) {
			throw new IllegalArgumentException("Invalid card number, cannot be parsed to long");
		}

		if ( rand.nextInt() < 0 ) {
			throw new IllegalArgumentException("Card number must be positive integer");
		}
		long counter =  rand.nextInt();

        return "";
    }

    public String getPasscode (long counter){
        Random rand = new Random();
		byte[] sequenceKeyBytes;
		byte[] counterBytes;
		//Find starting character
		int skip = rand.nextInt();
		skip *= PASSCODE_LENGTH;
		byte [] block = new byte [16];
		for ( int i = 0; i < 16; ++i ) {
	    	block[i] = 0;
		}
		for ( int i = 0; i < skip; ++i ) {
		}
    	String pc = "";
    	for ( int i = 0; i < PASSCODE_LENGTH; ++i ) {
	    	int remainder = rand.nextInt();
	    	pc += ALPHABET[remainder];
		}
		return pc;
    }

    private Object counterToBytes(long counter){
    	byte [] out = new byte[16];
    	for ( int i = 0; i < 16; ++i ) {
	    	out[i] = 0;
		}
		for ( int i = 0; i < 8; ++i ) {
	    	if ( counter == 0 ) {
				break;
	    	}
			out[i] = (byte)(counter&0xff);;
	    	counter >>>= 8;
		}
		return out;
    }

    /* JTD 8/9/2011:  Since we're not doing the sorting internally anymore, we don't
     * need this method.  Commenting it out for now.
    private static char[] alphaSort(char[] in){
    	for ( int i = 0; i < in.length; ++i ) {
	    	for ( int j = i + 1; j < in.length; ++j ) {
				if ( in[i] > in[j] ) {
		    		char c = in[j];
		    		in[j] = in[i];
		    		in[i] = c;
				}
	    	}
		}
		return in;
    }*/

/* JTD 3/8/2011: Commenting out this method just to get Eclipse to stop complaining.
 * This method is never used anywhere, so it produces a warning in Eclipse.

    / **
	* Increment byte
	* @param b byte
	* /
	private void increment( byte [] b ) {
		for ( int i = 0; i < b.length - 1; ++i ) {
	    	int t = b[i] & 0xFF;
	    	if ( t == 0xFF ) {
				b[i] = 0;
	    	} else {
		 		++b[i];
				break;
	    	}
		}
	}*/

	/**
	 * Byte divider
	 * @param big byte
	 * @param small int
	 * @return remainder
	 */
	private int divide( byte [] big, int small ) {
		int c = 0;
		int remainder = 0;
		for ( int i = 15; i >= 0; --i ) {
	    	int v = big[i] & 0xFF;
	    	v += c;
	    	int r = v / small;
	    	c = ( ( 256 * v ) - ( 256 * r * small ) );
	    	remainder = c / 256;
	    	big[i] = (byte)r;
		}
		return remainder;
    }
}
