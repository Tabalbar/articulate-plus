runnontiled:
        ./nontiled 1000

nontiled: nontiled.c
        gcc -0fast nontiled.c -o nontiled

runtiled:
        ./tiled 1000

untiled: tiled.c
        gcc -0fast tiled.c -o tiled