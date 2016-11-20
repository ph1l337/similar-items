# Similar Items

**Running the program**
`python -m similaritem.main [-k shingle-size] [-t threshold] [-sig signature-size] path`

    Where
        - path: is a path to a file or directory containing text documents
        - k   : is the size of the shingles. Defaults to 9
        - t   : is the threshold for documents signatures, 
                so documents will be considered similar. Defaults to .8
        - sig : document signature size. Defaults to 100
    
    
Note that the times reported don't include times for building signatures.
Several runs have shown us that for a small amount of documents the run 
time is `Signature < Jaccard < LSH`. With more documents this order changes to
`LSH < Signature < Jaccard`.

## Design Choices for Sub tasks

### Creation of Shingles
When creating the shingles of size k \t and \n characters are replaced 
with white-space. Multiple subsequent white-spaces are replaced by a single
one. Shingles are created line by line to reduce memory usage and allow 
shingling even very large documents. Left-over characters of one line are
added to the front of the subsequent line.

The shingles are then hashed to a domain of `2^31-1`. This is a prime number
as well as the biggest number that can be stored in a 32-bit signed integer.
Therefore we considered this number as suitable for the domain of our 
hashing function.

### Jaccard similarity of two shingle sets
The function calculating the jaccard similarity for all document pairs of
two sets first builds all possible pairs of documents between the two sets
(ignoring order) and then computes the jaccard similarity for each set.

### MinHash signatures
The function to create the minHash signatures for the documents randomly
generates `n` random hash functions with a domain of `2^31-1`. These
hashing functions serve to simulate the permutation of the characteristic
matrix. Therefore, the domain of our initial hashing function and these 
hashing functions are equal. From these functions the signature is created 
considering the minimum of the outputs of each of these hashing functions 
for the shingles of a document.

### Similarity of signatures 
Similarly to the jaccard similarity, all possible pairs between the documents
are formed. Then each position of the signatures is compared against the other
and checked if they are similar.

### Locality Sensitive Hashing
For calculating the number of rows and band given a threshold we use the 
method described in the book. First, the produce between the number of bands and rows in a band has to match the signature second. Second, the threshold can be relatively equal to the the inverse of the number of bands to the power of the inverse of the number of rows in a band, i.e. `(1/b)**(1/r)`. The value is tweaked, depending on whether we want high accuracy or high recall. For high recall, the threshold value is made slightly smaller than the factor, and for high precision the opposite.

## Implementation Notes

### Hashing

While one could use the `hash` function in python, there is adverse behaviour between python 2 and 3. In python2, the interpreter is initialised with a seed, so the output is consistent over several ones. In python3, the interpreter has a random seed on each run.

So, we resort to the `SHA256` function in the `hashlib` function. We extract the hash digest  a hexadecimal value, convert it to a base 10 integer, and use the first `2^31-1` bits.
This ensures a more consistent behaviour accross interpreters.

### Interpreters

Program tested using CPython interpreter, and PyPy. For high performance, PyPy is recommended as the interpreter of choice.

