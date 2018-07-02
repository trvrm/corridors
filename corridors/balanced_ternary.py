
def encode(i):
    assert isinstance(i,int)
    if i<0:
        return [-el for el in encode(-i)]
    
    def remainders(i):
        while i:
            i,mod=divmod(i,3)
            yield mod
        yield 0
    r = list(remainders(i))
    i=0
    while i < len(r):
        if r[i]>1:
            r[i]  -=3
            r[i+1]+=1
        i+=1
    if r[-1]==0:r.pop()
    return list(reversed(r))

def decode(l):
    l = list(reversed(l))
    out=0
    for i in range(len(l)):
        out+=(int(l[i]))*(3**i)
    return out