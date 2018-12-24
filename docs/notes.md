# Design notes.

I've chosen to have both a Game class and a Board class.

The `Board` represents the location of the pieces.

The `Game` tracks *who* is playing, and a small amount of UI information such as 
the currently selected piece.



```
pipenv run python setup.py build_ext --inplace   
```


Before I go any further I need some good baseline profiling results.

They shouldn't rely on, say, depth parameters for the bot.

A good test might simply be computing all the legal moves from a given board position. This covers most of what we need to do.

```
no speedups installed
Winner: blue, movecount: 66
0:00:05.863039
trevor@personal:~/code/corridors$ pipenv run python -m corridors.profile
speedups installed
Winner: blue, movecount: 66
0:00:00.200000
trevor@personal:~/code/corridors$ 
```

We run into a rather interesting, fundamental problem, with this algorithm, even
now I have it blisteringly fast.

 