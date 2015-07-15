'''
    @summary: Permutation Generator function
    @input elements: list of unique elements
    
'''
'''   
 read about itertools!
import itertools
itertools.permutations([list_of_elements])

'''
def allPermutationsGenerator(elements):
    if len(elements) <=1:
        yield elements;
    else:
        for perm in allPermutationsGenerator(elements[1:]):
            for i in range(len(elements)): 
                yield perm[:i] + elements[0:1] + perm[i:]; #nb elements[0:1] works in both string and list contexts
'''
 temp = []
        for k in range(len(seq)):
            part = seq[:k] + seq[k+1:]
            #print k, part  # test
            for m in permutate(part):
                temp.append(seq[k:k+1] + m)
                #print m, seq[k:k+1], temp  # test
        return temp
'''
def numPermCalculator(elements):
    ValidPermutations = [];
    ValidPermutations.extend(list(allPermutationsGenerator(elements)));
    return len(ValidPermutations)

if __name__ == '__main__':
    import sys
    numValidPermutations = numPermCalculator(sys.argv[1]);
    print 'The length of the given string was: %d \n' % len(sys.argv[1]);
    print 'The number of unique permutations is: %d \n' % numValidPermutations;

    