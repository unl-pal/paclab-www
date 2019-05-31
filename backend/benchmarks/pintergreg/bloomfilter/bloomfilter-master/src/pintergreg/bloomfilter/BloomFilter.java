/*
 * Copyright 2015 Gergő Pintér.
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *      http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */
package pintergreg.bloomfilter;

import java.io.Serializable;
import java.util.BitSet;

/**
 * Basic Bloom Filter implementation
 *
 * @author Gergő Pintér
 */
public class BloomFilter{
    
    private static final long serialVersionUID = 1L;

    protected int m;
    protected int k;

    protected BitSet bitSet;

    /**
     * Create Bloom Filter based on bitvector size and the numbers of hash
     * functions
     *
     * @param m - size of the bitvector
     * @param k - number of the hash functions
     *
     * It is not recommended to use this constructor, unless you really know
     * what you do
     */
    public BloomFilter(int m, int k) {
        BitSet bitSet;
		this.m = m;
        this.k = k;

        bitSet = new BitSet(m);
    }

    /**
     * Add item to Bloom Filter
     *
     * @param key - an item to be added to the Bloom Filter
     */
    public void add(byte[] key) {
    }

    /**
     * Search item in the Bloom Filter
     *
     * @param key - an item to be searched in the Bloom Filter
     * @return True if Bloom Filter contains the given item, False otherwise
     */
    public boolean include(byte[] key) {
        boolean result = true;

        return result;
    }

}
